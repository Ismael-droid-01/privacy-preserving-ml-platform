import uuid
import os
import pandas as pd
from app.core.config import settings

def save_temp_dataset(df: pd.DataFrame) -> str:
    dataset_id = str(uuid.uuid4())
    filename = f"{dataset_id}.csv"
    file_path = os.path.join(settings.RAW_DATA_PATH, filename)

    df.to_csv(file_path, index=False)
    return dataset_id

def get_dataset_by_id(dataset_id: str) -> pd.DataFrame:
    file_path = os.path.join(settings.RAW_DATA_PATH, f"{dataset_id}.csv")
    
    if not file_path.exists():
        raise FileNotFoundError
    return pd.read_csv(file_path)