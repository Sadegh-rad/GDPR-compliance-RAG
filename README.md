# GDPR Compliance Assistant 🛡️

A smart AI assistant that helps you understand and comply with GDPR regulations. Ask questions in plain English and get accurate answers backed by official GDPR sources.

## What Does It Do?

- **Answer GDPR Questions**: Ask anything about GDPR and get detailed, accurate answers
- **Check Compliance**: Describe your data practice and get instant risk assessment
- **Find Violations**: Automatically detect GDPR violations with highlighted text and exact GDPR citations
- **Cite Sources**: Every answer includes references to specific GDPR articles with quoted text
- **Verify Findings**: Professional reports with verification steps for compliance officers

## ✨ New Features

### Enhanced Violation Detection
- **🔴 Text Highlighting**: Directly quotes problematic text from your documents
- **📚 Source Citations**: Cites specific GDPR Articles/Recitals with exact quotes
- **✓ Verification**: Provides context for lawyers and compliance officers to verify findings

[Learn more about enhanced violations →](docs/ENHANCED_VIOLATIONS_GUIDE.md)

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Make Sure Ollama is Running

The system uses Ollama for AI responses. Check it's running:

```bash
curl http://localhost:11434/api/tags
```

If not installed, get it from [ollama.ai](https://ollama.ai)

### 3. Build the GDPR Database (First Time Only)

This takes 2-3 minutes and collects official GDPR text:

```bash
# Quick English-only database
python main.py collect --sources eur-lex --languages EN
python main.py process
python main.py build
```

### 4. Start Using It!

**Ask a Question:**
```bash
python main.py query --query "What are data subject rights?"
```

**Interactive Chat:**
```bash
python main.py interactive
```

**Check for Violations:**
```bash
python main.py analyze --scenario "We collect emails without consent" --output report.md
```

## Example Questions You Can Ask

- "What is the right to be forgotten?"
- "When do I need a Data Protection Officer?"
- "What are the lawful bases for processing data?"
- "What are the GDPR penalties?"
- "How should we handle data breaches?"

## How It Works

1. **Collect**: Downloads official GDPR regulation text from EUR-Lex
2. **Process**: Breaks text into smart chunks with context
3. **Index**: Creates searchable vector database (876 chunks, 55K words)
4. **Query**: Finds relevant GDPR sections and generates answers using AI

## What's Inside?

```
📁 Your Project
├── 📄 main.py              # Main command interface
├── 📄 config.yaml          # Settings (model, embeddings, etc.)
├── 📄 requirements.txt     # Python dependencies
├── 📁 src/                 # Source code
│   ├── data_collection/    # Scrapes GDPR sources
│   ├── preprocessing/      # Processes documents
│   ├── vectorstore/        # FAISS vector database
│   ├── rag/               # AI question answering
│   └── violation_finder/   # Compliance checker
├── 📁 data/               # Downloaded GDPR data
├── 📁 vectorstore/        # Searchable index
└── 📁 docs/               # Documentation
```

## Configuration

Edit `config.yaml` to customize:

```yaml
# AI Model
ollama:
  model: "gpt-oss:latest"
  temperature: 0.05  # Lower = more factual

# Embeddings (semantic search)
embeddings:
  model_name: "sentence-transformers/all-mpnet-base-v2"
  
# Search Settings
retrieval:
  top_k: 7                # How many sources to find
  score_threshold: 0.45   # Minimum relevance score
```

## Commands

| Command | What It Does |
|---------|-------------|
| `python main.py query --query "your question"` | Ask a single question |
| `python main.py interactive` | Start chat mode |
| `python main.py analyze --scenario "..."` | Check compliance |
| `python main.py collect` | Download GDPR data |
| `python main.py process` | Process documents |
| `python main.py build` | Build search index |

## Features

- ✅ **Accurate**: Uses official GDPR sources only
- ✅ **Smart**: 768-dimensional semantic search
- ✅ **Fast**: Sub-second search, ~30s answers
- ✅ **Honest**: Says "I don't know" instead of making things up
- ✅ **Cited**: Shows exact GDPR articles and recitals
- ✅ **Comprehensive**: 876 indexed chunks covering full GDPR

## System Info

- **Database**: 876 chunks from GDPR Regulation (EU) 2016/679
- **Coverage**: 99 articles, 173 recitals (English)
- **AI Model**: gpt-oss:latest via Ollama
- **Search**: FAISS with 768-dim embeddings
- **Quality**: Anti-hallucination safeguards enabled

## Troubleshooting

**"No module named..."**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"Index not found"**
```bash
# Build the database first
python main.py collect --sources eur-lex --languages EN
python main.py process
python main.py build
```

**"Ollama connection failed"**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

## Expand the Database

Want more sources? Add EDPB guidelines and case law:

```bash
# Full collection (takes 30-60 minutes)
python main.py collect --sources all --languages EN,DE,FR
python main.py process
python main.py build
```

## Python API

Use it in your own code:

```python
import yaml
from src.rag.gdpr_rag import GDPRRAGSystem

# Load config
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Initialize
rag = GDPRRAGSystem(config)

# Ask question
result = rag.query("What are data subject rights?")
print(result['answer'])
```

## Need Help?

- 📖 **Getting Started**: See `docs/GETTING_STARTED.md`
- 🔧 **API Guide**: See `docs/technical/API_GUIDE.md`
- 📚 **Quick Reference**: See `docs/QUICK_REFERENCE.md`

## License

This project is for GDPR compliance assistance. The GDPR regulation text is public domain from EUR-Lex.

## Technical Notes

- **No Internet Needed**: After building database, works offline
- **Private**: All data stays on your machine
- **Customizable**: Easy to add more sources or change models
- **Production Ready**: Anti-hallucination safeguards, source citations, honest about limitations

---

**Built with:** Python, Ollama, FAISS, Sentence Transformers, LangChain

**Status:** ✅ Production Ready | **Quality:** Professional Grade | **Accuracy:** High (Anti-Hallucination Enabled)
