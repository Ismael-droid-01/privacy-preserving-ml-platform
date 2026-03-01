import requests
import base64
import argparse

URL_BASE = "http://localhost:8000/api/v1/datasets"
URL_PPML = "http://localhost:8001/train"

def main(file, preview, split, dispatch):
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

    if split:
        split_payload = {
            "test_size": 0.2,
            "random_state": 42,
            "shuffle": True
        }
        response_split = requests.post(f"{URL_BASE}/{split}/split", json=split_payload)

        if response_split.status_code == 200:
            data = response_split.json()
            print(data["message"])
            print(f"train_id: {data['train_id']}")
            print(f"test_id: {data['test_id']}")
            print(f"sizes: {data['sizes']}")
        else:
            print(f"{response_split.status_code} - {response_split.text}")

    if dispatch:
        response_dispatch = requests.post(f"{URL_BASE}/{dispatch}/dispatch")

        if response_dispatch.status_code == 200:
            data = response_dispatch.json()
            print(f"Estado: {data['status']}")
            print(f"W: {data['weights']}")
            print(f"B: {data['bias']}")
            print(f"Time: {data['training_time']}")
        else:
            print(f"{response_dispatch.status_code} - {response_dispatch.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str)
    parser.add_argument("--preview", type=str)
    parser.add_argument("--split", type=str)
    parser.add_argument("--dispatch", type=str)
    args = parser.parse_args()

    main(file=args.file,  
         preview=args.preview,
         split=args.split,
         dispatch=args.dispatch
        )