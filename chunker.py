import json
import re

with open("output.json", 'r') as file:
    all_dict = json.load(file)

def clean(text):
    """Remove noise from the text for RAG pipeline.

    Args:
        text (str): input text raw_text

    Returns:
        str: clean text from noise
    """
    final_text = re.sub("<script setup>.*?</script>", "", text, flags=re.DOTALL)
    # final_text = re.sub(r":::\s*.*?\s*:::", "", final_text, flags=re.DOTALL)
    final_text = re.sub(r":::.*?:::", "", final_text, flags=re.DOTALL)
    final_text = re.sub(r"<[^>]+>", "", final_text)           # strips all HTML/Vue tags
    final_text = re.sub(r"<!--.*?-->", "", final_text, flags=re.DOTALL)  # strips HTML comments
    final_text = re.sub(r"\n{3,}", "\n\n", final_text)
    return final_text

for i in range(len(all_dict)):
    all_dict[i]["clean_text"] = clean(all_dict[i]["raw_text"])

with open("output.json", "w") as file:
    print(all_dict[0]["clean_text"])
    json.dump(all_dict, file)
