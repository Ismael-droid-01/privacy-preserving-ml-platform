# -------------------------------------------------------
# DESCARGA DE DATOS DE LOS SIETE MAGNÍFICOS Y CREACIÓN DE CSV
# -------------------------------------------------------

import yfinance as yf
import pandas as pd
import numpy as np

# Lista de los "Seven Magnificent"
tickers = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "NVDA",   # Nvidia
    "GOOGL",  # Alphabet (Google Class A)
    "AMZN",   # Amazon
    "META",   # Meta Platforms (Facebook)
    "TSLA"    # Tesla
]

# Descargar datos históricos
data = yf.download(
    tickers,
    start="2015-01-01",
    end="2025-01-01",
    group_by="ticker",
    auto_adjust=True
)

# Construir dataset unificado
dataset = []

for t in tickers:
    df = data[t].copy()
    df["Ticker"] = t
    df["Return"] = df["Close"].pct_change()
    dataset.append(df)

# Unir todos los DataFrames
final_df = pd.concat(dataset)
final_df.reset_index(inplace=True)

# Eliminar filas con NaN (causadas por pct_change)
final_df.dropna(inplace=True)

# Guardar como CSV
output_file = "magnificent7_dataset.csv"
final_df.to_csv(output_file, index=False)

print("\n✔ Dataset generado correctamente")
print(f"📄 Archivo guardado como: {output_file}")
print("\n📦 Dimensiones del dataset:", final_df.shape)
print("\n📝 Columnas incluidas:")
print(final_df.columns)
