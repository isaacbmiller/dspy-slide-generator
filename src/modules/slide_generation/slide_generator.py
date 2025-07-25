import logging
import dspy
import os
from src.utils.react_screenshot import react_to_screenshot
from src.schemas.schemas import PresentationInputs, Slide, SlideOverview
from src.schemas.signatures import DetailedSlideGenerator, SlideCodeGenerator, SlideJudge, NarrativeGenerator, SlideOverviewGenerator
from src.modules.slide_tournament import SlideTournament
from src.utils.utils import lm_with_temp, clean_slide_name
import rich

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class GenerateAndIterateSlides(dspy.Module):
    def __init__(self, max_iter: int = 1, output_dir: str = "outputs"):
        super().__init__()
        self.detailed_slide_generator = dspy.ChainOfThought(DetailedSlideGenerator)
        self.slide_code_generator = dspy.ChainOfThought(SlideCodeGenerator)
        self.slide_judge = dspy.ChainOfThought(SlideJudge)
        self.max_iter = max_iter
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def forward(self, narrative_points, slide_overviews, current_slide_overview, presentation_inputs, temperature=0.0) -> Slide:
        if not os.path.exists(f"{self.output_dir}/{temperature}"):
            os.makedirs(f"{self.output_dir}/{temperature}")

        with dspy.context(lm=lm_with_temp(temperature)):
            detailed_slide_inputs = self.detailed_slide_generator(
                narrative_points=narrative_points, 
                slide_overviews=slide_overviews, 
                current_slide_overview=current_slide_overview, 
                presentation_inputs=presentation_inputs
            ).detailed_slide_inputs

        # Find the first matching member of slide_overviews that matches current_slide_overview
        current_slide_number, current_slide_overview = next(
            ((i, slide) for i, slide in enumerate(slide_overviews) if slide == current_slide_overview),
            (None, None)
        )
        slide_name = clean_slide_name(detailed_slide_inputs.title)
            
        iteration = 0
        slide = Slide(title=detailed_slide_inputs.title)
        feedback = None
        while iteration < self.max_iter:
            current_code = self.slide_code_generator(
                detailed_slide_inputs=detailed_slide_inputs,
                current_slide=slide,
                feedback=feedback
            ).revised_react_code
            slide.screenshot = react_to_screenshot(current_code)
            slide.save(f"{self.output_dir}/{temperature}/{iteration}_{slide_name}.png")

            judgement = self.slide_judge(
                slide_overview=current_slide_overview,
                slide=slide
            )
            
            if judgement.is_satisfactory:
                break
            else:
                feedback = judgement.feedback
            
            iteration += 1
            if iteration > self.max_iter:
                break
        # Optionally, return the last screenshot or any other result as needed
        os.makedirs(f"{self.output_dir}/slide_{current_slide_number}", exist_ok=True)
        slide.save(f"{self.output_dir}/slide_{current_slide_number}/{temperature}_{iteration}_{slide_name}.png")
        slide.filename = f"{self.output_dir}/slide_{current_slide_number}/{temperature}_{iteration}_{slide_name}.png"

        return slide


class SlideGenerator(dspy.Module):
    def __init__(self, output_dir: str = "outputs", max_iter: int = 3):
        self.narrative_generator = dspy.ChainOfThought(NarrativeGenerator)
        self.slide_generator = dspy.ChainOfThought(SlideOverviewGenerator)
        self.output_dir = output_dir
        self.slide_code_generator = GenerateAndIterateSlides(max_iter=max_iter, output_dir=output_dir)
        self.slide_tournament = SlideTournament()


    def forward(self, presentation_inputs: PresentationInputs) -> list[str]:
        # PresentationInputs -> NarrativePoints
        narrative_points = self.narrative_generator(presentation_inputs=presentation_inputs).narrative_points

        # slides = NarrativePoints -> list[SlideOverview]
        slides: list[SlideOverview] = self.slide_generator(narrative_points=narrative_points, presentation_inputs=presentation_inputs).slides
        # completed_slides = []
        # ignoring variants/tournament at first
        for slide in slides[:1]:
            # variants = []
            possible_temps = [0.0, 0.25, 0.5, 0.75]
            
            slide_variants = self.slide_code_generator.batch(
                [dspy.Example(
                    narrative_points=narrative_points,
                    slide_overviews=slides,
                    current_slide_overview=slide,
                    presentation_inputs=presentation_inputs,
                    temperature=temp
                ).with_inputs("narrative_points", "slide_overviews", "current_slide_overview", "presentation_inputs", "temperature")
                for temp in possible_temps],
                num_threads=10,
                max_errors=0
            )
            winning_slide = self.slide_tournament(slides=slide_variants)
            rich.print(winning_slide)

        # TODO: compile everything as a single slide deck -- ill just collect the screenshots for now -- this is a great opporunity to vibe code a data viewer/labeler if I want going to do optimizer