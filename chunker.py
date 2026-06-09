import json
import re

with open("output.json", 'r') as file:
    all_dict = json.load(file)

def clean(text):
    for i in range(len(text)):
        final_text = {}
        final_text = re.sub("<script setup>.*?</script>", "", text, flags=re.DOTALL)
        print("Final Text", final_text)


clean(all_dict[0]["raw_text"])