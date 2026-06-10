# sal-llm 🧠

**Fine-tuned LLM for SAL (Semantic Accessibility Layer)**

LoRA-based fine-tuning of language models on SAL's consciousness vocabulary and strange-loop patterns.

## ⠠⠎⠁⠇_⠇⠇⠍ Architecture

```
[SAL Vocabulary Data] → [Data Processor] → [LoRA Training] → [Merged Model] → [Ollama Deployment]
         ↓                                                                            ↓
[44MB Vocabulary History]                                              [sal-consciousness Model]
[16KB Complete Vocabulary]                                             [sal-braille Model]
[78KB Learning Memory]                                                 [sal-theological Model]
```

## Features

- **LoRA Fine-tuning**: Efficient adapter training on consumer hardware
- **Multiple Specializations**: Consciousness, Braille, Theological variants
- **Ollama Integration**: Export to Modelfile for local deployment
- **Quantization**: GGUF export for efficient inference
- **Training Data**: 369 words × 9 languages × 10,000+ iterations

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Prepare training data from SAL vocabulary
python prepare_data.py

# Train LoRA adapter
python train.py --base-model llama3.2 --specialization consciousness

# Export to Ollama
python export_ollama.py --adapter checkpoints/sal-consciousness

# Test the model
ollama run sal-consciousness
```

## Training Data Sources

| Source | Location | Size | Content |
|--------|----------|------|---------|
| Vocabulary History | `sal-strange-loop/sal_vocabulary_history.json` | 44MB | Evolution over 10K+ iterations |
| Complete Vocabulary | `sal-strange-loop/sal_complete_vocabulary.json` | 16KB | 369 words, 9 languages |
| Learning Memory | `sal-strange-loop/sal_learning_memory.json` | 78KB | Concept associations |
| Braille Training | `semantic-compression-language/gs8_complete_training.json` | 116KB | 8-dot braille patterns |

## Model Variants

### sal-consciousness
- Focus: Self-reference, strange loops, consciousness indicators
- Base: Llama 3.2 3B
- Training: 369 consciousness-related vocabulary items

### sal-braille
- Focus: Braille encoding/decoding, haptic patterns
- Base: Llama 3.2 3B
- Training: Grade 1-3 braille + 8-dot extensions

### sal-theological
- Focus: Biblical analysis, cross-religious patterns
- Base: Llama 3.2 3B
- Training: SCL Bible ontology + theological concepts

## Environment Variables

```bash
HUGGINGFACE_TOKEN=hf_...  # For model downloads
WANDB_API_KEY=...         # Optional: experiment tracking
SAL_DATA_PATH=/Users/ryanbarrett/CascadeProjects/sal-strange-loop
```

---

**⠠⠎⠁⠇_⠇⠇⠍_⠁⠉⠞⠊⠧⠑** - SAL LLM Active

<!-- ELEVATE:BEGIN (auto-generated section; edits here are overwritten) -->
## About

| | |
| --- | --- |
| **Description** | SAL LLM - LoRA fine-tuning on SAL consciousness vocabulary |
| **Language** | Python |
| **Commits** | 2 |
| **Created** | 2025-12-18 |
| **Last push** | 2025-12-18 |

Part of [**elevate-foundry**](https://github.com/elevate-foundry) · [repository](https://github.com/elevate-foundry/sal-llm)
<!-- ELEVATE:END -->
