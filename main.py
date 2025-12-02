import numpy as np
from  sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.datasets import make_classification
from Pyfhel import Pyfhel

def generate_dataset():
    X, y = make_classification(
        n_samples=300,
        n_features=2,
        n_redundant=0,
        n_informative=2,
        n_clusters_per_class=1,
        class_sep=2.0,
        random_state=0
    )

    return train_test_split(X, y, test_size=0.2, random_state=0)

def train_plain_model(X_train, y_train):
    model = LogisticRegression()
    model.fit(X_train, y_train)
    return model

def init_ckks_context():
    HE = Pyfhel()
    HE.contextGen(
        scheme='CKKS',
        n=2**14,
        scale=2**30,
        qi_sizes=[60, 30, 30, 30, 60]
    )
    HE.keyGen()
    HE.relinKeyGen()
    HE.rotateKeyGen()
    return HE

def encrypted_predict(HE, X_test, weights, bias):
    encrypted_predictions = []

    for x in X_test:
        ctxt_x = HE.encryptFrac(x)

        ctxt_res = ctxt_x * weights

        HE.cumul_add(ctxt_res)

        ctxt_res = ctxt_res + bias

        decrypted_value = HE.decryptFrac(ctxt_res)[0]

        pred = 1 if decrypted_value >= 0 else 0
        encrypted_predictions.append(pred)

    return encrypted_predictions

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = generate_dataset()

    model = train_plain_model(X_train, y_train)
    y_pred_plain = model.predict(X_test)

    print("Plain Accuracy: ", accuracy_score(y_test, y_pred_plain))
    print("Weights: ", model.coef_)
    print("Bias: ", model.intercept_)

    weights = model.coef_[0]
    bias = model.intercept_[0]

    HE = init_ckks_context()

    y_pred_encrypted = encrypted_predict(HE, X_test, weights, bias)

    encrypted_acc  = accuracy_score(y_test, y_pred_encrypted)

    print(f"Encrypted predictions (first 5): {y_pred_encrypted[:5]}")
    print(f"Encrypted Accuracy: {encrypted_acc}")