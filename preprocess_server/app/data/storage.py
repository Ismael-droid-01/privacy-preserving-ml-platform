import uuid
import os
import pandas as pd
from app.core.config import settings

def get_dataset_by_id(dataset_id: str) -> pd.DataFrame:
    file_path = os.path.join(settings.RAW_DATA_PATH, f"{dataset_id}.csv")
    
    if not file_path.exists():
        raise FileNotFoundError
    return pd.read_csv(file_path)