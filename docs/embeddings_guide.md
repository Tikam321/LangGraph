# Embeddings Guide

## What Are Embeddings?

Embeddings map **variable-length text** → **fixed-length dense vector** (e.g. 384 floats).

- Similar texts produce similar vectors (high cosine similarity)
- "dog" and "puppy" are close in vector space
- Enable semantic search, clustering, classification

## Internal Architecture

```
Input Text → Tokenizer → Embedding Layer → Transformer Encoder → Pooling → Normalize → Vector
```

### 1. Tokenizer
Splits text into subword tokens (e.g. `"stock market"` → `["stock", "mar", "##ket"]`), each mapped to a token ID. Common tokenizers: BERT WordPiece, SentencePiece.

### 2. Embedding Layer
Looks up each token ID in a learned matrix, producing a token vector (e.g. 384-dim per token). This is the first learned representation.

### 3. Transformer Encoder
The core: stacks of **self-attention** + **feed-forward** layers. Each token attends to all other tokens, producing **contextualized** vectors — `"bank"` in `"river bank"` vs `"bank loan"` get different representations.

### 4. Pooling
Collapses the sequence of token vectors into one sentence vector:
- **Mean pooling** (most common in `all-MiniLM-L6-v2`): average all token vectors
- **CLS pooling**: take the `[CLS]` special token's output (used in BERT)
- **Weighted pooling**: weighted average (used in `intfloat/e5-mistral-7b-instruct`)

### 5. Normalization
L2-normalize so all vectors lie on a unit sphere. Makes cosine similarity equivalent to dot product for ranking.

---

## How They're Trained (Contrastive Learning)

Models are fine-tuned on **triplet pairs**:

```
(query, positive_passage, negative_passage)
```

- Pull `query` vector close to `positive_passage` vector
- Push `query` vector away from `negative_passage` vector
- Loss: **InfoNCE** (Multi-class softmax over cosine similarities)

### Hard Negative Mining
Hard negatives (documents that are superficially similar but irrelevant) are used during training to improve discrimination — e.g. "What is the P/E ratio?" vs "P/E ratio was 15.2" (good) vs "P/E ratio is a metric..." (bad, too generic).

---

## Types of Embedding Models

### API-Based Models

| Model | Provider | Dims | Max Tokens | Quality | Cost |
|---|---|---|---|---|---|
| `text-embedding-3-small` | OpenAI | 512/1536 | 8191 | Very High | $0.02/1M tokens |
| `text-embedding-3-large` | OpenAI | 256-3072 | 8191 | Highest | $0.13/1M tokens |
| `embedding-001` | Google Gemini | 768 | 2048 | High | Pay-as-you-go |
| `embed-multilingual-v3` | Cohere | 1024 | 512 | High | $0.10/1K units |

### Local / Open-Source Models

| Model | Dims | Max Tokens | Quality | Size | Use Case |
|---|---|---|---|---|---|
| `all-MiniLM-L6-v2` | 384 | 256 | Good | 80MB | Fast general-purpose, English |
| `all-mpnet-base-v2` | 768 | 384 | Very Good | 420MB | Higher accuracy, English |
| `BAAI/bge-small-en-v1.5` | 384 | 512 | Good | 33MB | Lightweight retrieval |
| `BAAI/bge-base-en-v1.5` | 768 | 512 | Very Good | 130MB | Balanced retrieval |
| `BAAI/bge-large-en-v1.5` | 1024 | 512 | Excellent | 1.3GB | Highest accuracy retrieval |
| `intfloat/e5-mistral-7b-instruct` | 4096 | 4096 | SOTA | 14GB | State-of-the-art retrieval |
| `sentence-transformers/ paraphrase-multilingual-MiniLM-L12-v2` | 384 | 128 | Good | 470MB | Multilingual |

### Task-Specific Models

- **Retrieval**: `bge-*`, `e5-*`, `gte-*` — trained on `(query, passage)` pairs
- **Clustering**: `all-MiniLM-L6-v2` — trained on STS (Semantic Textual Similarity)
- **Classification**: `all-mpnet-base-v2` — balanced for classification tasks
- **Multilingual**: `intfloat/multilingual-e5-*`, `paraphrase-multilingual-MiniLM-L12-v2`

> **Key Insight**: Retrieval models (BGE, E5) are NOT always the best for clustering, and vice versa. Always pick the model by the downstream task.

---

## Comparison: API-Based vs Local Embeddings

| Aspect | API-Based (OpenAI, Google, Cohere) | Local (MiniLM, BGE, E5) |
|---|---|---|
| **Latency** | 200-500ms per call (network round-trip) | 1-5ms per call (in-memory) |
| **Throughput** | Limited by rate limits (e.g. 60 req/min tier 1) | Unlimited — bounded only by CPU/GPU |
| **Cost** | Pay-per-token (can be significant at scale) | Free after one-time download |
| **Dimension** | 768-3072 | 384-4096 |
| **Quality** | Very High to Highest | Good to SOTA (7B models match API) |
| **Data Privacy** | Data sent to third-party API | Data stays local |
| **Maintenance** | Zero — provider manages infrastructure | You manage model downloads, cache, updates |
| **Scalability** | Scales with cloud budget | Scales with your hardware |
| **Multilingual** | Built-in (most support 100+ languages) | Variable — need specific multilingual model |
| **Context Window** | 2048-8191 tokens | 128-512 tokens (most mini models) |

