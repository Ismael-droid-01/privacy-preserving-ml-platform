import tenseal as ts
import base64
import pandas as pd
from pathlib import Path
from app.core.config import settings

def encrypt_dataset_ckks(file_path: Path) -> str:
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.global_scale = 2**40
    context.generate_galois_keys()

    df = pd.read_csv(file_path)

    encrypted_columns = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            encrypted_columns[col] = ts.ckks_vector(context, df[col].tolist())

    context_bytes = context.serialize(save_public_key=True, save_secret_key=False)

    serialized_data = {col: vec.serialize() for col, vec in encrypted_columns.items()}
    
    return {
        "context": base64.b64encode(context_bytes).decode('utf-8'),
        "encrypted_vectors": {col: base64.b64encode(v).decode('utf-8') for col, v in serialized_data.items()}
    }