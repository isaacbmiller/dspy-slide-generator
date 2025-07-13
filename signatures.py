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