import json
import re
from collections import defaultdict

# -----------------------------
# Preprocessing
# -----------------------------
STOPWORDS = set([
    "the","is","at","of","on","and","a","to","in","for","with"
])

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens

# -----------------------------
# Load Data
# -----------------------------
with open("documents.json") as f:
    documents = json.load(f)

with open("queries.json") as f:
    queries = json.load(f)

with open("qrels.json") as f:
    qrels = json.load(f)

# -----------------------------
# 1. Avg Document Length
# -----------------------------
doc_lengths = []

for doc in documents:
    tokens = preprocess(doc["text"])   # use cleaned version
    doc_lengths.append(len(tokens))

avg_doc_length = sum(doc_lengths) / len(documents)

# -----------------------------
# 2. Avg Query Length
# -----------------------------
query_lengths = []

for q in queries:
    tokens = preprocess(q["text"])
    query_lengths.append(len(tokens))

avg_query_length = sum(query_lengths) / len(queries)

# -----------------------------
# 3. Relevant Docs per Query
# -----------------------------
relevant_docs_count = {q["query_id"]: 0 for q in queries}

for entry in qrels:
    if entry["relevance"] == 1:
        relevant_docs_count[entry["query_id"]] += 1

# -----------------------------
# Output
# -----------------------------
print("Average Document Length:", avg_doc_length)
print("Average Query Length:", avg_query_length)

print("\nRelevant Documents per Query:")
for qid in sorted(relevant_docs_count.keys(), key=int):
    print(f"Query {qid} -> {relevant_docs_count[qid]}")