---

## Production Use Cases

### SaaS / Cloud Production → API-Based (OpenAI, Google)

**Why**: Managed infrastructure, no GPU/dependency overhead, consistent performance, same provider as your LLM.

```python
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
```

**Good for**: Customer-facing chatbots, multi-tenant apps, teams without dedicated ML infra.

### High-Throughput / On-Prem → Local (BGE, E5)

**Why**: Sub-ms latency at scale, no API costs, data never leaves your network.

```python
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
```

**Good for**: Document processing pipelines (millions of pages/day), air-gapped environments, privacy-sensitive data.

### Hybrid Pattern (Common)

| Stage | Embedding Model | Reason |
|---|---|---|
| Development | `all-MiniLM-L6-v2` | Fast, free, no rate limits |
| Staging | `text-embedding-3-small` | Match production API behavior |
| Production | `text-embedding-3-large` / `bge-large-en-v1.5` | Best quality, chosen by cost/privacy |

### Which to Use When

| Scenario | Recommended Model | Why |
|---|---|---|
| Prototype / POC | `all-MiniLM-L6-v2` | Zero cost, instant setup |
| English RAG app | `BAAI/bge-base-en-v1.5` | Best quality-to-size ratio for retrieval |
| Multilingual RAG | `intfloat/multilingual-e5-large` | SOTA multilingual retrieval |
| Cost-sensitive, large scale | `text-embedding-3-small` (API) or `BAAI/bge-small-en-v1.5` (local) | Cheapest per document |
| Maximum accuracy | `text-embedding-3-large` (API) or `intfloat/e5-mistral-7b-instruct` (local) | Highest quality |
| No GPU, no API budget | `all-MiniLM-L6-v2` | Runs on CPU in milliseconds |
| Enterprise, data privacy | `BAAI/bge-base-en-v1.5` or `e5-mistral-7b-instruct` | Self-hosted, data stays local |

---

## Chunking + Embedding Pipeline (RAG)

```
PDF Document
      │
      ▼
Text Splitter (RecursiveCharacterTextSplitter)
   chunk_size=500, chunk_overlap=50
      │
      ├── Chunk 1: "Q1 earnings rose 15%..."
      ├── Chunk 2: "driven by strong sales..."
      ├── Chunk 3: "in the Asia-Pacific region..."
      │
      ▼
Embedding Model
      │
      ├── Chunk 1 → [0.23, -0.45, ..., 0.89]  (384-dim)
      ├── Chunk 2 → [0.21, -0.42, ..., 0.12]
      ├── Chunk 3 → [0.19, -0.44, ..., 0.91]
      │
      ▼
Vector Store (Chroma)
      │
      ▼ (Query time)
"Which region drove growth?"
      │
      ▼
Query embedding → [0.20, -0.43, ..., 0.88]
      │
      ▼
Cosine similarity with all stored vectors
      │
      ├── Chunk 1: 0.91  ← top match (driven by strong sales)
      ├── Chunk 2: 0.85
      ├── Chunk 3: 0.79
      │
      ▼
Return top-k chunks to LLM
```

---

## Our Setup

| Component | Choice | Why |
|---|---|---|
| **Embedding Model** | `all-MiniLM-L6-v2` (384-dim) | Free, fast, CPU-friendly, no API quota |
| **Library** | `langchain-huggingface` + `sentence-transformers` | Clean integration with LangChain ecosystem |
| **Vector Store** | Chroma (SQLite persistence) | Local, no external DB needed |
| **LLM** | `gemini-2.5-flash-lite` (Google Gemini) | Handles summary/generation from retrieved chunks |
| **Chunk Size** | 500 chars, overlap 50 | Balances granularity with context coherence |

### Why `all-MiniLM-L6-v2` Specifically

- **384 dims** → compact storage, fast search (vs 768-3072 for API models)
- **80MB** → downloads in seconds, runs on any laptop
- **~5ms per chunk** on CPU → no GPU required
- **Good enough quality** for English document retrieval
- **Zero cost**, unlimited throughput
- No external API dependency, rate limits, or quota issues

---

## Key Takeaways

1. **Dimensionality matters**: Higher dims capture more nuance but cost more in storage + search speed. 384 is fine for most use cases.
2. **Model must match task**: A retrieval model (BGE, E5) outperforms a generic model (MiniLM) for RAG, but not necessarily for clustering.
3. **Chunk size affects quality**: Too small → lost context. Too large → diluted signal. 500 chars with overlap is a good default.
4. **Normalization is crucial**: Always L2-normalize if using cosine similarity (most modern models do this by default).
5. **Production = tradeoff**: API for simplicity, local for cost/privacy/latency. Many teams use both (local in dev, API in prod, or vice versa).
