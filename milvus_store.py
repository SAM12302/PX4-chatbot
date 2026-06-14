from pymilvus import MilvusClient

TIMEOUT = 120
HAS_COLLECTION = True

milvus_client = MilvusClient(
    uri="milvus_px4.db"
)
my_dict = {}

def create_collection():
    if not HAS_COLLECTION:
        milvus_client.create_collection(
            collection_name="px4_doc_collection",
            timeout=TIMEOUT,
            dimension=384,
            auto_id=True
        )
    else:
        milvus_client.drop_collection(
            collection_name="px4_doc_collection",
            timeout=TIMEOUT
        )
        milvus_client.create_collection(
            collection_name="px4_doc_collection",
            timeout=TIMEOUT,
            dimension=384,
            auto_id=True
        )

def insert_into_collection(my_dict):
    milvus_client.insert(
        collection_name="px4_doc_collection",
        data=my_dict
    )
