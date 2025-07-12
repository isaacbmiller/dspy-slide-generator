import dspy
from schemas import *
from signatures import *
import mlflow
import json
import rich
from utils import lm_with_temp
from react_screenshot import react_to_screenshot
import os

# This needs to return a screenshot and thats it -- no code for now

# SlideOverview -> DetailedSlideInputs
# is_satisfactory = false
# current_code = None
# feedback = None
# while not is_satisfactory:
#     DetailedSlideInputs, current_code, screenshot: dspy.Image, feedback -> revised_code
#     is_satisfactory = slide_judge(slide outline: Slide, screenshot: DSPy.Image -> is_satisfactory: bool, critique: str)
class GenerateAndIterateSlides(dspy.Module):
    def __init__(self, max_iter: int = 1, output_dir: str = "outputs"):
        super().__init__()
        self.detailed_slide_generator = dspy.ChainOfThought(DetailedSlideGenerator)
        self.slide_code_generator = dspy.ChainOfThought(SlideCodeGenerator)
        self.max_iter = max_iter
        self.output_dir = output_dir

    def forward(self, narrative_points, slide_overviews, current_slide_overview, presentation_inputs, temperature=0.0):
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
            
        iteration = 0
        screenshot = None
        feedback = None
        current_code = None
        while iteration < self.max_iter:
            revised_code = self.slide_code_generator(
                detailed_slide_inputs=detailed_slide_inputs,
                current_code=current_code,
                screenshot=screenshot,
                feedback=feedback
            ).revised_react_code
            screenshot = react_to_screenshot(revised_code)

            # temporarily save the screenshot
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            if not os.path.exists(f"{self.output_dir}/{temperature}"):
                os.makedirs(f"{self.output_dir}/{temperature}")
            screenshot.save(f"{self.output_dir}/{temperature}/{current_slide_number}_{detailed_slide_inputs.title.replace(' ', '_').replace(':', '_').lower()}_{iteration}.png")

            iteration += 1
            if iteration > self.max_iter:
                raise Exception("Max iterations reached")
        # Optionally, return the last screenshot or any other result as needed
        return screenshot
class SlideGenerator(dspy.Module):
    def __init__(self):
        self.narrative_generator = dspy.ChainOfThought(NarrativeGenerator)
        self.slide_generator = dspy.ChainOfThought(SlideOverviewGenerator)
        self.slide_code_generator = GenerateAndIterateSlides()
        self.slide_judge = dspy.ChainOfThought(SlideJudge)
        self.pairwise_judge = dspy.ChainOfThought(PairwiseJudge)


    def forward(self, presentation_inputs: PresentationInputs) -> list[str]:
        # PresentationInputs -> NarrativePoints
        narrative_points = self.narrative_generator(presentation_inputs=presentation_inputs).narrative_points

        # slides = NarrativePoints -> list[SlideOverview]
        slides: list[SlideOverview] = self.slide_generator(narrative_points=narrative_points, presentation_inputs=presentation_inputs).slides
        completed_slides = []
        # ignoring variants/tournament at first
        for slide in slides:
            # variants = []
            possible_temps = [0.0]
            
            self.slide_code_generator.batch(
                dspy.Example(
                    narrative_points=narrative_points,
                    slide_overviews=slides,
                    current_slide_overview=slide,
                    presentation_inputs=presentation_inputs,
                    temperature=temp
                ).with_inputs("narrative_points", "slide_overviews", "current_slide_overview", "presentation_inputs", "temperature")
                for temp in possible_temps
            )
            # tournament logic:
                # will make sure to give myself a nice tournament number of variants per slide -- 8 or 16
                # remaining_variants = variants
                # while len(remaining_variants) > 0:
                    # remaining_variants = tournament_round(remaining_variants)

                    # tournament_round = lambda variants: [pairwise_judge(a, b) for a, b in zip(variants[::2], variants[1::2])]
                    # pairwise_judge = ChainOfThought(screenshot_A: dspy.Image, screenshot_B: dspy.Image, preference: Literal["A", "B"])
                # completed_slides.append(remaining_variants[0])

        # compile everything as a single slide deck -- ill just collect the screenshots for now -- this is a great opporunity to vibe code a data viewer/labeler if I want going to do optimizer

# This should be generated
with open("blog.md", "r") as f:
    blog_markdown = f.read()

with open("why_i_bet_on_dspy.md", "r") as f:
    why_i_bet_on_dspy = f.read()

with open("dspy_brand_structure.json", "r") as f:
    brand_guidelines = json.load(f)
    brand_guidelines = BrandGuidelines(**brand_guidelines)

why_i_bet_on_dspy_data = {
    "user_goal": "Generate a slide deck that informs the audience of the core function of dspy as a way to solve problems with compound LLM systems.",
    "user_intent": "Persuade the audience in order to understand the value of DSPy as a forward thinking framework",
    "relevant_data": why_i_bet_on_dspy,
    "brand_guidelines": brand_guidelines
}

blog_data = {
    "user_goal": "Show the audience a cool implementation of a compound system built using dspy",
    "user_intent": "Impress the audience with how easy it is to develop such a complex system",
    "relevant_data": blog_markdown,
    "brand_guidelines": brand_guidelines
}


mock_presentation_inputs = [PresentationInputs(
    **example
) for example in [why_i_bet_on_dspy_data, blog_data]]


def main():
    slide_generator = SlideGenerator()

    # print(mock_presentation_inputs)

    rich.print(slide_generator(mock_presentation_inputs[1]))



if __name__ == "__main__":


    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("slide_generator")
    mlflow.dspy.autolog()

    dspy.configure(lm=dspy.LM("gpt-4.1"))
    main()