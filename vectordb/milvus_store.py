from pymilvus import MilvusClient
from dotenv import load_dotenv
import os

load_dotenv(".env")
db_name = os.getenv("MILVUS_DB_PATH")
print(repr(db_name))

TIMEOUT = 120

milvus_client = MilvusClient(
    uri=db_name
)

def create_collection():
    if not milvus_client.has_collection(collection_name="px4_doc_collection", timeout=TIMEOUT):
        milvus_client.create_collection(
            collection_name="px4_doc_collection",
            timeout=TIMEOUT,
            dimension=384,
            auto_id=True
        )
        print("Collection created\n")
    else:
        print("Collection already exists — appending to it\n")


def insert_into_collection(my_dict):
    milvus_client.insert(
        collection_name="px4_doc_collection",
        data=my_dict
    )