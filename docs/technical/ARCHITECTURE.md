# GDPR RAG System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GDPR RAG SYSTEM                               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     DATA COLLECTION LAYER                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ EUR-Lex  │  │   EDPB   │  │ GDPRhub  │  │   CJEU   │           │
│  │          │  │          │  │          │  │          │           │
│  │ Official │  │Guidelines│  │Case Law  │  │ Court    │           │
│  │   GDPR   │  │& Guides  │  │Database  │  │Decisions │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │             │             │             │                   │
│       └─────────────┴─────────────┴─────────────┘                   │
│                            │                                         │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT PROCESSING LAYER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              Document Processor                             │    │
│  ├────────────────────────────────────────────────────────────┤    │
│  │                                                              │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │    │
│  │  │  Structure   │  │    Smart     │  │   Metadata   │    │    │
│  │  │ Preservation │  │   Chunking   │  │  Enrichment  │    │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │    │
│  │                                                              │    │
│  │  • Preserve Articles, Recitals, Sections                   │    │
│  │  • Context-aware chunking with overlap                      │    │
│  │  • Violation category tagging                               │    │
│  │  • Legal structure metadata                                 │    │
│  └────────────────────────────────────────────────────────────┘    │
│                            │                                         │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EMBEDDING & INDEXING LAYER                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │            Sentence Transformers                           │     │
│  │     (all-MiniLM-L6-v2 or multilingual variant)           │     │
│  └─────────────────────────┬─────────────────────────────────┘     │
│                            │                                         │
│                            ▼                                         │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │                  FAISS Vector Index                        │     │
│  │              (HNSW for fast search)                        │     │
│  ├───────────────────────────────────────────────────────────┤     │
│  │                                                             │     │
│  │  5,000 - 20,000 vectors (384 dimensions)                  │     │
│  │  • Metadata filtering                                       │     │
│  │  • Semantic similarity search                               │     │
│  │  • <100ms query time                                        │     │
│  └───────────────────────────────────────────────────────────┘     │
│                            │                                         │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RETRIEVAL LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Query → Embed → Search FAISS → Filter → Rank → Top-K Results      │
│                                                                       │
│  Features:                                                            │
│  • Semantic search across all documents                              │
│  • Metadata filtering (source, article, category)                    │
│  • Score threshold filtering                                         │
│  • Optional reranking                                                │
│                                                                       │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GENERATION LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │                    Ollama LLM                              │     │
│  │          (Llama2, Mistral, or other models)               │     │
│  ├───────────────────────────────────────────────────────────┤     │
│  │                                                             │     │
│  │  Input: Query + Retrieved Context + System Prompt         │     │
│  │  Output: Contextualized Answer with Citations             │     │
│  │                                                             │     │
│  │  Features:                                                  │     │
│  │  • Local inference (privacy-preserving)                    │     │
│  │  • Customizable prompts                                     │     │
│  │  • Temperature control                                      │     │
│  │  • Source attribution                                       │     │
│  └───────────────────────────────────────────────────────────┘     │
│                            │                                         │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐       │
│  │   Q&A System   │  │   Violation    │  │     Risk       │       │
│  │                │  │     Finder     │  │   Assessment   │       │
│  ├────────────────┤  ├────────────────┤  ├────────────────┤       │
│  │                │  │                │  │                │       │
│  │ • Interactive  │  │ • Identify     │  │ • Risk scoring │       │
│  │ • Batch query  │  │   violations   │  │ • Severity     │       │
│  │ • Filtered     │  │ • Categorize   │  │   levels       │       │
│  │   search       │  │ • Recommend    │  │ • Compliance   │       │
│  │ • Multi-lang   │  │   remediation  │  │   reports      │       │
│  └────────────────┘  └────────────────┘  └────────────────┘       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      INTERFACE LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │   CLI    │  │  Python  │  │   REST   │  │   Web    │           │
│  │          │  │   API    │  │   API    │  │    UI    │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Data Collection Flow
```
External Sources → HTTP Requests → HTML/JSON Parsing → 
Structured Extraction → JSON Storage → Raw Data Directory
```

### 2. Processing Flow
```
Raw JSON → Document Parser → Structure Analyzer → 
Chunking Engine → Metadata Tagger → Processed Chunks → 
JSON Storage
```

