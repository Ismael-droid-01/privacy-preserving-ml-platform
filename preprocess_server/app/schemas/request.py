from pydantic import BaseModel, Field
from typing import Optional

class DatasetValidationRequest(BaseModel):
    dataset_base64: str = Field(
        ..., description="Dataset CSV codificado en base64"
    )

    target: Optional[str] = Field(
        None, description="Nombre de la columna objetivo"
    )