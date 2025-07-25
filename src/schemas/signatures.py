from src.schemas.schemas import DetailedSlideInputs, PresentationInputs, Slide, SlideOverview, NarrativePoint
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


class DetailedSlideGenerator(dspy.Signature):
    """Generate detailed slide inputs from the current slide overview"""
    presentation_inputs: PresentationInputs = dspy.InputField()
    narrative_points: list[NarrativePoint] = dspy.InputField()
    slide_overviews: list[SlideOverview] = dspy.InputField()
    current_slide_overview: SlideOverview = dspy.InputField()
    detailed_slide_inputs: DetailedSlideInputs = dspy.OutputField()