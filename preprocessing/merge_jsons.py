import json
from pathlib import Path
# read the json files from ../json/saa-c02/*.json
# folder = Path(__file__).parent.parent / "json" / "saa-c02"
# json_files = list(folder.glob("*.json"))
# merged_json = []
# for file in json_files:
#     with open(file, "r", encoding="utf8") as f:
#         j = f.read()
#     merged_json.extend(j)
#
# with open("merged.json", "w", encoding="utf8") as f:
#     json.dump(merged_json, f, indent=4)

# read data.json and merged.json and merge them into data.json 
folder = Path(__file__).parent.parent
data_file = folder / "data.json"
merged_file = folder / "merged.json"
with open(data_file, "r", encoding="utf8") as f:
    data = json.load(f)
with open(merged_file, "r", encoding="utf8") as f:
    merged = json.load(f)

data.extend(merged)
with open(data_file, "w", encoding="utf8") as f:
    json.dump(data, f, indent=4)
