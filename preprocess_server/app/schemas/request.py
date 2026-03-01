from pydantic import BaseModel, Field
from typing import Optional

class DatasetValidationRequest(BaseModel):
    dataset_base64: str = Field(
        ..., description="Dataset CSV codificado en base64"
    )

    target: Optional[str] = Field(
        None, description="Nombre de la columna objetivo"
    )

class DatasetSplitRequest(BaseModel):
    test_size: float = Field(0.2, ge=0.1, le=0.5, description="Proporción del dataset para pruebas (0.1 a 0.5)")
    shuffle: bool = True
    random_state: int = 42