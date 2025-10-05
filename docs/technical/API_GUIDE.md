# API Usage Guide

This guide shows how to use the GDPR RAG system as a Python library in your applications.

## Installation

```python
# Add the src directory to your Python path
import sys
from pathlib import Path
sys.path.append(str(Path('/path/to/GDPR-compliance-RAG/src')))
```

Or install as a package:
```bash
pip install -e /path/to/GDPR-compliance-RAG
```

## Basic Usage

### 1. Initialize the System

```python
import yaml
from rag.gdpr_rag import GDPRRAGSystem

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize RAG system
rag = GDPRRAGSystem(config)
```

### 2. Simple Question Answering

```python
# Ask a question
answer = rag.ask("What are the data subject rights under GDPR?")
print(answer)

# Get detailed response with sources
result = rag.query("What is a Data Protection Impact Assessment?")
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])}")

for source in result['sources']:
    print(f"  - {source['source']}: {source['document_type']}")
```

### 3. Filtered Queries

```python
# Query specific article
result = rag.query(
    "What are the requirements for consent?",
    filters={"article_number": "7"}
)

# Query specific source
result = rag.query(
    "What are EDPB guidelines on consent?",
    filters={"source": "EDPB"}
)

# Query specific document type
result = rag.query(
    "What case law exists on legitimate interest?",
    filters={"document_type": "case_law"}
)
```

### 4. Batch Processing

```python
queries = [
    "What is the right to erasure?",
    "When is a DPO required?",
    "What are the penalties for violations?"
]

results = rag.batch_query(queries, top_k=3)

for result in results:
    print(f"Q: {result['query']}")
    print(f"A: {result['answer'][:200]}...\n")
```

## Violation Detection

### 1. Basic Violation Analysis

```python
from violation_finder.violation_finder import GDPRViolationFinder

finder = GDPRViolationFinder(config)

scenario = """
We collect user email addresses without explicit consent and 
use them for marketing purposes. Users cannot easily unsubscribe.
"""

assessment = finder.analyze_scenario(scenario)

print(f"Risk Level: {assessment.overall_risk_level}")
print(f"Risk Score: {assessment.risk_score}/10")
print(f"Violations: {len(assessment.violations)}")
```

### 2. Detailed Violation Information

```python
assessment = finder.analyze_scenario(scenario)

for violation in assessment.violations:
    print(f"\nCategory: {violation.category}")
    print(f"Severity: {violation.severity}")
    print(f"Risk Score: {violation.risk_score}/10")
    print(f"Articles: {', '.join(violation.articles)}")
    print(f"Description: {violation.description}")
    print(f"Recommendation: {violation.recommendation}")
```

### 3. Generate Reports

```python
# Markdown report
report = finder.generate_compliance_report(
    scenario, 
    assessment, 
    format="markdown"
)
with open('report.md', 'w') as f:
    f.write(report)

# JSON report
report = finder.generate_compliance_report(
    scenario, 
    assessment, 
    format="json"
)
with open('report.json', 'w') as f:
    f.write(report)
```

### 4. Check Specific Requirements

```python
result = finder.check_specific_requirement(
    requirement="Article 6 - Legal Basis",
    scenario="We process employee data for payroll purposes"
)

print(result['analysis'])
```

## Advanced Usage

### 1. Custom Retrieval Parameters

```python
# Adjust number of retrieved documents
result = rag.query(query, top_k=10)

# Set score threshold
from vectorstore.faiss_store import FAISSVectorStore

vector_store = FAISSVectorStore(config)
vector_store.load_index()

results = vector_store.search(
    query="consent requirements",
    top_k=5
)

# Filter by score
high_quality = [r for r in results if r['score'] > 0.8]
```

### 2. Custom Prompts

```python
custom_prompt = """
Based on the following GDPR context, provide a brief summary 
suitable for non-technical stakeholders.

Context: {context}

Question: {query}

Summary:
"""

response = rag.generate_response(
    query="What is data minimization?",
    context=context,
    custom_prompt_template=custom_prompt
)
```

### 3. Access Vector Store Directly

```python
from vectorstore.faiss_store import FAISSVectorStore

vector_store = FAISSVectorStore(config)
vector_store.load_index()

# Get statistics
stats = vector_store.get_statistics()
print(f"Total documents: {stats['total_vectors']}")
print(f"Sources: {stats['sources']}")

# Search with metadata filters
results = vector_store.search(
    query="data breach notification",
    top_k=5,
    filter_metadata={
        "source": "EUR-Lex",
        "article_number": "33"
    }
)
```

## Integration Examples

### Flask API

