import json
import re

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

def chunk(text):
    all_chunks = []
    current_lines = []
    current_section = ""

    for line in text.split("\n"):
        heading = re.match(r"^(#{1,6})\s+(.*)", line)
        if heading:
            heading = heading.group(2)
            # print("Heading\n", heading)

            if current_lines:
                all_chunks.append({
                    "current_section": current_section,
                    "current_lines": "\n".join(current_lines).strip(),
                })
            current_section = heading
            current_lines = []
        else:
            # If it is a normal line, add it to our text collection
            if line.strip():  # Skips empty blank lines
                current_lines.append(line)


    # don't forget the last chunk after loop ends
    all_chunks.append({
        "current_section": current_section,
        "current_lines": "\n".join(current_lines).strip(),
    })
    return all_chunks


with open("output.json", 'r') as file:
    print("Reading from output.json file\n")
    all_dict = json.load(file)

for i in range(len(all_dict)):
    all_dict[i]["clean_text"] = clean(all_dict[i]["raw_text"])
    all_dict[i]["chunks"] = chunk(all_dict[i]["clean_text"])

# all_dict[0]["chunks"] = chunk(all_dict[0]["clean_text"])

with open("chunks.json", "w") as file:
    print("Writing to chunks.json file\n")
    json.dump(all_dict, file)
