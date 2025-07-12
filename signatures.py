from schemas import *
import dspy
from typing import Optional, Literal


class NarrativeGenerator(dspy.Signature):
    """Generate a list of 3-5 narrative points"""
    presentation_inputs: PresentationInputs = dspy.InputField()
    narrative_points: list[NarrativePoint] = dspy.OutputField()


class SlideOverviewGenerator(dspy.Signature):
    """Generate 5-10 slide overviews from narrative points"""
    presentation_inputs: PresentationInputs = dspy.InputField()
    narrative_points: list[NarrativePoint] = dspy.InputField()
    slides: list[SlideOverview] = dspy.OutputField()


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
    current_code: Optional[str] = dspy.InputField()
    screenshot: Optional[dspy.Image] = dspy.InputField()
    feedback: Optional[str] = dspy.InputField()
    revised_react_code: str = dspy.OutputField()


class SlideJudge(dspy.Signature):
    """Judge if a slide is satisfactory based on outline and screenshot"""
    slide_overview: SlideOverview = dspy.InputField()
    screenshot: dspy.Image = dspy.InputField()
    is_satisfactory: bool = dspy.OutputField()
    critique: str = dspy.OutputField()


class PairwiseJudge(dspy.Signature):
    """Compare two slides and provide preference"""
    screenshot_A: dspy.Image = dspy.InputField()
    screenshot_B: dspy.Image = dspy.InputField()
    preference: Literal['A', 'B'] = dspy.OutputField()