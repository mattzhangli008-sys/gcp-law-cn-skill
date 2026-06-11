---
name: gcp-regulations-qa
description: Use this skill to answer Chinese GCP, clinical trial, clinical trial drug, drug registration, pharmacovigilance, ethics, institution management, and related NMPA/SAMR/MOJ regulation questions from a bundled local Chroma RAG library. Use when the user asks for法规依据, 条款出处, GCP法规问答, 临床试验法规解释, or wants cited answers based on the downloaded regulation documents.
---

# GCP Regulations QA

## Purpose

Answer GCP and clinical-trial regulation questions using the bundled local Chroma RAG database in `assets/rag_chroma`. The library contains 32 downloaded regulation source files split into 466 chunks with metadata for title, authority, release/effective dates, official URL, download URL, page/paragraph, article number, and `chunk_id`.

## Quick Workflow

1. Retrieve evidence before answering:

```bash
python3.12 scripts/query_gcp_rag.py "用户的问题" -n 6
```

If `python3.12` lacks dependencies, use the project venv if available or create one with:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt
.venv/bin/python scripts/query_gcp_rag.py "用户的问题" -n 6
```

2. Use only retrieved evidence for法规依据. Do not invent article numbers, dates, or authorities.

3. Answer in Chinese unless the user asks otherwise. Keep regulatory conclusions cautious: distinguish mandatory language such as “应当/不得/必须” from explanatory interpretation.

4. Include sources after the answer. Preferred format:

```text
依据：
1. 《法规名称》 第三十一条，国家药品监督管理局，2022-05-27，chunk:19-0005，官方链接：https://...
2. 《法规名称》 第5页，国家市场监督管理总局，2020-01-22，chunk:3-0004，官方链接：https://...
```

Always include a source link in each cited item. Prefer `official_url`; if it is empty, use `download_url` and label it as the source file/download link.

## Evidence Rules

- If retrieved chunks conflict, explain the conflict and cite both sources.
- If the question asks for exact obligations, quote or closely paraphrase the specific article text and cite the chunk.
- If the RAG results are weak or unrelated, say the bundled法规库 did not retrieve sufficient evidence and ask whether to broaden the search or inspect original files.
- If the user provides only the Chroma library in a future workspace, source citations still come from Chroma metadata. Original files are not required for ordinary Q&A, but are needed for re-chunking, page-image verification, or rebuilding the database.
- Each answer's `依据` section must include the regulation title, location/article if available, authority, publication date, `chunk_id`, and official/source link.

## Bundled Files

- `assets/rag_chroma/`: persistent Chroma database.
- `assets/rag_manifest.json`: document/chunk counts and metadata schema.
- `references/source_documents.csv`: original download report and document-level source metadata.
- `scripts/query_gcp_rag.py`: retrieval CLI with lightweight keyword reranking.
- `scripts/rag_embeddings.py`: deterministic local embedding function required to query this database.
- `requirements.txt`: Python runtime dependencies for querying the bundled Chroma database.
