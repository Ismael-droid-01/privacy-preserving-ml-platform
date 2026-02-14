import requests
import base64
import argparse

URL_BASE = "http://localhost:8000/api/v1/datasets"
URL_PPML = "http://localhost:8001/train"

def main(file, preview, encrypt):
    if file:
        with open(file, "rb") as f:
            csv_base64 = base64.b64encode(f.read()).decode('utf-8')
        payload = {"dataset_base64": csv_base64, "target": "columna_objetivo"}
        response_up = requests.post(f"{URL_BASE}/upload", json=payload)
        data_up = response_up.json()

        if response_up.status_code == 200:
            dataset_id = data_up["dataset_id"]
            print(f"Éxito. ID recibido: {dataset_id}")
        else:
            print("Error en subida:", response_up.text)
        return
    
    if preview:
        response_preview = requests.get(f"{URL_BASE}/{preview}/preview")

        if response_preview.status_code == 200:
            print("head: ")
            data = response_preview.json()
            for row in data['data']:
                print(row)
            print("Metadatos: ", data['metadata'])
        else:
            print(f"{response_preview.status_code} - {response_preview.text}")

    if encrypt:
        response_encrypt = requests.post(f"{URL_BASE}/{encrypt}/encrypt")

        if response_encrypt.status_code == 200:
            data = response_encrypt.json()
            print(data["encrypted_vector"])
            confirmation = input("He recibido los datos deseas mandarlos al PPML?")
            if confirmation.lower() == "yes":
                print("Enviado por favor espere...")
            else:
                print("Ahi nos vemos usuario :)")

        else:
            print(f"{response_encrypt.status_code} - {response_encrypt.text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str)
    parser.add_argument("--preview", type=str)
    parser.add_argument("--encrypt", type=str)
    args = parser.parse_args()

    main(file=args.file,  
         preview=args.preview,
         encrypt=args.encrypt
        )