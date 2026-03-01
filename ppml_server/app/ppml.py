import numpy as np
from Pyfhel import Pyfhel, PyCtxt

class LogisticRegression:
    def __init__(self, HE, n_features, m_samples, lr=0.05):
        self.HE = HE
        self.n_features = n_features
        self.m_samples = m_samples
        self.lr = lr / m_samples 
        self.n_slots = HE.get_nSlots()

        self.ctxt_w = self.HE.encrypt(np.array([0.1] * n_features, dtype=np.float64))
        self.ctxt_b = self.HE.encrypt(np.array([0.0] * self.n_slots, dtype=np.float64))

    def _maintenance(self, ctxt):
        self.HE.relinearize(ctxt)
        self.HE.rescale_to_next(ctxt)
        return ctxt

    def _z(self, cx):
        # z = x * w + b 

        # x * w
        z = cx * self.ctxt_w
        z = self._maintenance(z)

        # + b
        temp_b = self.ctxt_b.copy()
        self.HE.align_mod_n_scale(temp_b, z)
        z = z + temp_b

        return z
    
    def _sigmoid(self, z):
        # y_hat = 0.5 + 0.197z

        # 0.197z
        c_0197 = self.HE.encrypt(np.array([0.197] * self.n_slots, dtype=np.float64))
        self.HE.align_mod_n_scale(c_0197, z)
        y_hat = z * c_0197
        y_hat = self._maintenance(y_hat)

        # + 0.5
        c_05 = self.HE.encrypt(np.array([0.5] * self.n_slots, dtype=np.float64))
        self.HE.align_mod_n_scale(c_05, y_hat)
        y_hat = y_hat + c_05

        return y_hat
    
    def _error(self, y_hat, cy):
        # y_hat - y
        temp_y = cy.copy() # Usamos copia para no arruinar cy en el siguiente paso
        self.HE.align_mod_n_scale(temp_y, y_hat)
        error = y_hat - temp_y

        return error
    
    def _gradient(self, error, cx):
        temp_cx = cx.copy() # Usamos copia para no bajar de nivel la x original
        self.HE.align_mod_n_scale(temp_cx, error)
        grad_w = temp_cx * error
        grad_w = self._maintenance(grad_w)

        return grad_w
    
    def _update(self, grad_w):
        # CIFRAMOS el lr para que sea PyCtxt y soporte align_mod_n_scale
        c_lr = self.HE.encrypt(np.array([self.lr] * self.n_slots, dtype=np.float64))
        self.HE.align_mod_n_scale(c_lr, grad_w)
        update = grad_w * c_lr
        update = self._maintenance(update) 

        # Finalmente actualizamos el peso global
        self.HE.align_mod_n_scale(self.ctxt_w, update)
        self.ctxt_w = self.ctxt_w - update
        
    def train(self, cx, cy, epochs):
        
        for e in range(epochs):
            # 1. z = x * w + b
            z = self._z(cx)

            # 2. Sigmoide: 0.5 + 0.197z
            y_hat = self._sigmoid(z)
            
            # 3. Error (y_hat - y)
            error = self._error(y_hat, cy)

            # 4. Gradiente (x * error)
            grad_w = self._gradient(error, cx)

            # 5. Actualización de pesos
            self._update(grad_w)
        
        return error