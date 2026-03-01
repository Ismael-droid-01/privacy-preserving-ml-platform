import base64
import io
import pandas as pd
import os

def load_csv_from_base64(dataset_base64: str) -> pd.DataFrame:
    decoded = base64.b64decode(dataset_base64)
    buffer = io.StringIO(decoded.decode("utf-8"))
    return pd.read_csv(buffer)
