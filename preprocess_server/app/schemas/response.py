from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class UploadResponse(BaseModel):
    dataset_id: str
    message: str

class DatasetPreviewMetaDataResponse(BaseModel):
    columns: List[str]
    column_types: Dict[str, str]
    total_rows: int
    total_columns: int
    null_counts: Dict[str, int]

class DatasetPreviewResponse(BaseModel):
    dataset_id: str
    metadata: DatasetPreviewMetaDataResponse
    data: List[Dict[str, Any]]
    message: str
