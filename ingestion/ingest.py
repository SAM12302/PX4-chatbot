import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vectordb.embedder import embed
from vectordb.milvus_store import create_collection, insert_into_collection
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--chunks_file", help="Path to the chunks file", required=True)
args = parser.parse_args()

print("Creating milvus collection\n")
create_collection()

with open(args.chunks_file, "r") as file:
    print("Reading from chunks file\n")
    all_dict = json.load(file)

counter = 0

for my_dict in all_dict:
    dict_to_insert = {}
    dict_to_insert["source"] = my_dict["source"]
    dict_to_insert["relative_path"] = my_dict["relative_path"]
    for chunk in my_dict["chunks"]:
        dict_to_insert["text"] = chunk["current_lines"]
        dict_to_insert["vector"] = embed(chunk["current_lines"])
        print("Chunk embedded successfully\n")
        dict_to_insert["current_section"] = chunk["current_section"]
        insert_into_collection(dict_to_insert)
    print(f"Docs chunked {counter}\n")
    counter += 1

