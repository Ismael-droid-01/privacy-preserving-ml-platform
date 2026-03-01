import tenseal as ts
import pandas as pd
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

df = pd.read_csv("estudiantes.csv")
df = pd.DataFrame(df)


# 1. Preparación de datos matriciales (Emisor)
# En lugar de una lista de filas, creamos vectores planos para X e Y
X_flat = df['horas'].tolist()
y_flat = df['aprobado'].tolist()

enc_X = ts.ckks_vector(context, X_flat) # Vector de tamaño m
enc_y = ts.ckks_vector(context, y_flat) # Vector de tamaño m

# 2. Inicialización de Pesos
w = ts.ckks_vector(context, [0.1]) # Solo un peso para 'horas'
b = ts.ckks_vector(context, [0.0])

# Parámetros
lr = 0.05
m = len(X_flat)
lr_batch = lr / m

# --- ACTUALIZACIÓN MATRICIAL (PPML) ---

inicio = time.time()
print(f"RAM al inicio: {huella_ram():.2f} MB")

for epoch in range(3):
    # a. Predicción vectorizada: z = w * X + b
    # w es un escalar cifrado que multiplica a todo el vector X
    z = enc_X * w + b 
    
    # b. Activación (Sigmoide aproximada)
    # Aplicada a todo el vector simultáneamente
    y_hat = z * 0.197 + 0.5
    
    # c. Error vectorial: (h(x) - y)
    y_hat.scale = enc_y.scale # Alineación de escala para la resta
    error = y_hat - enc_y
    
    # d. Cálculo del Gradiente Matricial: X.T * error
    # Para una sola variable, es el producto punto entre el vector X y el vector error
    grad_w_scalar = enc_X.dot(error) 
    
    # Para el bias, sumamos todos los elementos del vector error
    grad_b_scalar = error.sum()

    # e. Actualización de Pesos
    w -= grad_w_scalar * lr_batch
    b -= grad_b_scalar * lr_batch

    # print(f"Época completada usando regla de actualización simplificada[cite: 75].")
    print(f"Epoch {epoch+1} - Consumo RAM: {huella_ram():.2f} MB")

# Al finalizar las épocas de entrenamiento
# w es el ckks_vector que contiene el peso de 'horas'
fin = time.time()
# 1. Descifrar el vector (requiere la clave secreta en el contexto)
pesos_finales = w.decrypt() 

# 2. Imprimir el resultado
# Como w es un vector, accedemos al primer elemento [0]
print(f"Peso final (w) para 'horas': {pesos_finales[0]}")
print(f"Bias final (b): {b.decrypt()[0]}")
tiempo_segundos = fin - inicio
tiempo_minutos = tiempo_segundos / 60

print(f"Tiempo total de ejecución: {tiempo_minutos:.2f} minutos")