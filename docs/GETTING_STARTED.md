# GDPR RAG System - Getting Started Guide

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] At least 4GB RAM available
- [ ] 2GB free disk space
- [ ] Stable internet connection (for data collection)
- [ ] Ollama installed

## Step-by-Step Setup

### 1. Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download and install from https://ollama.ai/download

### 2. Pull an Ollama Model

Choose one based on your system:

**For 8GB+ RAM (Recommended):**
```bash
ollama pull llama2
```

**For 4-8GB RAM:**
```bash
ollama pull mistral
```

**For 16GB+ RAM (Best Quality):**
```bash
ollama pull llama2:13b
```

### 3. Start Ollama

```bash
ollama serve
```

Leave this running in a terminal.

### 4. Setup Python Environment

```bash
# Navigate to project directory
cd GDPR-compliance-RAG

# Run setup script
chmod +x setup.sh
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Configure the System

Edit `config.yaml` if needed:

```yaml
ollama:
  model: "llama2"  # Change to your downloaded model
  
embeddings:
  device: "cpu"    # Change to "cuda" if you have GPU
```

### 6. Build the Database

This will take 15-30 minutes:

```bash
python main.py setup
```

This command will:
1. Collect GDPR data from official sources
2. Process and chunk documents
3. Generate embeddings
4. Build FAISS index

**Progress Indicators:**
- Data collection: ~10-15 minutes
- Document processing: ~2-5 minutes
- Vector store building: ~5-10 minutes

### 7. Verify Installation

Test with a simple query:

```bash
python main.py query --query "What are data subject rights?"
```

Expected output:
```
Query: What are data subject rights?
================================================================================

Answer:
Under GDPR, data subjects have the following rights:
...
```

## Quick Commands

### Interactive Mode
```bash
python main.py interactive
```

### Single Query
```bash
python main.py query --query "Your question here"
```

### Analyze Scenario
```bash
python main.py analyze --scenario "Describe your scenario" --output report.md
```

### Run Examples
```bash
python examples.py --example 1
```

## Common Issues

### Issue: Ollama connection refused
**Solution:** Make sure Ollama is running with `ollama serve`

### Issue: Out of memory
**Solution:** 
- Use a smaller model: `ollama pull mistral`
- Reduce batch_size in config.yaml
- Close other applications

### Issue: Slow embeddings
**Solution:**
- Enable GPU if available: set `device: "cuda"` in config.yaml
- Use a smaller embedding model in config.yaml

### Issue: Poor answer quality
**Solution:**
- Use a larger Ollama model
- Increase `top_k` in config.yaml
- Rebuild the index with better embeddings

## Next Steps

1. **Explore Examples**
   ```bash
   python examples.py
   ```

2. **Try Different Queries**
   - "What is a Data Protection Impact Assessment?"
   - "When do I need to appoint a DPO?"
   - "What are the penalties for GDPR violations?"

3. **Analyze Compliance Scenarios**
   ```bash
   python main.py analyze --scenario "We collect user data without explicit consent"
   ```

4. **Customize Configuration**
   - Edit `config.yaml` to adjust models, parameters
   - Add/remove data sources
   - Modify chunk sizes and retrieval settings

## Tips for Best Results

1. **Be Specific**: Ask detailed questions for better answers
   - ❌ "Tell me about GDPR"
   - ✅ "What are the requirements for obtaining valid consent under Article 7?"

2. **Use Filters**: Filter by source or article for targeted results
   ```python
   rag.query("consent requirements", filters={"article_number": "7"})
   ```

3. **Provide Context**: Include relevant details in violation analysis
   - ❌ "Check if we're compliant"
   - ✅ "We collect customer emails and phone numbers for marketing. Users check a box during registration. We store data for 5 years. Are we compliant?"

4. **Review Sources**: Always check the sources cited in responses

## Getting Help

- Check logs: `logs/gdpr_rag.log`
- Read README.md for detailed documentation
- Review examples.py for usage patterns

## System Requirements Summary

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 4GB | 8GB+ |
| Disk | 2GB | 5GB+ |
| CPU | 2 cores | 4+ cores |
| Python | 3.8 | 3.10+ |

## Troubleshooting Checklist

If something isn't working:

- [ ] Is Ollama running? (`curl http://localhost:11434/api/tags`)
- [ ] Is the virtual environment activated? (`which python`)
- [ ] Are all dependencies installed? (`pip list`)
- [ ] Is the FAISS index built? (check `vectorstore/` directory)
- [ ] Are there processed chunks? (check `data/processed/`)
- [ ] Check logs for errors (`logs/gdpr_rag.log`)

---

**Ready to start?** Run `python main.py interactive` and ask your first question!
