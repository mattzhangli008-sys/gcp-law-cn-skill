#!/usr/bin/env python3.12
import argparse
import re
from pathlib import Path

import chromadb

from rag_embeddings import HashNgramEmbeddingFunction


ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = ROOT / "assets" / "rag_chroma"
COLLECTION = "gcp_regulations"


def query_terms(question: str) -> list[str]:
    compact = re.sub(r"\s+", "", question)
    terms = set()
    for m in re.finditer(r"第[一二三四五六七八九十百千万零〇\d]+条", compact):
        terms.add(m.group(0))
    for n in (4, 3, 2):
        for i in range(0, max(0, len(compact) - n + 1)):
            token = compact[i : i + n]
            if re.search(r"[\u4e00-\u9fff]", token):
                terms.add(token)
    stop = {"哪些", "什么", "如何", "是否", "应当", "需要", "进行", "关于", "法规"}
    return [t for t in terms if t not in stop]


def rerank_score(question_terms: list[str], doc: str, meta: dict, distance: float) -> float:
    haystack = f"{meta.get('title', '')}{meta.get('article_no', '')}{meta.get('section_title', '')}{doc}"
    hits = sum(1 for term in question_terms if term in haystack)
    title_hits = sum(1 for term in question_terms if term in meta.get("title", ""))
    article_hits = sum(1 for term in question_terms if term in meta.get("article_no", ""))
    return hits * 2.0 + title_hits * 3.0 + article_hits * 4.0 - distance


def source_label(meta: dict) -> str:
    loc = ""
    if meta.get("page_start"):
        loc = f"第{meta['page_start']}页"
        if meta.get("page_end") and meta["page_end"] != meta["page_start"]:
            loc = f"第{meta['page_start']}-{meta['page_end']}页"
    elif meta.get("article_no"):
        loc = meta["article_no"]
    elif meta.get("paragraph_start"):
        loc = f"段落{meta['paragraph_start']}"
    pieces = [f"《{meta.get('title', '')}》"]
    if loc:
        pieces.append(loc)
    if meta.get("authority"):
        pieces.append(meta["authority"])
    if meta.get("published"):
        pieces.append(f"发布:{meta['published']}")
    pieces.append(f"chunk:{meta.get('chunk_id', '')}")
    link = meta.get("official_url") or meta.get("download_url") or ""
    if link:
        pieces.append(f"官方链接:{link}")
    return "，".join(pieces)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("-n", "--n-results", type=int, default=5)
    args = parser.parse_args()

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(name=COLLECTION, embedding_function=HashNgramEmbeddingFunction())
    result = collection.query(query_texts=[args.question], n_results=max(args.n_results * 5, 20))
    terms = query_terms(args.question)
    rows = list(zip(result["documents"][0], result["metadatas"][0], result["distances"][0]))
    rows.sort(key=lambda row: rerank_score(terms, row[0], row[1], row[2]), reverse=True)

    for rank, (doc, meta, dist) in enumerate(rows[: args.n_results], start=1):
        print(f"\n[{rank}] distance={dist:.4f}")
        print(source_label(meta))
        print("-" * 80)
        preview = doc.strip().replace("\n\n", "\n")
        print(preview[:900])


if __name__ == "__main__":
    main()
