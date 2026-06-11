# gcp-law-cn-skill

中国 GCP/临床试验法规问答 Codex skill。该 skill 内置本地 Chroma RAG 库，可围绕药物临床试验、临床试验用药品、伦理审查、机构管理、药品注册、药物警戒等法规问题进行检索式回答，并在答案中给出可追溯来源。

## 内容

- 32 份中国临床试验相关法规/规范性文件
- 466 个法规文本 chunk
- 本地 Chroma 持久化数据库
- 离线、确定性的中文 n-gram embedding 函数
- 查询脚本和来源明细

## 目录结构

```text
.
├── SKILL.md
├── agents/openai.yaml
├── assets/
│   ├── rag_chroma/
│   └── rag_manifest.json
├── references/
│   └── source_documents.csv
├── scripts/
│   ├── query_gcp_rag.py
│   └── rag_embeddings.py
└── requirements.txt
```

## 安装依赖

推荐使用 Python 3.12。

```bash
python3.12 -m venv .venv
.venv/bin/pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt
```

## 使用

在仓库根目录运行：

```bash
.venv/bin/python scripts/query_gcp_rag.py "伦理变更流程" -n 6
```

输出会包含：

- 命中的法规片段
- 法规名称
- 页码、段落或条款号
- 发布机构和发布日期
- chunk id
- 官方链接或来源文件链接

## 在 Codex 中使用

安装/启用该 skill 后，可以直接询问：

```text
$gcp-regulations-qa 伦理批件需要哪些规范？
$gcp-regulations-qa 临床试验用药品标签应当包含哪些内容？
$gcp-regulations-qa 药物临床试验机构需要具备哪些条件？
```

回答应基于检索证据，并在“依据”部分列出来源，例如：

```text
依据：
1. 《临床试验用药品附录（试行）》第三十九条，国家药品监督管理局，2022-05-27，chunk:19-0008，官方链接：https://...
```

## 数据来源

法规清单来源于 AIINCT 法规文档页面，并逐条下载/补充官方或公开来源文件。文档级来源信息保存在：

```text
references/source_documents.csv
```

RAG 库中的每个 chunk 均包含 metadata，包括：

- `title`
- `authority`
- `published`
- `effective`
- `official_url`
- `download_url`
- `page_start` / `page_end`
- `paragraph_start` / `paragraph_end`
- `article_no`
- `chunk_id`

## 重要说明

该 skill 的检索库可独立于原始 Word/PDF 文件使用。只要保留 `assets/rag_chroma`，问答时仍可从 Chroma metadata 中给出来源。

当前 embedding 使用本地哈希 n-gram 方法，优点是离线、轻量、可复现；缺点是语义泛化不如专业 embedding 模型。后续可以在保持 metadata 结构不变的情况下替换为 BGE、OpenAI embeddings 或其他医学/中文法规 embedding 模型。

## 合规提示

该 skill 仅用于法规检索、学习和辅助分析，不替代法律、注册、伦理委员会或监管部门的正式意见。涉及实际临床试验启动、变更、暂停、终止或申报事项时，应以官方法规文本、监管要求和机构 SOP 为准。
