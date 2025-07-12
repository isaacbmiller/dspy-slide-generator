from pydantic import BaseModel

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


    
    
"""

"""