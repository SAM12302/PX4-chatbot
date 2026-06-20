from bs4 import BeautifulSoup
import requests
import glob
import json
import os
from dotenv import load_dotenv

load_dotenv()


all_json = []

cwd_path = os.getenv("CWD_PATH")
docs_path = "/docs"
en_path = "/en"

filenames = glob.glob(cwd_path + docs_path + en_path + '**/**/*.md', recursive=True)

for filename in filenames:
    final_json = {}
    with open(filename, 'r', encoding='utf-8') as file:
        raw_text = file.read()
        final_json["source"] = "PX4-user_guide"
        final_json["raw_text"] = raw_text
        final_json["relative_path"] = filename.rsplit(sep=docs_path)[1]

    all_json.append(final_json)

with open("output.json", 'w') as file:
    json.dump(all_json, file, indent=4)
