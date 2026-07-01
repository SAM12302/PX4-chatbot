"""Example Use:
python path/to/scraper.py 
  --cwd_path path/to/repo
  --source_name Source_Name 
  --output_file output_source.json
"""
import glob
import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--cwd_path", help="Path to the cloned repository", required=True)
parser.add_argument("--en_path_flag", help="Flag to indicate the English path",
                     action="store_true")
parser.add_argument("--source_name", help="Name of the source", required=True)
parser.add_argument("--output_file", help="Name of the output file",required=True)
args = parser.parse_args()


all_json = []

# cwd_path = os.getenv("CWD_PATH")
cwd_path = args.cwd_path
docs_path = "/docs"
en_path = "/en" if args.en_path_flag else ""

filenames = glob.glob(cwd_path + docs_path + en_path + '**/**/*.md', recursive=True)

for filename in filenames:
    final_json = {}
    with open(filename, 'r', encoding='utf-8') as file:
        raw_text = file.read()
        final_json["source"] = args.source_name
        final_json["raw_text"] = raw_text
        final_json["relative_path"] = filename.rsplit(sep=docs_path)[1]

    all_json.append(final_json)

# with open("output.json", 'w') as file:
#     json.dump(all_json, file, indent=4)

with open(args.output_file, 'w') as file:
    json.dump(all_json, file, indent=4)
