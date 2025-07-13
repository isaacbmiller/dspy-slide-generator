import logging
import dspy
import os
from react_screenshot import react_to_screenshot
from schemas import DetailedSlideInputs, PresentationInputs, Slide, SlideOverview, NarrativePoint
from typing import Optional
from utils import lm_with_temp, to_PIL_image, clean_slide_name


logger = logging.getLogger(__name__) # __name__ gives a unique name based on the module
logger.setLevel(logging.DEBUG)
class DetailedSlideGenerator(dspy.Signature):
    """Generate detailed slide inputs from the current slide overview"""
    presentation_inputs: PresentationInputs = dspy.InputField()
    narrative_points: list[NarrativePoint] = dspy.InputField()
    slide_overviews: list[SlideOverview] = dspy.InputField()
    current_slide_overview: SlideOverview = dspy.InputField()
    detailed_slide_inputs: DetailedSlideInputs = dspy.OutputField()


class SlideCodeGenerator(dspy.Signature):
    """Generate React code for slides based on detailed inputs. 
    The window is 1920x1080.
    Start the code with exactly `function App() {`"""
    detailed_slide_inputs: DetailedSlideInputs = dspy.InputField()
    current_slide: Slide = dspy.InputField()
    feedback: Optional[str] = dspy.InputField()
    revised_react_code: str = dspy.OutputField()


class SlideJudge(dspy.Signature):
    """Judge if a slide is a high quality slide matching the overview based on outline and screenshot
    Slides should be visibly appealing, well formatted, and easy to understand.
    You should be a harsh judge with high quality standards, ensuring that no misaligned text or figures are present.
    The entire canvas should be used up.
    """
    slide_overview: SlideOverview = dspy.InputField()
    slide: Slide = dspy.InputField()
    is_satisfactory: bool = dspy.OutputField()
    feedback: str = dspy.OutputField()

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
