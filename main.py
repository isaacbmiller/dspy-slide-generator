import dspy
from schemas import *
from signatures import *
import mlflow
import json
import rich
from utils import lm_with_temp
from react_screenshot import react_to_screenshot
import os
import datetime
from slide_generator import GenerateAndIterateSlides
from slide_tournament import SlideTournament
class SlideGenerator(dspy.Module):
    def __init__(self, output_dir: str = "outputs"):
        self.narrative_generator = dspy.ChainOfThought(NarrativeGenerator)
        self.slide_generator = dspy.ChainOfThought(SlideOverviewGenerator)
        self.output_dir = output_dir
        self.slide_code_generator = GenerateAndIterateSlides(max_iter=3, output_dir=output_dir)
        self.slide_tournament = SlideTournament()


    def forward(self, presentation_inputs: PresentationInputs) -> list[str]:
        # PresentationInputs -> NarrativePoints
        narrative_points = self.narrative_generator(presentation_inputs=presentation_inputs).narrative_points

        # slides = NarrativePoints -> list[SlideOverview]
        slides: list[SlideOverview] = self.slide_generator(narrative_points=narrative_points, presentation_inputs=presentation_inputs).slides
        completed_slides = []
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

        # compile everything as a single slide deck -- ill just collect the screenshots for now -- this is a great opporunity to vibe code a data viewer/labeler if I want going to do optimizer

# This should be generated
with open("blog_1.md", "r") as f:
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
    output_dir = "outputs/{}".format(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    os.makedirs(output_dir, exist_ok=True)
    slide_generator = SlideGenerator(output_dir=output_dir)

    # print(mock_presentation_inputs)

    slide_generator(mock_presentation_inputs[0])



if __name__ == "__main__":


    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("slide_generator")
    mlflow.dspy.autolog()

    dspy.configure(lm=dspy.LM("gpt-4.1"))
    main()