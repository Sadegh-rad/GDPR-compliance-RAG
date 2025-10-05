# GDPR RAG System - Quick Reference

## Installation
```bash
# Clone and setup
git clone <repo-url>
cd GDPR-compliance-RAG
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install and start Ollama
ollama serve
ollama pull llama2

# Build database (15-30 min)
python main.py setup
```

## Commands

| Command | Description |
|---------|-------------|
| `python main.py setup` | Complete system setup |
| `python main.py collect` | Collect GDPR data |
| `python main.py process` | Process documents |
| `python main.py build` | Build vector store |
| `python main.py interactive` | Interactive Q&A |
| `python main.py query --query "..."` | Single query |
| `python main.py analyze --scenario "..."` | Violation analysis |

## Python API

### Basic Query
```python
from rag.gdpr_rag import GDPRRAGSystem
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

rag = GDPRRAGSystem(config)
result = rag.query("What are data subject rights?")
print(result['answer'])
```

### Violation Detection
```python
from violation_finder.violation_finder import GDPRViolationFinder

finder = GDPRViolationFinder(config)
assessment = finder.analyze_scenario("We collect emails without consent")

print(f"Risk: {assessment.overall_risk_level}")
print(f"Violations: {len(assessment.violations)}")
```

## Common Queries

| Query Type | Example |
|------------|---------|
| Rights | "What are the rights of data subjects?" |
| Legal Basis | "What is the legal basis for processing?" |
| Consent | "What are valid consent requirements?" |
| DPO | "When must I appoint a DPO?" |
| DPIA | "When is a DPIA required?" |
| Breach | "What are breach notification requirements?" |
| Penalties | "What are the penalties for violations?" |
| Transfer | "How can I transfer data outside EU?" |

## Configuration Quick Reference

```yaml
# config.yaml essentials

ollama:
  model: "llama2"        # or "mistral", "llama2:13b"
  temperature: 0.1       # 0-1, lower = more factual

embeddings:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  device: "cpu"          # or "cuda" for GPU

retrieval:
  top_k: 5              # results to retrieve
  score_threshold: 0.7   # min similarity score

text_processing:
  chunk_size: 1000       # characters per chunk
  chunk_overlap: 200     # context overlap
```

## Filters

```python
# Filter by article
rag.query("consent requirements", filters={"article_number": "7"})

# Filter by source
rag.query("guidelines", filters={"source": "EDPB"})

# Filter by document type
rag.query("case law", filters={"document_type": "case_law"})

# Multiple filters
rag.query("query", filters={
    "source": "EUR-Lex",
    "article_number": "6",
    "language": "EN"
})
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Ollama connection error | Run `ollama serve` |
| Index not found | Run `python main.py build` |
| Out of memory | Use smaller model or reduce batch_size |
| Slow responses | Use faster model (mistral) or GPU |
| Poor answers | Increase top_k or use larger model |

## File Structure

```
GDPR-compliance-RAG/
├── config.yaml         # Configuration
├── main.py            # CLI interface
├── examples.py        # Usage examples
├── src/               # Source code
├── data/              # Collected data
├── vectorstore/       # FAISS index
└── logs/              # System logs
```

## Performance Tips

| Goal | Action |
|------|--------|
| Faster | Smaller model, lower top_k, use GPU |
| Better quality | Larger model, higher top_k |
| Less memory | Smaller model, lower batch_size |
| More sources | Enable in config.yaml |

## Example Scenarios

### Privacy Policy Review
```python
policy = "Our privacy policy text..."
finder.analyze_scenario(policy)
```

### Data Processing Check
```python
scenario = "We process employee health data for insurance"
assessment = finder.analyze_scenario(scenario)
```

### Compliance Report
```python
report = finder.generate_compliance_report(
    scenario, assessment, format="markdown"
)
```

## Keyboard Shortcuts (Interactive Mode)

- `Ctrl+C` or type `quit`: Exit
- `Ctrl+D`: Exit
- Just press Enter: Continue

## Environment Variables

```bash
export OLLAMA_HOST="http://localhost:11434"
export CUDA_VISIBLE_DEVICES="0"  # For GPU
```

## System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4GB | 8GB+ |
| Disk | 2GB | 5GB+ |
| CPU | 2 cores | 4+ cores |

## Model Comparison

| Model | Size | Speed | Quality | RAM |
|-------|------|-------|---------|-----|
| mistral | 7B | Fast | Good | 4GB |
| llama2 | 7B | Medium | Good | 6GB |
| llama2:13b | 13B | Slow | Better | 10GB |

## Quick Checks

```bash
# Is Ollama running?
curl http://localhost:11434/api/tags

# Is index built?
ls vectorstore/*.faiss

# Check logs
tail -f logs/gdpr_rag.log

# System info
python -c "from rag.gdpr_rag import GDPRRAGSystem; import yaml; config = yaml.safe_load(open('config.yaml')); rag = GDPRRAGSystem(config); print(rag.get_system_info())"
```

## Documentation Files

- `README.md` - Full documentation
- `GETTING_STARTED.md` - Setup guide
- `API_GUIDE.md` - API reference
- `DATA_SOURCES.md` - Data sources info
- `PROJECT_SUMMARY.md` - Project overview

## Support

1. Check documentation
2. Run examples: `python examples.py`
3. Check logs: `logs/gdpr_rag.log`
4. GitHub issues

---

**Quick Start**: `python main.py setup && python main.py interactive`
