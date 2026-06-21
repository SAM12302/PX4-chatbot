import dotenv
from retry import retry
import os
from huggingface_hub import InferenceClient

dotenv.load_dotenv(".env")

model_id = os.getenv("LLM_MODEL")
hf_token = os.getenv("hf_token")

inference_client = InferenceClient(
    api_key=hf_token, provider="auto"
)

@retry(tries=3, delay=2)
def inference(text):
    result = inference_client.chat_completion(
    model="meta-llama/Llama-3.3-70B-Instruct",
    messages=[{"role": "user", "content": text}],
    max_tokens=1024,
    temperature=0.2,
    stream=True
)
    
    return result
if __name__ == "__main__":
    result = inference("Tell me what is the capital of France")
    for token in result:
        content = token.choices[0].delta.content
        if content is not None:
            print(content, end="", flush=True)
            import time
            time.sleep(0.05)