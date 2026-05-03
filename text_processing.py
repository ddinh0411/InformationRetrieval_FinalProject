#-------------------------------------------------------------
# AUTHOR: Ivan Trinh
# FILENAME: text_processing.py
# SPECIFICATION: main goal of this program is to tokenize any
# text that comes through here, be it a query or a document
#
# FOR: CS 5180- Final Project
# TIME SPENT: about like a few hours
#-----------------------------------------------------------*/

import json
import re
import time
from collections import defaultdict


#-------------------------------------------------------------
# Big stopword list aga
#-----------------------------------------------------------*/
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "need",
    "dare", "ought", "used", "not", "no", "nor", "so", "yet", "both",
    "either", "neither", "each", "every", "all", "any", "few", "more",
    "most", "other", "some", "such", "than", "too", "very", "s", "t",
    "just", "don", "should", "now", "d", "ll", "m", "o", "re", "ve", "y",
    "ain", "aren", "couldn", "didn", "doesn", "hadn", "hasn", "haven",
    "isn", "ma", "mightn", "mustn", "needn", "shan", "shouldn", "wasn",
    "weren", "won", "wouldn", "about", "above", "after", "again",
    "against", "also", "am", "as", "because", "before", "between",
    "during", "further", "here", "how", "i", "into", "it", "its",
    "itself", "me", "my", "myself", "once", "only", "our", "out", "own",
    "same", "she", "he", "her", "him", "his", "hers", "them", "their",
    "then", "there", "these", "they", "this", "those", "through", "under",
    "until", "up", "us", "we", "what", "when", "where", "which", "while",
    "who", "whom", "why", "you", "your", "yours", "yourself",
}

#-------------------------------------------------------------
# Basic porter stemmer 
#-----------------------------------------------------------*/
def stem(word: str) -> str:
    if len(word) <= 3:
        return word
    for suffix, replacement in [
        ("ational", "ate"), ("tional", "tion"), ("enci", "ence"),
        ("anci", "ance"), ("izer", "ize"), ("ising", "ise"),
        ("izing", "ize"), ("ising", "ise"),
        ("nesses", ""), ("fulness", ""), ("ousness", ""), ("iveness", ""),
        ("ational", ""), ("ingness", ""),
        ("ement", ""), ("ments", ""), ("ment", ""),
        ("ations", "ate"), ("ation", "ate"),
        ("ities", ""), ("iness", ""),
        ("ically", "ic"), ("ically", ""), ("ical", ""),
        ("ively", "ive"), ("ively", ""),
        ("fulness", "ful"),
        ("ously", ""), ("ious", ""),
        ("ings", ""), ("ing", ""),
        ("edly", ""), ("edly", "ed"),
        ("ness", ""), ("less", ""),
        ("ists", ""), ("ist", ""),
        ("ers", ""), ("er", ""),
        ("ies", "y"), ("ied", "y"),
        ("ves", ""), ("ves", "f"),
        ("ses", "s"), ("sses", "ss"),
        ("ness", ""),
        ("tion", ""), ("tions", ""),
        ("able", ""), ("ible", ""),
        ("ed", ""), ("es", ""), ("s", ""),
    ]:
        if word.endswith(suffix) and len(word) - len(suffix) > 2:
            return word[: len(word) - len(suffix)] + replacement
    return word

#-------------------------------------------------------------
# Main tokenizer
#-----------------------------------------------------------*/
def tokenize(text:str, apply_stem: bool = True) -> list[str]:
    # make lowercase
    text = text.lower()

    # expanding any contractions
    text = re.sub(r"n't", " not", text)
    text = re.sub(r"'s",  " ",    text)
    text = re.sub(r"'re", " are", text)
    text = re.sub(r"'ve", " have", text)
    text = re.sub(r"'ll", " will", text)
    text = re.sub(r"'d",  " would", text)
    # keeping only alphanumerical characters and space
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    result = []
    for tok in tokens:
        if tok in STOPWORDS:
            continue
        if tok.isdigit():
            continue
        if len(tok) < 2: # drop any single characters if any
            continue
        if apply_stem:
            tok = stem(tok)
            if not tok or len(tok) < 2:
                continue
        result.append(tok)
    return result

#-------------------------------------------------------------
# Constructing an inverted index based on a tokenized document
#-----------------------------------------------------------*/
def build_inverted_index(tokenized_docs: list[dict]) -> dict:
    index: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for doc in tokenized_docs:
        doc_id = doc["doc_id"]
        for pos, token in enumerate(doc["tokens"]):
            index[token][doc_id].append(pos)
    
    return {tok: dict(postings) for tok, postings in index.items()}

