from bs4 import BeautifulSoup
import requests
import glob
import json

all_json = []


# url_base = "https://docs.px4.io/main/en/"

# response = requests.get(url_base)

# soup = BeautifulSoup(response.text, "html.parser")

# print("Cleaned Document", soup)

cwd_path = r'C:\Users\Admin\Documents\portfolio_project\PX4-Autopilot'
docs_path = r"\docs"
en_path = r"\en"

# print(text)

filenames = glob.glob(cwd_path + docs_path + en_path + r'**\**\*.md', recursive=True)

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
