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

####################################################################
class DatasetSummaryResponse(BaseModel):
    dataset_id: str
    n_samples: int
    n_features: int
    numeric_features: List[str]
    non_numeric_features: List[str]
    missing_values: Dict[str, int]
    target: Optional[str]
    target_valid: bool
    ckks_compatible: bool
    preview: List[Dict[str, Any]]
    
class PreprocessResponse(BaseModel):
    summary: Optional[DatasetSummaryResponse] = None
    isValid: bool
    message: str