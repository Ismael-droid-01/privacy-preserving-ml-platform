from Pyfhel import Pyfhel, PyCtxt
import numpy as np
import time

# Configuración del contexto CKKS
HE = Pyfhel()
HE.contextGen(scheme='CKKS', n=2**14, scale=2**30, qi_sizes=[60, 40, 40, 60])
HE.keyGen()

# Datos de entrada
x = np.array([5.3, 2.7])
y = np.array([1.5, 3.2])

enc_x = HE.encryptFrac(x)
enc_y = HE.encryptFrac(y)

# Ciclo de operaciones para medir rendimiento
iters = 1000
print(f"Ejecutando {iters} operaciones homomórficas...\n")

# Prueba de sumas
start_sum = time.time()
for _ in range(iters):
    _ = enc_x + enc_y
sum_time = time.time() - start_sum

# Prueba de multiplicaciones
start_mul = time.time()
for _ in range(iters):
    _ = enc_x * enc_y
mul_time = time.time() - start_mul

# Resultados
print(f"Tiempo total (sumas): {sum_time:.4f} s")
print(f"Tiempo total (multiplicaciones): {mul_time:.4f} s")
print(f"Promedio por suma: {sum_time/iters:.6f} s")
print(f"Promedio por multiplicación: {mul_time/iters:.6f} s\n")

# Verificación de resultados
dec_sum = HE.decryptFrac(enc_x + enc_y)
dec_prod = HE.decryptFrac(enc_x * enc_y)

print("Suma desencriptada:", dec_sum[:2])
print("Producto desencriptado:", dec_prod[:2])
