import pandas as pd
import numpy as np
from typing import Optional

def summarize_dataset(df: pd.DataFrame, target: Optional[str] = None) -> dict:
    numeric_features = df.select_dtypes(include=["number"]).columns.tolist()
    non_numeric_features = df.select_dtypes(exclude=["number"]).columns.tolist()

    missing_values = df.isna().sum().to_dict()
    
    target_valid = False
    if target is not None and target in df.columns:
        target_valid = True
    
    # El dataset ya esta listo para cifrar?
    ckks_compatible = len(non_numeric_features) == 0

    # Obtener las primeras 5 filas
    preview = df.head(5).replace({np.nan: None}).to_dict(orient="records")

    return {
        "n_samples": df.shape[0],
        "n_features": df.shape[1],
        "numeric_features": numeric_features,
        "non_numeric_features": non_numeric_features,
        "missing_values": missing_values,
        "target": target,
        "target_valid": target_valid,
        "ckks_compatible": ckks_compatible,
        "preview": preview
    }