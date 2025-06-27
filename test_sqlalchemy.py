from sqlalchemy import create_engine
import pandas as pd

# Create a SQLAlchemy engine that connects to your SQLite DB
engine = create_engine('sqlite:///nissili_bilingual_inventory.db')

# Query your inventory table (grab 5 rows)
df = pd.read_sql('SELECT * FROM inventory LIMIT 5', engine)

print(df)