from pymilvus import MilvusClient
import dotenv
import os
import pandas as pd
from vectordb.embedder import embed

dotenv.load_dotenv(".env")

DB = os.getenv("MILVUS_DB_PATH")
COLLECTION_NAME = os.getenv("collection_name")

def search_embedding(query: str):
    client = MilvusClient(
        uri=DB
    )

    client.load_collection(
        COLLECTION_NAME
    )

    query_embedding = embed(query)

    result = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_embedding],
        anns_field="vector",
        output_fields=["source", "current_section", "text"],
        limit=5
    )

    return result

if __name__ == "__main__":
    result = search_embedding(query="How do I activate Offboard Mode")
    result = str(result)
    # results_df = pd.DataFrame(result)
    with open("output.txt", "w") as file:
        file.write(result)