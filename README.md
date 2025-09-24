# Bespoke Document Embeddings

A document processing and question generation system that parses PDF documents and generates contextual questions using locally served LLM models via vLLM.

## Features

- **PDF Document Parsing**: Uses Docling to extract structured content from PDF documents
- **Intelligent Text Consolidation**: Groups content by sections/headers with token-aware chunking
- **Question Generation**: Generates 5 contextual questions per text chunk using LLM
- **Local LLM Integration**: Communicates with vLLM-served models via OpenAI-compatible API
- **Token Management**: Automatically adjusts content chunks based on model's context window

## Project Structure

```
bespoke_document_embeddings/
├── parser/
│   ├── data/                    # Input PDF files
│   ├── output/                  # Parsed JSON outputs
│   └── docling_parser.py        # PDF parsing logic
├── question_generator/
│   ├── output/                  # Generated questions output
│   ├── generate_questions.py    # Question generation logic
│   ├── llm_utils.py            # LLM communication utilities
│   └── prompts.py              # System and user prompts
├── models/                     # Cached model files
├── main.py                     # Main execution script
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

## Prerequisites

- Python 3.13+
- Hugging Face account and token
- vLLM server running locally

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd bespoke_document_embeddings
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   cp .env_example .env
   ```
   
   Edit `.env` and add your configuration:
   ```env
   HF_TOKEN=your_huggingface_token
   BI_ENCODER_MODEL_NAME=your_encoder_model_name
   CACHE_DIR=./models
   CONTEXT_WINDOW=3000
   ```

## Usage

### 1. Start vLLM Server

First, start the vLLM server with Llama model:

```bash
vllm serve meta-llama/Llama-3.2-3B-Instruct --max-model-len 3000 --max-num-batched-tokens 3000 --dtype auto --api-key praveen@123
```

### 2. Run the Pipeline

Execute the main script to process a PDF and generate questions:

```bash
python main.py
```

This will:
1. Parse the PDF document (`parser/data/AWQ.pdf`)
2. Extract and consolidate text content by sections
3. Generate questions for each text chunk
4. Save results to `question_generator/output/parsed_content_with_questions.json`

### 3. Output Files

The pipeline generates several output files:

- `parser/output/table_of_contents.json` - Document structure with page numbers
- `parser/output/parsed_output.json` - Raw parsed document data
- `parser/output/consolidated_parsed_output.json` - Text consolidated by sections
- `parser/output/tokenizer_adjusted_parsed_output.json` - Token-aware chunked content
- `question_generator/output/parsed_content_with_questions.json` - Final output with questions

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `HF_TOKEN` | Hugging Face authentication token | `hf_xxxxx` |
| `BI_ENCODER_MODEL_NAME` | Model name for tokenizer | `google/embeddinggemma-300m` |
| `CACHE_DIR` | Directory for cached models | `./models` |
| `CONTEXT_WINDOW` | Maximum tokens per chunk | `3000` |

### vLLM Server Configuration

The system expects a vLLM server running on `http://localhost:8000` with:
- Model: `meta-llama/Llama-3.2-3B-Instruct`
- API Key: `praveen@123`
- Max model length: 3000 tokens
- Max batched tokens: 3000

## Components

### PDFParser (`parser/docling_parser.py`)

Handles PDF document processing with the following capabilities:
- Document conversion using Docling
- Table of contents extraction
- Text consolidation by sections
- Token-aware content chunking
- Multiple output formats (JSON, Markdown)

### GenerateQuestions (`question_generator/generate_questions.py`)

Generates contextual questions from parsed content:
- Processes each text chunk individually
- Extracts structured JSON responses from LLM
- Handles malformed responses gracefully
- Progress tracking with tqdm

### LLM Utils (`question_generator/llm_utils.py`)

Manages communication with the vLLM server:
- OpenAI-compatible API client
- Configurable model and parameters
- System and user prompt handling

## Example Output

The final output contains structured data like:

```json
{
  "Section Title": {
    "start_page": 1,
    "text_with_questions": [
      {
        "text_content": "Your document content here...",
        "questions": [
          "What is the main concept discussed?",
          "How does this relate to the broader topic?",
          "What are the key findings?",
          "What methodology was used?",
          "What are the implications?"
        ]
      }
    ]
  }
}
```

## Dependencies

- **docling**: PDF document processing
- **transformers**: Tokenizer for content chunking
- **openai**: LLM API communication
- **vllm**: Local model serving
- **python-dotenv**: Environment variable management
- **tqdm**: Progress tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Troubleshooting

### Common Issues

1. **vLLM Server Not Running**: Ensure the vLLM server is started before running the pipeline
2. **Token Limit Exceeded**: Adjust `CONTEXT_WINDOW` in environment variables
3. **Model Not Found**: Verify model name and Hugging Face token
4. **JSON Parsing Errors**: Check LLM responses in logs for malformed JSON

### Support

For issues and questions, please open an issue in the repository.
