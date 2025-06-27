import pandas as pd

# Load your CSV
df = pd.read_csv("nissili_bilingual_inventory.csv")

# Show first 5 rows
print(df.head())

# Show columns
print("\nColumns:", df.columns.tolist())

# Quick info
print("\nInfo:")
print(df.info())