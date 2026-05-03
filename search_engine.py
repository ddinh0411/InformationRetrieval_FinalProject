import json
import numpy as np
from rank_bm25 import BM25Okapi
from text_processing import tokenize

# Class Object to be used for the UI of the IR model
class FinancialIR:
    # Creator Function for the Class Object
    def __init__(self, tokenized_doc_path, norm_doc_path):
        self.bm25 = None
        self.raw_documents = {}
        self.corpus_tokens = []
        self.doc_ids = []

        self._load_initial_corpus(tokenized_doc_path, norm_doc_path)

    # Function to load up the initial corpus and create model
    def _load_initial_corpus(self, tokenized_doc_path, norm_doc_path):
        with open(tokenized_doc_path, 'r', encoding='etf-8') as f:
            tokenized_data = json.load(f)
        with open(norm_doc_path, 'r', encoding='etf-8') as f:
            raw_docs = json.load(f)
            self.raw_documents = {d['doc_id']: d['text'] for d in raw_docs}

        for doc in tokenized_data:
            self.corpus_tokens.append(doc['tokens'])
            self.doc_ids.append(doc['doc_id'])

        self.bm25 = BM25Okapi(self.corpus_tokens)

    # Function to grab the 25 most relevant documents given a query
    # Returns a array where each object is the doc id, it's corresponding BM25 score, and text of the document
    def search(self, query_text, n=25):
        query_tokens = tokenize(query_text)
        scores = self.bm25.get_scores(query_tokens)
        top_docs = np.argsort(scores)[::-1][:n]

        return [{
            "doc_id": self.doc_ids[idx],
            "score": round(scores[idx], 4),
            "text": self.raw_documents.get(self.doc_ids[idx], "")
        } for idx in top_docs]
    
    # Function used to grab the AP and MAP scores for the BM25 model for queries
    def evaluate_IR(self, queries_list, qrels_dict):
        ap_scores = []

        for query in queries_list:
            q_id = q['query_id']
            relevents = set(qrels_dict.get(q_id, []))

            if not relevents:
                continue

            results = self.search(q['text'], n=len(self.doc_ids))

            hits = 0
            total_precision = 0.0
            for rank, res in enumerate(results, start=1):
                if res['doc_id'] in relevents:
                    hits += 1
                    total_precision += (hits / rank)
            
            ap = total_precision / len(relevents)
            ap_scores.append(ap)
            print(f"Query {q_id} AP: {ap:.4f}")
        
        map_score = sum(ap_scores) / len(ap_scores) if ap_scores else 0
        return map_score
    
    def update_corpus(self, new_docs):
        for doc in new_docs:
            doc_id = doc['doc_id']
            text = doc['text']

            self.raw_documents[doc_id] = text

            new_tokens = tokenize(text)

            self.corpus_tokens.append(new_tokens)
            self.doc_ids.append(doc_id)

        self.bm25 = BM25Okapi(self.corpus_tokens)
        print(f"Update Complete. Total documents now: {len(self.doc_id_map)}")

# Main Function goes here or just include and call the functions
# When initializing the path for the raw documents it should be dataset/documents.json
# For the tokenized docs the path should be outputs/tokenized_documents.json