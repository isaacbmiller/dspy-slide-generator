from pydantic import BaseModel, field_validator, PlainValidator
from typing import Optional, Any, Annotated
from PIL import Image
import dspy
class BrandGuidelines(BaseModel):
    brand: dict
    tone: dict
    voice: dict
    

class PresentationInputs(BaseModel):
    user_goal: str
    user_intent: str
    relevant_data: str
    brand_guidelines: BrandGuidelines

class NarrativePoint(BaseModel):
    name: str
    bullets: list[str]

class SlideOverview(BaseModel):
    name: str
    description: str

class DetailedSlideInputs(BaseModel):
    title: str
    data: list[str]
    visual: list[str]
    layout: list[str]
    tone: list[str]

class Slide(dspy.BaseType):

    title: str
    code: Optional[str] = None
    filename: Optional[str] = None
    screenshot: Optional[Annotated[Image.Image, PlainValidator(lambda x: x)]] = None

    def format(self):
        return_string = ""
        if self.title:
            return_string += f"Title: {self.title}\n"
        return_string += f"Code: {self.code}\n"

        if self.screenshot is not None:
            return_string += "Screenshot:"
            return [{"type": "text", "text": return_string}].extend(dspy.Image.from_PIL(self.screenshot).format())
        else:
            return_string += "Screenshot: None"
            return return_string
    
    def dspy_image(self):
        if self.screenshot is not None:
            return dspy.Image.from_PIL(self.screenshot)
        return None
    
    def save(self, filename: str):
        if self.screenshot is not None:
            self.screenshot.save(filename)
