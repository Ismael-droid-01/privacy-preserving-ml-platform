import base64
import io
import pandas as pd
import os

def load_csv_from_base64(dataset_base64: str) -> pd.DataFrame:
    decoded = base64.b64decode(dataset_base64)
    buffer = io.StringIO(decoded.decode("utf-8"))
    return pd.read_csv(buffer)

def get_dataset_head(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path, nrows=10)

def get_dataset_metadata(file_path: str):
    df_sample = pd.read_csv(file_path, nrows=100)

    with open(file_path, 'r') as f:
        total_rows = sum(1 for line in f) - 1
    
    return {
        "columns": df_sample.columns.tolist(),
        "column_types": {col: str(dtype) for col, dtype in df_sample.dtypes.items()},
        "total_rows": total_rows,
        "total_columns": len(df_sample.columns),
        "null_counts": df_sample.isnull().sum().to_dict()
    }