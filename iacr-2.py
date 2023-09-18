import json

with open('iacr.json', 'r') as f:
    papers = json.loads(f.read())

print(len(papers))