### 3. Indexing Flow
```
Processed Chunks → Text Extraction → Batch Processing → 
Sentence Transformer → Embeddings (384D) → 
FAISS Index + Metadata Store → Disk Storage
```

### 4. Query Flow
```
User Query → Query Embedding → FAISS Search → 
Score Filtering → Metadata Filtering → Top-K Selection → 
Context Assembly → LLM Generation → Response + Sources
```

### 5. Violation Detection Flow
```
Scenario → Relevant Document Retrieval → 
Context Assembly → Violation Analysis Prompt → 
LLM Processing → Structured Extraction → 
Risk Scoring → Compliance Report
```

## Component Interaction

```
┌──────────────┐
│     User     │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     CLI      │────▶│   RAG Core   │────▶│ Vector Store │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Retriever  │     │  Generator   │     │   Metadata   │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                            │
                            ▼
                      ┌──────────────┐
                      │   Response   │
                      └──────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────┐
│          Application Layer                   │
│  Python 3.8+, Click, Loguru                 │
├─────────────────────────────────────────────┤
│          RAG & NLP Layer                     │
│  Ollama, Sentence Transformers              │
├─────────────────────────────────────────────┤
│          Vector Store Layer                  │
│  FAISS, NumPy                               │
├─────────────────────────────────────────────┤
│          Data Processing Layer               │
│  Pandas, BeautifulSoup4, JSON               │
├─────────────────────────────────────────────┤
│          Infrastructure Layer                │
│  Requests, PyYAML, Pydantic                 │
└─────────────────────────────────────────────┘
```

## Deployment Architecture

### Local Development
```
┌──────────────────────────────────────┐
│        Developer Machine             │
│  ┌────────────┐    ┌──────────────┐ │
│  │   Ollama   │    │  GDPR RAG    │ │
│  │  (Port     │◀───│   System     │ │
│  │   11434)   │    │              │ │
│  └────────────┘    └──────────────┘ │
│                                      │
│  ┌────────────────────────────────┐ │
│  │      FAISS Index Files         │ │
│  └────────────────────────────────┘ │
└──────────────────────────────────────┘
```

### Production (Future)
```
┌──────────────────────────────────────────┐
│           Load Balancer                   │
└──────────────┬───────────────────────────┘
               │
    ┌──────────┴──────────┬───────────┐
    │                     │           │
    ▼                     ▼           ▼
┌─────────┐         ┌─────────┐  ┌─────────┐
│ API     │         │ API     │  │ API     │
│ Server 1│         │ Server 2│  │ Server 3│
└────┬────┘         └────┬────┘  └────┬────┘
     │                   │            │
     └───────────────────┴────────────┘
                         │
                         ▼
              ┌─────────────────┐
              │ Shared Vector   │
              │     Store       │
              └─────────────────┘
```

## Performance Optimization

```
┌──────────────────────────────────────┐
│     Query Performance                 │
│                                       │
│  Cache Layer (Redis)                 │
│         ↓                             │
│  Embedding Cache                      │
│         ↓                             │
│  FAISS HNSW Index                    │
│         ↓                             │
│  Metadata Filter                      │
│         ↓                             │
│  Result Reranking                     │
│         ↓                             │
│  LLM Generation (Ollama)             │
│                                       │
│  Total: <5 seconds                    │
└──────────────────────────────────────┘
```

## Security Layers

```
┌──────────────────────────────────────┐
│   Input Validation                    │
├──────────────────────────────────────┤
│   Query Sanitization                  │
├──────────────────────────────────────┤
│   Rate Limiting                       │
├──────────────────────────────────────┤
│   Access Control (Future)             │
├──────────────────────────────────────┤
│   Audit Logging                       │
├──────────────────────────────────────┤
│   Data Encryption at Rest             │
└──────────────────────────────────────┘
```

## Monitoring & Logging

```
Application Logs (Loguru)
         │
         ├─→ Console Output
         ├─→ File Logs (Rotating)
         └─→ Error Tracking
         
Query Analytics
         │
         ├─→ Response Times
         ├─→ Success Rates
         ├─→ Popular Queries
         └─→ Resource Usage
```

---

This architecture provides:
- ✅ High accuracy through quality data sources
- ✅ Fast retrieval with FAISS indexing
- ✅ Privacy-preserving local LLM inference
- ✅ Scalable design for future enhancements
- ✅ Modular components for easy maintenance
