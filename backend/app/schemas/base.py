from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """
    Base Pydantic model for all schemas in VaaniAi.
    Configured to allow population from attributes (ORM mode compatible).
    """
    model_config = ConfigDict(from_attributes=True)