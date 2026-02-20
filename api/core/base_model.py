from pydantic import BaseModel, ConfigDict


class RavenBaseModel(BaseModel):
    """
    Base model for all Raven models with Pydantic 2.x compatibility settings.
    
    Configuration:
    - coerce_numbers_to_str: Automatically converts numeric database IDs to strings
    - str_strip_whitespace: Strips whitespace from string fields
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        coerce_numbers_to_str=True
    )
