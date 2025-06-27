import pandas as pd
import sqlite3

# Load your CSV
df = pd.read_csv('nissili_bilingual_inventory.csv')

# Connect (or create) SQLite DB
conn = sqlite3.connect('nissili_bilingual_inventory.db')

# Save DataFrame to a SQL table named "inventory"
df.to_sql('inventory', conn, if_exists='replace', index=False)

# Close the connection
conn.close()

print("CSV data saved to SQLite DB successfully!")