import dotenv
from retry import retry
import os
from huggingface_hub import InferenceClient

dotenv.load_dotenv(".env")

model_id = os.getenv("EMBEDDING_MODEL")
hf_token = os.getenv("hf_token")

inference_client = InferenceClient(
    api_key=hf_token, provider="hf-inference"
)

@retry(tries=3, delay=2)
def embed(text):
    result = inference_client.feature_extraction(
        text,
        model=model_id
    )
    return result
