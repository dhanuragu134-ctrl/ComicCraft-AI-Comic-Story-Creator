from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    story_prompt: str = Field(..., min_length=1)
    character_name: str = Field(..., min_length=1)
    setting: str = Field(..., min_length=1)
    tone: str = Field(..., min_length=1)
    art_style: str = Field(..., min_length=1)