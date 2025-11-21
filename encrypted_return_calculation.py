"""
Cálculo de retorno acumulado de AAPL:
- En claro
- Usando TenSEAL (suma homomórfica de log(1+r) con ciphertexts escalares)
"""

import pandas as pd
import numpy as np
import tenseal as ts

# ============================================================
# 1. CARGAR DATASET Y PREPARAR RETORNOS
# ============================================================

# Ajusta la ruta según tu repo
df = pd.read_csv("data/magnificent7_dataset.csv")

# Nos quedamos solo con AAPL y ordenamos por fecha
df_aapl = df[df["Ticker"] == "AAPL"].sort_values("Date").dropna()

# Tomamos la columna de retornos (asumiendo que existe "Return")
returns = df_aapl["Return"].tolist()
print(f"Días de datos AAPL (originales): {len(returns)}")

# ============================================================
# 2. LIMPIEZA / SEGURIDAD PARA LOG(1+r)
# ============================================================

# Para evitar problemas con log(1+r), filtramos valores peligrosos
safe_returns = []
for r in returns:
    # Si r <= -0.9999, (1+r) ≈ 0 o negativo -> log no definido / ruido brutal
    if r <= -0.9999:
        # Opción 1: saltar ese día
        # continue

        # Opción 2: clamp (lo dejo como clamp ligero)
        r = -0.9999
    safe_returns.append(r)

print(f"Días de datos AAPL usados (safe_returns): {len(safe_returns)}")

# ============================================================
# 3. RETORNO ACUMULADO EN CLARO (USANDO safe_returns)
# ============================================================

growth_factors = [1.0 + r for r in safe_returns]
retorno_acum_claro = np.prod(growth_factors) - 1.0

print("\n=== RETORNO ACUMULADO EN CLARO (safe_returns) ===")
print(f"Retorno acumulado: {retorno_acum_claro:.6f}  ({retorno_acum_claro*100:.2f}%)")

# También calculamos suma de logs en claro (para comparar con HE)
logs_growth = [float(np.log(1.0 + r)) for r in safe_returns]
sum_logs_claro = sum(logs_growth)
retorno_desde_logs_claro = np.exp(sum_logs_claro) - 1.0

print("\nChequeo vía logs en claro:")
print(f"Suma logs (claro): {sum_logs_claro:.6f}")
print(f"Retorno desde logs (claro): {retorno_desde_logs_claro:.6f}  ({retorno_desde_logs_claro*100:.2f}%)")

# ============================================================
# 4. CONTEXTO CKKS
# ============================================================

context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,      # suficiente para todos los datos
    coeff_mod_bit_sizes=[40, 20, 40]
)
context.global_scale = 2**20
context.generate_galois_keys()

# ============================================================
# 5. CIFRAR CADA LOG(1+r) EN CIPHERTEXTS ESCALARES
# ============================================================

enc_logs_list = []
for lg in logs_growth:
    # Cada ciphertext tiene UN solo slot
    enc_logs_list.append(ts.ckks_vector(context, [lg]))

# ============================================================
# 6. SUMA HOMOMÓRFICA DE LOS LOGS
# ============================================================

# Inicializamos con el primer ciphertext
enc_sum_logs = enc_logs_list[0]
for ct in enc_logs_list[1:]:
    enc_sum_logs = enc_sum_logs + ct

# desencriptamos el escalar
sum_logs_he = enc_sum_logs.decrypt()[0]

# reconstruimos retorno acumulado
retorno_acum_from_he = np.exp(sum_logs_he) - 1.0

# ============================================================
# 7. COMPARAR RESULTADOS
# ============================================================

print("\n=== RETORNO ACUMULADO VÍA HE (suma de logs cifrados) ===")
print(f"Suma logs (HE): {sum_logs_he:.6f}")
print(f"Retorno acumulado (HE): {retorno_acum_from_he:.6f}  ({retorno_acum_from_he*100:.2f}%)")

diff = abs(retorno_acum_claro - retorno_acum_from_he)
print(f"\nDiferencia entre claro y HE: {diff:.10f}")
