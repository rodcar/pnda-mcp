<div align="center">

# PNDA-MCP
#### **Model Context Protocol (MCP) Server for PNDA - National Open Data Platform / Plataforma Nacional de Datos Abiertos (Peru)**

---

### 👨‍💻 Author

**Ivan Yang Rodriguez Carranza**

[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:ivanrodcar@outlook.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/irodcar)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/rodcar)

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🎬 Demo](#-demo)
- [🔧 Tools](#-tools)
- [💬 Prompts](#-prompts)
- [🚀 How to Use](#-how-to-use)
- [💡 Examples](#-examples)
- [🏛️ Architecture Diagram](#️-architecture-diagram)
- [🔄 ETL Pipeline](#-etl-pipeline)
- [📝 License](#-license)

---

## 🎯 Overview

PNDA-MCP is a **Model Context Protocol (MCP) server** for **Peru's National Open Data Platform (Plataforma Nacional de Datos Abiertos)**. Although Peru's open data platform [datosabiertos.gob.pe](https://datosabiertos.gob.pe) hosts valuable datasets, it can be a challenging for AI agents to find and retrieve the most relevant data for a specific data analysis question. PNDA-MCP simplifies this by providing tools and prompts that let AI agents or any MCP client (such as VS Code or Claude Desktop) easily search for and access datasets metadata, and associated data files. The goal is to enable data scientist agents or code agents to automatically discover and analyze public datasets.

This repository includes the ETL pipeline used to extract, transform, and index dataset references (see `etl` folder).

---

## 🎬 Demo

<div align="center">

</div>

Demo (Spanish):

---

## 🔧 Tools

| Name | Input | Description |
|------|-------|-------------|
| `dataset_search` | `query`, `top_k` | Search for relevant datasets from the PNDA (Plataforma Nacional de Datos Abiertos) Peru. `query` is the search text, `top_k` limits the number of results returned (max 25). |
| `dataset_details` | `id` | Get dataset details including title, metadata, and resources. Returns complete resource information: direct download URLs, file names, sizes, creation dates, MIME types, formats, states, and descriptions. |

---

## 💬 Prompts

| Name | Input | Description |
|------|-------|-------------|
| `question_generation` | `topic` | Generate 5 data analysis questions for any topic using available PNDA datasets. |
| `analysis_quick` | `question` | Create a minimal Jupyter notebook with quick data analysis addressing a question. |
| `analysis_full` | `question` | Create a complete Jupyter notebook with detailed data exploration and analysis addressing a question. |

---

## 🚀 How to Use

### **Local Server**

> **Note:** Make sure you have `uv` installed. If not, install it from [uv.tool](https://docs.astral.sh/uv/getting-started/installation/).

1. Clone and install:
   ```bash
   git clone https://github.com/yourusername/pnda-mcp.git
   cd pnda-mcp
   uv sync
   ```

2. Add to Claude Desktop config (Claude > Settings > Developer > Edit Config):

> **Note:** Replace `/path/to/pnda-mcp` with the actual path where you cloned the repository.

   ```json
   {
     "mcpServers": {
       "pnda_mcp": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/pnda-mcp",
           "run",
           "main.py"
         ]
       }
     }
   }
   ```

### **MCP Inspector (Alternative)**

> **Note:** Requires `npx` which comes bundled with npm. If you don't have npm installed, install [Node.js](https://nodejs.org/) which includes npm.

> **Note:** Replace `/path/to/pnda-mcp` with the actual path where you cloned the repository.

Run:

```bash
npx @modelcontextprotocol/inspector \
  uv \
  --directory /path/to/pnda-mcp \                     
  run \
  main.py
```

Open MCP Inspector (URL displayed in the console) and configure the MCP client.

---

## 💡 Examples

| Prompt | Description | Usage |
|--------|-------------|-------|
| `tool_1` | Example usage | Coming soon |

---

## 🏛️ Architecture Diagram

PNDA-MCP follows the Model Context Protocol specification and provides a clean abstraction layer for PNDA functionality.

```mermaid
flowchart LR
    CLIENT["MCP Client\n(Claude Desktop, IDE, etc.)"] -->|MCP| MCP_SERVER["PNDA-MCP Server\n(main.py, FastMCP)"]
    MCP_SERVER -->|Tool| TOOLS["Tools\n(@mcp.tool)"]
    MCP_SERVER -->|Prompt| PROMPTS["Prompts\n(@mcp.prompt)"]
    TOOLS -->|Vector Search| PINECONE["Pinecone"]
    TOOLS -->|Embeddings| OPENAI["OpenAI API"]
    style CLIENT fill:#e3f2fd
    style MCP_SERVER fill:#f3e5f5
    style TOOLS fill:#e8f5e9
    style PROMPTS fill:#fffde7
    style PINECONE fill:#fff3e0
    style OPENAI fill:#ffe0e0
```

---

## 🔁 ETL Pipeline

> **Note:** The following ETL documentation is only needed if you want to run the MCP locally or deploy your own MCP service. You can use the remote MCP service without running the ETL.

To search datasets using natural language, semantic search with text vector embeddings is used. The ETL pipeline handles the initial indexing and ongoing synchronization of the vector database containing dataset metadata from Peru's National Open Data Platform. It can be run manually or automatically via cron jobs to ensure the dataset information stays up to date.

### Requirements

- **Redis server**: Message broker and result backend for distributed task processing via Celery.
- **OpenAI API key**: Valid API key with access to text embedding models (specifically `text-embedding-3-small`) for generating vector representations of dataset metadata
- **Pinecone account**: Active account with API access for cloud-based vector database operations, including index creation and vector storage/retrieval. If you don't have a Pinecone account, sign up at [pinecone.io](https://www.pinecone.io/).

### Running the ETL

Clone repository

Configuration env vars


commadn to create .env based on .env.example
then set openai api key
set pinecone api key

Run Redis with Docker

> **Note:** This is not the only way to have a broker and backend for Celery. See [Celery documentation](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html) for other options. 

```bash
docker run -d -p 6379:6379 redis
```

```bash
# Start Celery worker
./etl/celery_worker.sh
```

#### Manual Execution
```bash
# Run ETL pipeline
python -m etl.pipeline
```

#### Automated Execution
```bash
# Setup cron job (runs every 2 minutes)
crontab -e

# Add this line:
*/2 * * * * /path/to/pnda-mcp/etl/cron.sh

# Make script executable
chmod +x /path/to/pnda-mcp/etl/cron.sh

# Check
crontab -l
```

"results" folder and logs.

### ETL Diagram

```mermaid
flowchart LR
    subgraph EXTRACT_WRAPPER["<b>Extract</b>"]
        EXTRACT["Fetch complete dataset list from PNDA API"] --> PNDA_API["For each dataset, fetch metadata from PNDA API"]
    end
    
    subgraph TRANSFORM_WRAPPER["<b>Transform</b>"]
        FILTER["Filter active datasets"] --> STRUCTURE["Format dataset metadata for indexing"]
    end
    
    subgraph LOAD_WRAPPER["<b>Load</b>"]
        FILTER_CHANGED["Filter datasets with changes*"] --> EMBEDDINGS["Generate embeddings using OpenAI Text Embeddings API"] --> UPSERT["Upsert embeddings to the vector database (Pinecone)"]
    end
    
    EXTRACT_WRAPPER e1@==> TRANSFORM_WRAPPER
    TRANSFORM_WRAPPER e2@==> LOAD_WRAPPER
    
    e1@{ animate: true }
    e2@{ animate: true }
    
    style EXTRACT fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style PNDA_API fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style FILTER fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style STRUCTURE fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style FILTER_CHANGED fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style EMBEDDINGS fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style UPSERT fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

---

## 📝 License

This project is licensed under the [Apache License 2.0](LICENSE).

---

<div align="center">

[Report Bug](https://github.com/rodcar/bcrp-mcp/issues) · [Request Feature](https://github.com/rodcar/bcrp-mcp/issues)

</div>