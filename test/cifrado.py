import tenseal as ts
import numpy as np
import time
import psutil
import os

def huella_ram():
    # Obtiene el proceso actual
    proceso = psutil.Process(os.getpid())
    # Convierte bytes a Megabytes
    ram_mb = proceso.memory_info().rss / (1024 * 1024)
    return ram_mb

context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=2**15,
    coeff_mod_bit_sizes=[60] + [30] * 20 + [60]
)

context.global_scale = 2**30

context.generate_galois_keys()

context.auto_rescale = True

import pandas as pd

# Cargar el dataset
df = pd.read_csv('estudiantes.csv') # Asegúrate de que el nombre coincida

# Preparar X (características) y y (etiquetas)
# Convertimos a numpy array manteniendo la estructura de matriz para X
X = df[['horas']].values 
y = df['aprobado'].values

# Cifrado con TenSEAL
enc_X = [ts.ckks_vector(context, x.tolist()) for x in X]
enc_y = [ts.ckks_vector(context, [yi]) for yi in y]

# Pesos y bias cifrados
w = ts.ckks_vector(context, [0.1])
b = ts.ckks_vector(context, [0.0])

# Learning rate (en claro)
lr = 0.05
n_samples = len(enc_X)
lr_batch = lr / n_samples

EPOCHS = 3

inicio = time.time()
print(f"RAM al inicio: {huella_ram():.2f} MB")

for epoch in range(EPOCHS):
    # Inicializamos gradientes en cero para esta época
    grad_w = ts.ckks_vector(context, [0.0])
    grad_b = ts.ckks_vector(context, [0.0])

    for enc_x_i, enc_y_i in zip(enc_X, enc_y):
        # 1. Predicción: z = x · w + b
        z = enc_x_i.dot(w) + b

        # 2. Activación (Aproximación lineal: 0.197z + 0.5)
        y_hat = z * 0.197 + 0.5

        # 3. Error
        error = y_hat - enc_y_i

        # 4. Acumulación de gradientes (Suma homomórfica)
        # Multiplicamos por 2 y por x_i (consume nivel)
        grad_w += enc_x_i * error 
        grad_b += error

    # 5. Actualización ÚNICA de pesos por época
    # Esto reduce drásticamente el consumo de profundidad
    w -= grad_w * lr_batch
    b -= grad_b * lr_batch

    print(f"Epoch {epoch+1} - Consumo RAM: {huella_ram():.2f} MB")


fin = time.time()

# ENTRENAMIENTO EN PLANO
# Pesos y bias en claro
w_plain = np.array([0.1], dtype=float)
b_plain = 0.0

for epoch in range(EPOCHS):
    grad_w_plain = np.zeros_like(w_plain)
    grad_b_plain = 0.0

    for x_i, y_i in zip(X, y):
        z = np.dot(x_i, w_plain) + b_plain
        y_hat = 0.197 * z + 0.5
        error = y_hat - y_i

        grad_w_plain += x_i * error
        grad_b_plain += error

    w_plain -= lr_batch * grad_w_plain
    b_plain -= lr_batch * grad_b_plain

print("Entrenamiento en plano terminado")

# DESCIFRADO DE PESOS CKKS

w_ckks = np.array(w.decrypt())
b_ckks = b.decrypt()[0]

print("w CKKS  :", w_ckks)
print("b CKKS  :", b_ckks)
tiempo_segundos = fin - inicio
tiempo_minutos = tiempo_segundos / 60
print(f"Tiempo total de ejecución: {tiempo_minutos:.2f} minutos")
