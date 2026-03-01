from fastapi import APIRouter, HTTPException, UploadFile, File
from app.schemas.response import UploadResponse, DatasetPreviewResponse
import requests
import pickle
import pandas as pd
from fastapi import HTTPException
from Pyfhel import Pyfhel, PyCtxt
import uuid
import numpy as np
import pickle
import os
import psutil

STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

memory_storage = {}

def save_to_memory(df: pd.DataFrame, parent_id: str = None, tag: str = "original") -> str:
    try:
        dataset_id = f"{tag}_{uuid.uuid4().hex[:8]}" 
        # dataset_id = "estudiantes"
        memory_storage[dataset_id] = {
            "df": df,
            "parent_id": parent_id,
            "type": tag
        }
        return dataset_id
    except Exception as e:
        raise Exception(f"Error al guardar en memoria: {e}")

def get_ram_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload", response_model=UploadResponse)
def upload_dataset(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        dataset_id = str(uuid.uuid4())

        file_path = os.path.join(STORAGE_DIR, f"{dataset_id}.bin")

        with open(file_path, "wb") as f:
            pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)

        return UploadResponse(
            dataset_id=dataset_id,
            message="Dataset saved as binary"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        file.file.close()

@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(dataset_id: str):
    try:
        df = load_dataset(dataset_id)

        metadata = {
            "columns": df.columns.tolist(),
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "null_counts": df.isnull().sum().to_dict()
        }

        df_head = df.head(10)
        data_dict = df_head.to_dict(orient="records")

        return DatasetPreviewResponse(
            dataset_id=dataset_id,
            metadata=metadata,
            data=data_dict,
            message="Successfully generated preview"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing dataset: {str(e)}"
        )

def create_context():
    HE = Pyfhel()
    HE.contextGen(
        scheme='ckks', 
        n=16384, 
        scale=2**40,         
        qi_sizes=[60, 40, 40, 40, 40, 60]  
    )

    HE.keyGen()            
    HE.relinKeyGen()        
    HE.rotateKeyGen()       
        
    return HE

def load_dataset(dataset_id: str):
    file_path = os.path.join(STORAGE_DIR, f"{dataset_id}.bin")
    with open(file_path, "rb") as f:
        df = pickle.load(f)
    return df

def encrypt_dataset(dataset_id: str):
    try:
        HE = create_context()
        df = load_dataset(dataset_id)

        X_data = df.iloc[:, :-1].values.astype(np.float64).flatten()
        y_data = df.iloc[:, -1].values.astype(np.float64)

        cx = HE.encrypt(X_data)
        cy = HE.encrypt(y_data)

        return HE, cx, cy
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encrypting the dataset {dataset_id}: {str(e)}")

@router.post("/{dataset_id}/submit")
def sumbit_dataset(dataset_id: str):
    initial_mem = get_ram_usage()
    HE, cx, cy = encrypt_dataset(dataset_id)
    peak_mem = get_ram_usage()

    # Temporal: Debemos de ver la manera de obtener esto mas rapido
    file_path = os.path.join(STORAGE_DIR, f"{dataset_id}.bin")
    with open(file_path, "rb") as f:
        df = pickle.load(f)
    n_samples = df.shape[0]
    n_features = df.shape[1] - 1

    package = {
        "context": HE.to_bytes_context(),
        "pk": HE.to_bytes_public_key(),
        "rlk": HE.to_bytes_relin_key(), 
        "cx": cx.to_bytes(),
        "cy": cy.to_bytes(),
        "n_features": n_features,
        "n_samples": n_samples
    }
    
    response = requests.post(
        "http://localhost:8001/train", 
        data=pickle.dumps(package), 
        headers={'Content-Type': 'application/octet-stream'},
        timeout=300
    )

    if response.status_code == 200:
        result_package = pickle.loads(response.content)
        return {
            "training_time": f"{result_package.get('training_time', 0):.4f}s",
            "compute_ram": f"{result_package.get('compute_ram', 0)}mb",
            "encryption_ram": f"{peak_mem - initial_mem}mb",
            "message": "Homomorphic training correctly"
        }
    else:
        return {
            "training_time": "0s",
            "message": f"Server error: {response.text}"
        }


###########################################################################################################
def encrypt_datasetsssssssss(dataset_id: str):
    try:
        HE = create_context()
        file_path = os.path.join(STORAGE_DIR, f"{dataset_id}.bin")
        with open(file_path, "rb") as f:
            df = pickle.load(f)
        
        # 1. Preparación de dimensiones
        n_samples = df.shape[0]
        n_features = df.shape[1] - 1
        
        # 2. Organización de los datos (IMPORTANTE)
        # Para que el servidor haga (cx * w), cx debe estar alineado.
        # Si x_data es [f1, f2, f1, f2...], al multiplicar por w [w1, w2], 
        # coincidirán perfectamente en los slots.
        X_data = df.iloc[:, :-1].values.astype(np.float64).flatten()
        y_data = df.iloc[:, -1].values.astype(np.float64)

        # 3. Cifrado
        cx = HE.encrypt(X_data)
        
        cy = HE.encrypt(y_data)

        # 4. Serialización
        package = {
            "context": HE.to_bytes_context(),
            "pk": HE.to_bytes_public_key(),
            "rlk": HE.to_bytes_relin_key(), 
            "cx": cx.to_bytes(),
            "cy": cy.to_bytes(),
            "n_features": n_features,
            "n_samples": n_samples
        }

        # 5. Envío
        url_ppml = "http://localhost:8001/train_pyfhel"
        response = requests.post(
            url_ppml, 
            data=pickle.dumps(package), 
            headers={'Content-Type': 'application/octet-stream'},
            timeout=300
        )
        
        if response.status_code == 200:
            result_package = pickle.loads(response.content)

            # 6. Reconstrucción y Descifrado de los pesos finales
            enc_w = PyCtxt(pyfhel=HE)
            enc_w.from_bytes(result_package["w"])
            
            # Desciframos (esto usa la llave privada que solo el cliente tiene)
            dec_w = HE.decrypt(enc_w)
            
            # Como el resultado es un vector de slots, tomamos los primeros n_features
            weights = np.round(dec_w[:n_features], 4).tolist()
            
            # El bias puede venir cifrado también
            bias = 0.0
            if "b" in result_package and isinstance(result_package["b"], bytes):
                enc_b = PyCtxt(pyfhel=HE)
                enc_b.from_bytes(result_package["b"])
                bias = round(HE.decrypt(enc_b)[0], 4)
            else:
                bias = result_package.get("b", 0.0)

            return {
                "status": "success",
                "weights": weights,
                "bias": bias,
                "training_time": f"{result_package.get('training_time', 0):.4f}s"
            }
        else:
            return {"status": "error", "detail": f"PPML Server Error: {response.text}"}

    except Exception as e:
        return {"status": "error", "detail": f"Client Error: {str(e)}"}