#-------------------------------------------------------------
# Testing the creation of an inverted index
#-----------------------------------------------------------*/
def main():
    print("=" * 60)
    print("IR Data Preprocessing Pipeline")
    print("=" * 60)
 
    # Loading json files
    print("\n[1/4] Loading raw data...")
    with open("dataset/queries.json", encoding="utf-8")   as f: queries   = json.load(f)
    with open("dataset/documents.json", encoding="utf-8") as f: documents = json.load(f)
    with open("dataset/qrels.json", encoding="utf-8")     as f: qrels     = json.load(f)
    print(f"      Queries  : {len(queries):>6,}")
    print(f"      Documents: {len(documents):>6,}")
    print(f"      Qrels    : {len(qrels):>6,}")
 
    # Tokenizing queries
    print("\n[2/4] Tokenizing queries...")
    t0 = time.time()
    tokenized_queries = []
    for q in queries:
        raw_tokens = q["text"].split()
        tokens = tokenize(q["text"], apply_stem=True)
        tokenized_queries.append({
            "query_id":         q["query_id"],
            "original_text":    q["text"],
            "tokens":           tokens,
            "token_count":      len(tokens),
            "raw_token_count":  len(raw_tokens),
        })
    print(f"      Done in {time.time()-t0:.2f}s  |  "
          f"avg {sum(q['token_count'] for q in tokenized_queries)/len(tokenized_queries):.1f} tokens/query")
 
    # Tokenize documents 
    print("\n[3/4] Tokenizing documents...")
    t0 = time.time()
    tokenized_docs = []
    total_raw = total_tok = 0
    for doc in documents:
        raw_tokens = doc["text"].split()
        tokens = tokenize(doc["text"], apply_stem=True)
        tokenized_docs.append({
            "doc_id":          doc["doc_id"],
            "original_text":   doc["text"],
            "tokens":          tokens,
            "token_count":     len(tokens),
            "raw_token_count": len(raw_tokens),
        })
        total_raw += len(raw_tokens)
        total_tok += len(tokens)
    elapsed = time.time() - t0
    print(f"      Done in {elapsed:.2f}s  |  "
          f"avg {total_tok/len(tokenized_docs):.1f} tokens/doc  |  "
          f"stopword/stem reduction: {(1 - total_tok/total_raw)*100:.1f}%")
 
    # Build inverted index
    print("\n[4/4] Building inverted index...")
    t0 = time.time()
    inv_index = build_inverted_index(tokenized_docs)
    elapsed = time.time() - t0
    print(f"      Done in {elapsed:.2f}s  |  "
          f"vocabulary size: {len(inv_index):,} unique terms")
 
    # Compute stats 
    postings_counts = [len(v) for v in inv_index.values()]
    postings_counts.sort(reverse=True)
    top10 = sorted(inv_index.items(), key=lambda x: len(x[1]), reverse=True)[:10]
 
    stats = {
        "queries": {
            "total": len(tokenized_queries),
            "avg_tokens": round(sum(q["token_count"] for q in tokenized_queries) / len(tokenized_queries), 2),
        },
        "documents": {
            "total": len(tokenized_docs),
            "total_tokens_after_preprocessing": total_tok,
            "total_tokens_before_preprocessing": total_raw,
            "stopword_stem_reduction_pct": round((1 - total_tok / total_raw) * 100, 2),
            "avg_tokens_per_doc": round(total_tok / len(tokenized_docs), 2),
        },
        "inverted_index": {
            "vocabulary_size": len(inv_index),
            "total_postings": sum(postings_counts),
            "avg_docs_per_term": round(sum(postings_counts) / len(inv_index), 2),
            "max_postings_term": top10[0][0],
            "top10_most_frequent_terms": [
                {"term": t, "doc_freq": len(v)} for t, v in top10
            ],
        },
        "qrels": {
            "total": len(qrels),
        },
    }
 
    # Save outputs 
    out_dir = "./outputs"
    import os; os.makedirs(out_dir, exist_ok=True)
 
    with open(f"{out_dir}/tokenized_queries.json",   "w") as f: json.dump(tokenized_queries, f, indent=2)
    with open(f"{out_dir}/tokenized_documents.json", "w") as f: json.dump(tokenized_docs,    f, indent=2)
    with open(f"{out_dir}/inverted_index.json",      "w") as f: json.dump(inv_index,         f, indent=2)
    with open(f"{out_dir}/preprocessing_stats.json", "w") as f: json.dump(stats,             f, indent=2)
 
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Queries tokenized    : {stats['queries']['total']}")
    print(f"  Documents tokenized  : {stats['documents']['total']}")
    print(f"  Vocabulary size      : {stats['inverted_index']['vocabulary_size']:,}")
    print(f"  Total postings       : {stats['inverted_index']['total_postings']:,}")
    print(f"  Avg tokens/doc       : {stats['documents']['avg_tokens_per_doc']}")
    print(f"  Reduction (stop+stem): {stats['documents']['stopword_stem_reduction_pct']}%")
    print("\nTop 10 most frequent terms:")
    for entry in stats["inverted_index"]["top10_most_frequent_terms"]:
        print(f"    {entry['term']:<20} doc_freq={entry['doc_freq']}")
    print("\nOutput files:")
    for fname in ["tokenized_queries.json", "tokenized_documents.json",
                  "inverted_index.json", "preprocessing_stats.json"]:
        size = os.path.getsize(f"{out_dir}/{fname}") / 1024
        print(f"    {fname:<35} ({size:>7.1f} KB)")
    print()
 
 
if __name__ == "__main__":
    main()
