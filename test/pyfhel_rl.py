from Pyfhel import Pyfhel

HE = Pyfhel()

# Contexto
HE.contextGen(
    scheme="ckks", # Esquema de cifrado
    n=16384, # Numero de slots (mas grande mas seguro pero mas lento)
    scale=2**40, # Precision decimal
    qi_sizes=[60, 40, 40, 40, 40, 60] # Profundidad multiplicativa
)

HE.keyGen() # Llave privada (guardar en secreto) 
HE.relinKeyGen() # Llave  para multiplicaciones

import numpy as np

# Dataset
X_raw = np.array([
    [0.1, 0.2], 
    [0.4, 0.5], 
    [0.7, 0.8], 
    [0.9, 0.1]
], dtype=np.float64)
y_raw = np.array([0.0, 0.0, 1.0, 1.0], dtype=np.float64)

# Pesos y bias
w_raw = np.array([0.15, -0.2], dtype=np.float64)
b_raw = np.array([0.1], dtype=np.float64)

# Solo para fila uno
x_sample = X_raw[0]
w = w_raw
b = b_raw[0]

# Encriptacion de las caracteristicas
ctxt_x = HE.encrypt(x_sample)
# Encriptacion de los pesos iniciales
ctxt_w = HE.encrypt(w)
# Encriptacion del bias

# Multiplicacion
ctxt_prod = ctxt_x * ctxt_w
HE.relinearize(ctxt_prod) # Devolverlo al tamano normal (Para que no crezca en memoria)
HE.rescale_to_next(ctxt_prod) # Rescalado de 2^80 a 2^40

ptxt_b = HE.encode(np.array([b] * HE.get_nSlots(), dtype=np.float64)) # Crear un vector que todos sus valores tienen bias
# Encriptacion del bias
ctxt_b = HE.encrypt(np.array([b] * HE.get_nSlots(), dtype=np.float64))
HE.align_mod_n_scale(ctxt_b, ctxt_prod) # Ajusta los dos vectores al mismo nivel

ctxt_z = ctxt_prod + ctxt_b

res_intermedio = HE.decrypt(ctxt_z)
print(f"Resultado: {x_sample * w + b}")
print(f"Resultado de (x*w + b) CKKS: {res_intermedio[:2]}")

# Sigmoide
# 0.197 x z
# Creacion del vector para todos los slots
c1 = 0.197
ptxt_c1 = HE.encode(np.array([c1] * HE.get_nSlots(), dtype=np.float64))
ctxt_c1 = HE.encrypt(ptxt_c1)

# Multiplicacion: z * 0.197
HE.align_mod_n_scale(ctxt_c1, ctxt_z) # Hace dos cosas (que para la multiplicacion solo es necesaria una)
ctxt_sigmoid_part1 = ctxt_z * ctxt_c1

# Limpieza de la multiplicacion
HE.relinearize(ctxt_sigmoid_part1)
HE.rescale_to_next(ctxt_sigmoid_part1)

# Suma: + 0.5
c2 = 0.5
ptxt_c2 = HE.encode(np.array([c2] * HE.get_nSlots(), dtype=np.float64))
ctxt_c2 = HE.encrypt(ptxt_c2)

# Alineacion: Bajamos el 0.5 a nivel donde esta la parte1
HE.align_mod_n_scale(ctxt_c2, ctxt_sigmoid_part1)

# Suma final: 0.5 + (0.197 * z)
ctxt_y_hat = ctxt_sigmoid_part1 + ctxt_c2

y_hat_final = HE.decrypt(ctxt_y_hat)

z_normal = x_sample * w + b
sigmoide_normal = 0.5 + 0.197 * z_normal

print(f"Predicción normal (0.5 + 0.197z): {sigmoide_normal[:2]}")
print(f"Predicción CKKS (y_hat): {y_hat_final[:2]}")

# Error: Error = Prediccion - Etiqueta Real
y_target = y_raw[0]
ptxt_y_real = HE.encode(np.array([y_target] * HE.get_nSlots(), dtype=np.float64))
ctxt_y_real = HE.encrypt(ptxt_y_real)

HE.align_mod_n_scale(ctxt_y_real, ctxt_y_hat)

ctxt_error = ctxt_y_hat - ctxt_y_real

error_descifrado = HE.decrypt(ctxt_error)
print(f"Error calculado (CKKS): {error_descifrado[0]}")
print(f"Error real (NumPy): {sigmoide_normal[0] - y_target}")

# Calculo del gradiente
# w = x * (y_hat - y)
ctxt_x_aligned = ctxt_x.copy() 
HE.align_mod_n_scale(ctxt_x_aligned, ctxt_error) # Bajar las x al mismo nivel que error

# Multiplicacion
ctxt_grad_w = ctxt_x_aligned * ctxt_error

# Limpieza
HE.relinearize(ctxt_grad_w)
HE.rescale_to_next(ctxt_grad_w)

grad_w_descifrado = HE.decrypt(ctxt_grad_w)

grad_w_normal = x_sample * (sigmoide_normal[0] - y_target)

print(f"Gradiente w (CKKS): {grad_w_descifrado[:2]}")
print(f"Gradiente w (NumPy): {grad_w_normal}")

# Actualizacion de pesos: w_nuevo = w_viejo - (lr * der(w))
learning_rate = 0.01
ptxt_lr = HE.encode(np.array([learning_rate] * HE.get_nSlots(), dtype=np.float64))
ctxt_lr = HE.encrypt(ptxt_lr)
# Multiplicar gradiente por learning rate (grad_w * 0.01)
# ptxt_lr.scale = ctxt_grad_w.scale
HE.align_mod_n_scale(ctxt_lr, ctxt_grad_w)
ctxt_update = ctxt_grad_w * ptxt_lr

# Limpieza
HE.relinearize(ctxt_update)
HE.rescale_to_next(ctxt_update)

# Restar el update a los pesos originales
ctxt_w_new = ctxt_w.copy()
HE.align_mod_n_scale(ctxt_w_new, ctxt_update)

w_final_ctxt = ctxt_w_new - ctxt_update

w_final = HE.decrypt(w_final_ctxt)

w_numpy_new = w - (learning_rate * grad_w_normal)

print(f"Pesos actualizados (CKKS): {w_final[:2]}")
print(f"Pesos actualizados (NumPy): {w_numpy_new}")