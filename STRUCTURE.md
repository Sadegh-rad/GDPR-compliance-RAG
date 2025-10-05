# Project Structure

```
GDPR-compliance-RAG/
│
├── 📄 README.md                    # Start here - simple guide
├── 📄 main.py                      # Main command interface
├── 📄 config.yaml                  # System configuration
├── 📄 requirements.txt             # Python dependencies
│
├── 📁 src/                         # Source code
│   ├── 📁 data_collection/         # Download GDPR sources
│   ├── 📁 preprocessing/           # Process documents
│   ├── 📁 vectorstore/             # Vector database (FAISS)
│   ├── 📁 rag/                     # AI Q&A system
│   ├── 📁 violation_finder/        # Compliance checker
│   ├── 📄 config.py                # Config management
│   └── 📄 utils.py                 # Helper functions
│
├── 📁 data/                        # GDPR data storage
│   ├── 📁 raw/                     # Downloaded sources
│   └── 📁 processed/               # Processed chunks
│
├── 📁 vectorstore/                 # Search index
│   ├── gdpr_faiss_index.faiss     # Vector index
│   └── gdpr_faiss_index_metadata.pkl  # Metadata
│
├── 📁 scripts/                     # Helper scripts
│   ├── demo.py                     # Demo examples
│   ├── test_system.py              # System tests
│   ├── quick_build.sh              # Quick setup
│   └── build_full_database.sh      # Full setup
│
├── 📁 docs/                        # Documentation
│   ├── GETTING_STARTED.md          # Step-by-step guide
│   ├── QUICK_REFERENCE.md          # Command reference
│   ├── PROJECT_SUMMARY.md          # Project overview
│   ├── 📁 technical/               # Technical docs
│   │   ├── API_GUIDE.md            # API documentation
│   │   ├── ARCHITECTURE.md         # System design
│   │   └── DATA_SOURCES.md         # Data sources info
│   └── 📁 reports/                 # Development reports
│       ├── TEST_RESULTS.md         # Test outcomes
│       ├── QUALITY_IMPROVEMENTS.md # Quality upgrades
│       ├── SYSTEM_SUCCESS.md       # Success metrics
│       └── ANTI_HALLUCINATION_FIXES.md  # Bug fixes
│
└── 📁 logs/                        # Application logs
    └── gdpr_rag.log
```

## Key Files

### For Users
- **README.md** - Start here, simple guide
- **config.yaml** - Change settings here
- **main.py** - Run commands here

### For Developers
- **src/** - All source code
- **docs/technical/** - Technical documentation
- **scripts/** - Utility scripts

### Generated
- **data/** - Downloaded GDPR data
- **vectorstore/** - Search index (auto-created)
- **logs/** - Application logs
