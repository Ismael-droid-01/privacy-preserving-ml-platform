import tenseal as ts
import time

# Configuración del contexto CKKS
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.generate_galois_keys()
context.global_scale = 2**40

# Datos de entrada
vec1 = [5.3, 2.7]
vec2 = [1.5, 3.2]

enc_vec1 = ts.ckks_vector(context, vec1)
enc_vec2 = ts.ckks_vector(context, vec2)

# Ciclo de operaciones para medir rendimiento
iters = 1000
print(f"Ejecutando {iters} operaciones homomórficas...\n")

# Prueba de sumas
start_sum = time.time()
for _ in range(iters):
    _ = enc_vec1 + enc_vec2
sum_time = time.time() - start_sum

# Prueba de multiplicaciones
start_mul = time.time()
for _ in range(iters):
    _ = enc_vec1 * enc_vec2
mul_time = time.time() - start_mul

# Resultados
print(f"Tiempo total (sumas): {sum_time:.4f} s")
print(f"Tiempo total (multiplicaciones): {mul_time:.4f} s")
print(f"Promedio por suma: {sum_time/iters:.6f} s")
print(f"Promedio por multiplicación: {mul_time/iters:.6f} s\n")

# Verificación de resultados
print("Suma desencriptada:", (enc_vec1 + enc_vec2).decrypt())
print("Producto desencriptado:", (enc_vec1 * enc_vec2).decrypt())
