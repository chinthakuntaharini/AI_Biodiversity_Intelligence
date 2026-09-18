"""
Knowledge Base and Retrieval-Augmented Generation (RAG) Engine.
Maintains indexed corpus of peer-reviewed literature, environmental metrics,
and multi-variable ecological interventions.
"""

import os
import json
import math
import re
from typing import List, Dict, Any, Optional

class KnowledgeDocument:
    def __init__(self, doc_id: str, domain: str, topic: str, content: str,
                 key_variables: List[str], interventions: List[Dict[str, Any]],
                 citations: List[str]):
        self.doc_id = doc_id
        self.domain = domain
        self.topic = topic
        self.content = content
        self.key_variables = key_variables
        self.interventions = interventions
        self.citations = citations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "domain": self.domain,
            "topic": self.topic,
            "content": self.content,
            "key_variables": self.key_variables,
            "interventions": self.interventions,
            "citations": self.citations
        }


class KnowledgeBase:
    """
    Structured retrieval layer for environmental and biodiversity metrics.
    Combines structured property filtering with BM25/cosine semantic relevance.
    """

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_path, "data", "knowledge_store")
        
        self.data_dir = data_dir
        self.documents: List[KnowledgeDocument] = []
        self.vocab: Dict[str, int] = {}
        self.doc_term_freqs: List[Dict[str, int]] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_length: float = 0.0
        self.idf: Dict[str, float] = {}

        self._load_corpus()
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r'[a-zA-Z0-9_\-\.\%]+', text.lower())
        stopwords = {
            "a", "an", "the", "in", "on", "of", "to", "for", "with", "and", "or",
            "is", "are", "was", "were", "by", "as", "at", "it", "from", "be", "this",
            "that", "into", "over", "such", "can", "should", "will"
        }
        return [t for t in tokens if t not in stopwords and len(t) > 1]

    def _load_corpus(self):
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Knowledge store directory not found at {self.data_dir}")

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        records = json.load(f)
                        for record in records:
                            doc_id = record.get("id", "")
                            domain = record.get("domain", "")
                            topic = record.get("topic", "")
                            summary = record.get("scientific_summary", "")
                            variables = record.get("key_variables", [])
                            interventions = record.get("interventions", [])

                            citations = []
                            for intervention in interventions:
                                citations.extend(intervention.get("citations", []))

                            combined_text = f"{topic} {summary} " + " ".join(variables)
                            for inv in interventions:
                                combined_text += f" {inv.get('name', '')} {inv.get('mechanism', '')}"

                            doc = KnowledgeDocument(
                                doc_id=doc_id,
                                domain=domain,
                                topic=topic,
                                content=combined_text,
                                key_variables=variables,
                                interventions=interventions,
                                citations=list(set(citations))
                            )
                            self.documents.append(doc)
                except Exception as e:
                    print(f"Warning: Failed to load {file_path}: {e}")

    def _build_index(self):
        total_docs = len(self.documents)
        if total_docs == 0:
            return

        doc_frequencies: Dict[str, int] = {}
        self.doc_term_freqs = []
        self.doc_lengths = []

        for doc in self.documents:
            tokens = self._tokenize(doc.content)
            self.doc_lengths.append(len(tokens))
            term_freq: Dict[str, int] = {}
            for token in tokens:
                term_freq[token] = term_freq.get(token, 0) + 1
            self.doc_term_freqs.append(term_freq)

            for token in set(tokens):
                doc_frequencies[token] = doc_frequencies.get(token, 0) + 1

        self.avg_doc_length = sum(self.doc_lengths) / total_docs if total_docs > 0 else 0.0

        # Compute Robertson-Spärck Jones IDF
        for token, df in doc_frequencies.items():
            self.idf[token] = math.log(1.0 + (total_docs - df + 0.5) / (df + 0.5))

    def retrieve(self, query: str, domain: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve top-k relevant scientific knowledge chunks using BM25 and keyword scoring.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens or not self.documents:
            return []

        k1 = 1.5
        b = 0.75
        scores: List[tuple[int, float]] = []

        for idx, doc in enumerate(self.documents):
            if domain and doc.domain != domain:
                continue

            score = 0.0
            doc_len = self.doc_lengths[idx]
            tf_dict = self.doc_term_freqs[idx]

            for token in query_tokens:
                if token in tf_dict:
                    tf = tf_dict[token]
                    idf_val = self.idf.get(token, 0.1)
                    numerator = tf * (k1 + 1.0)
                    denominator = tf + k1 * (1.0 - b + b * (doc_len / (self.avg_doc_length or 1.0)))
                    score += idf_val * (numerator / denominator)

            # Boost if exact variable match
            for var in doc.key_variables:
                if var in query.lower():
                    score += 2.5

            if score > 0.0:
                scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        results = []

        for doc_idx, score in scores[:top_k]:
            doc = self.documents[doc_idx]
            results.append({
                "doc_id": doc.doc_id,
                "domain": doc.domain,
                "topic": doc.topic,
                "score": round(score, 3),
                "interventions": doc.interventions,
                "citations": doc.citations,
                "key_variables": doc.key_variables
            })

        return results

    def get_all_domains(self) -> List[str]:
        return list(set(doc.domain for doc in self.documents))

    def get_all_citations(self) -> List[str]:
        citations = set()
        for doc in self.documents:
            citations.update(doc.citations)
        return sorted(list(citations))