```python
from flask import Flask, request, jsonify
from rag.gdpr_rag import GDPRRAGSystem
import yaml

app = Flask(__name__)

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

rag = GDPRRAGSystem(config)

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    result = rag.query(data['query'], top_k=data.get('top_k', 5))
    return jsonify(result)

@app.route('/analyze', methods=['POST'])
def analyze():
    from violation_finder.violation_finder import GDPRViolationFinder
    
    finder = GDPRViolationFinder(config)
    data = request.json
    assessment = finder.analyze_scenario(data['scenario'])
    
    return jsonify({
        'risk_level': assessment.overall_risk_level,
        'risk_score': assessment.risk_score,
        'violations': len(assessment.violations)
    })

if __name__ == '__main__':
    app.run(port=5000)
```

### FastAPI

```python
from fastapi import FastAPI
from pydantic import BaseModel
from rag.gdpr_rag import GDPRRAGSystem
import yaml

app = FastAPI()

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

rag = GDPRRAGSystem(config)

class Query(BaseModel):
    query: str
    top_k: int = 5

class Scenario(BaseModel):
    scenario: str

@app.post("/query")
async def query(q: Query):
    result = rag.query(q.query, top_k=q.top_k)
    return result

@app.post("/analyze")
async def analyze(s: Scenario):
    from violation_finder.violation_finder import GDPRViolationFinder
    
    finder = GDPRViolationFinder(config)
    assessment = finder.analyze_scenario(s.scenario)
    
    return {
        'risk_level': assessment.overall_risk_level,
        'risk_score': assessment.risk_score,
        'violations': [v.__dict__ for v in assessment.violations]
    }
```

### Streamlit Dashboard

```python
import streamlit as st
from rag.gdpr_rag import GDPRRAGSystem
import yaml

st.title("GDPR Compliance Assistant")

# Initialize
@st.cache_resource
def load_system():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return GDPRRAGSystem(config)

rag = load_system()

# Query interface
query = st.text_input("Ask a GDPR question:")

if query:
    with st.spinner("Searching..."):
        result = rag.query(query)
    
    st.subheader("Answer")
    st.write(result['answer'])
    
    with st.expander("View Sources"):
        for i, source in enumerate(result.get('sources', []), 1):
            st.write(f"{i}. {source['source']} - {source['document_type']}")
```

## Error Handling

```python
try:
    result = rag.query(query)
except Exception as e:
    print(f"Error processing query: {e}")
    # Handle error

# Check if vector store is loaded
if not rag.vector_store.index:
    print("Vector store not loaded. Please build the index first.")
```

## Performance Tips

1. **Reuse RAG instance**: Initialize once, query multiple times
2. **Adjust top_k**: Lower values = faster responses
3. **Use filters**: Narrow down search space
4. **Enable caching**: Cache embeddings for repeated queries
5. **Batch queries**: Process multiple queries together

## Best Practices

1. **Validate inputs**: Sanitize user queries
2. **Handle errors**: Implement proper error handling
3. **Monitor performance**: Track response times
4. **Cache results**: Cache frequent queries
5. **Update regularly**: Rebuild index with new data
6. **Log queries**: Keep audit trail
7. **Rate limit**: Prevent abuse in production

## Troubleshooting

### Vector Store Not Found
```python
from vectorstore.faiss_store import FAISSVectorStore

vector_store = FAISSVectorStore(config)
if not vector_store.load_index():
    print("Index not found. Run: python main.py build")
```

### Ollama Connection Issues
```python
import requests

try:
    response = requests.get('http://localhost:11434/api/tags')
    if response.status_code == 200:
        print("Ollama is running")
except:
    print("Ollama is not running. Start with: ollama serve")
```

### Memory Issues
```python
# Reduce batch size
config['embeddings']['batch_size'] = 16

# Use smaller model
config['ollama']['model'] = 'mistral'
```

## Reference

### RAG System Methods

- `query(query, top_k, filters, return_sources)`: Main query method
- `ask(query)`: Simple query, returns just answer
- `batch_query(queries)`: Process multiple queries
- `retrieve_context(query, top_k, filters)`: Get relevant documents
- `get_system_info()`: Get system information

### Violation Finder Methods

- `analyze_scenario(scenario, context_type)`: Analyze for violations
- `check_specific_requirement(requirement, scenario)`: Check specific requirement
- `generate_compliance_report(scenario, assessment, format)`: Generate report

### Vector Store Methods

- `search(query, top_k, filter_metadata)`: Semantic search
- `get_statistics()`: Get database statistics
- `load_index()`: Load existing index
- `save_index()`: Save index to disk
