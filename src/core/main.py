import dspy
from src.schemas.schemas import PresentationInputs, SlideOverview, BrandGuidelines
from src.schemas.signatures import NarrativeGenerator, SlideOverviewGenerator
import mlflow
import json
import rich
from src.utils.utils import lm_with_temp
from src.utils.react_screenshot import react_to_screenshot
import os
import datetime
from src.modules.slide_generator import GenerateAndIterateSlides
from src.modules.slide_tournament import SlideTournament


# This should be generated
with open("docs/blogs/blog_1.md", "r") as f:
    blog_markdown = f.read()

with open("docs/research/why_i_bet_on_dspy.md", "r") as f:
    why_i_bet_on_dspy = f.read()

with open("data/brand/dspy_brand_structure.json", "r") as f:
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