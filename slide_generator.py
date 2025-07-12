import dspy
from schemas import *
from signatures import *
import mlflow
import json
import rich
from utils import lm_with_temp
from react_screenshot import react_to_screenshot

def generate_and_iterate_slides(detailed_slide_inputs: DetailedSlideInputs, slide_code_generator: dspy.Module, max_iter: int):
    iteration = 0
    screenshot = None
    feedback = None
    current_code = None
    while iteration < max_iter:
        screenshot = react_to_screenshot(detailed_slide_inputs.react_code)
        iteration += 1
        if iteration > max_iter:
            raise Exception("Max iterations reached")
    pass
class SlideGenerator(dspy.Module):
    def __init__(self):
        self.narrative_generator = dspy.ChainOfThought(NarrativeGenerator)
        self.slide_generator = dspy.ChainOfThought(SlideOverviewGenerator)
        self.detailed_slide_generator = dspy.ChainOfThought(DetailedSlideGenerator)
        self.slide_code_generator = dspy.ChainOfThought(SlideCodeGenerator)
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
            # will want to make this parallel
            for temp in possible_temps:
                with dspy.context(lm=lm_with_temp(temp)):
                    
                    detailed_slide_inputs = self.detailed_slide_generator(narrative_points=narrative_points, slide_overviews=slides, current_slide_overview=slide, presentation_inputs=presentation_inputs).detailed_slide_inputs


# detailed_slide_inputs: DetailedSlideInputs = dspy.InputField()
    # current_code: Optional[str] = dspy.InputField()
    # screenshot: Optional[dspy.Image] = dspy.InputField()
    # feedback: Optional[str] = dspy.InputField()
    # revised_react_code: str = dspy.OutputField()
                    

                # SlideOverview -> DetailedSlideInputs
                # is_satisfactory = false
                # current_code = None
                # feedback = None
                # while not is_satisfactory:
                #     DetailedSlideInputs, current_code, screenshot: dspy.Image, feedback -> revised_code
                #     is_satisfactory = slide_judge(slide outline: Slide, screenshot: DSPy.Image -> is_satisfactory: bool, critique: str)
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
with open("why_i_bet_on_dspy.md", "r") as f:
    blog_markdown = f.read()

with open("dspy_brand_structure.json", "r") as f:
    brand_guidelines = json.load(f)
    brand_guidelines = BrandGuidelines(**brand_guidelines)

mock_presentation_inputs = PresentationInputs(
    user_goal="Generate a slide deck that informs the audience of the core function of dspy as a way to solve problems with compound LLM systems.",
    user_intent="Persuade the audience in order to understand the value of DSPy as a forward thinking framework",
    relevant_data=blog_markdown, # load from why_i_bet_on_dspy.md
    brand_guidelines=brand_guidelines # Load from dspy_brand_structure.json
)

def main():
    slide_generator = SlideGenerator()

    # print(mock_presentation_inputs)

    rich.print(slide_generator(mock_presentation_inputs))



if __name__ == "__main__":


    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("slide_generator")
    mlflow.dspy.autolog()

    dspy.configure(lm=dspy.LM("gpt-4.1"))
    main()