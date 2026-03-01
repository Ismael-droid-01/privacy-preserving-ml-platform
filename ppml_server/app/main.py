import numpy as np
import pickle
from fastapi import FastAPI, HTTPException, Request, Response
import time 
from Pyfhel import Pyfhel, PyCtxt
from app.ppml import LogisticRegression
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

app = FastAPI()

@app.post("/train")
async def train(request: Request):
    try:
        body = await request.body()
        package = pickle.loads(body)

        # 1. Rehidratar el objeto Pyfhel (Contexto y Llaves del cliente)
        HE = Pyfhel()
        HE.from_bytes_context(package["context"])
        HE.from_bytes_public_key(package["pk"])
        HE.from_bytes_relin_key(package["rlk"])

        # 2. Cargar Tensores Cifrados
        cx = PyCtxt(pyfhel=HE)
        cx.from_bytes(package["cx"])
        cy = PyCtxt(pyfhel=HE)
        cy.from_bytes(package["cy"])

        # 3. Inicializar el Entrenador con la clase
        trainer = LogisticRegression(
            HE, 
            n_features=package["n_features"], 
            m_samples=package["n_samples"],
            lr=0.05
        )

        print(f"Entrenando en Pyfhel: {package['n_features']} features...")
        initial_mem = get_memory_usage()
        start_time = time.time()

        # 4. Ciclo de entrenamiento (Épocas)
        # Gracias a la clase, el loop es súper limpio
        trainer.train(cx, cy, epochs=1)
            
        end_time = time.time()
        peak_mem = get_memory_usage()

        # 5. Serializar resultados (Enviamos los pesos cifrados de vuelta)
        metrics_package = {
            "w": trainer.ctxt_w.to_bytes(),
            "training_time": end_time - start_time,
            "compute_ram": peak_mem - initial_mem
        }

        return Response(
            content=pickle.dumps(metrics_package),
            media_type="application/octet-stream"
        )

    except Exception as e:
        print(f"Error en Pyfhel: {e}")
        raise HTTPException(status_code=500, detail=str(e))