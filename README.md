<div align="center">

# PNDA-MCP
#### **Model Context Protocol (MCP) Server for PNDA**

---

### 👨‍💻 Author

**Your Name**

[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:your.email@example.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/yourprofile)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yourusername)

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🔧 Tools](#-tools)
- [💬 Prompts](#-prompts)
- [🚀 How to Use](#-how-to-use)
- [💡 Examples](#-examples)
- [🏛️ Architecture Diagram](#️-architecture-diagram)
- [📝 License](#-license)

---

## 🎯 Overview

PNDA-MCP is a **Model Context Protocol (MCP) server** that provides functionality for PNDA (Platform for Network Data Analytics). This server enables AI agents and applications to interact with PNDA through a standardized MCP interface.

---

## 🔧 Tools

| Name | Input | Description |
|------|-------|-------------|
| `tool_1` | - | Placeholder tool for PNDA functionality |

---

## 💬 Prompts

| Name | Input | Description |
|------|-------|-------------|
| `prompt_1` | - | Placeholder prompt for PNDA functionality |

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

## 🔄 ETL Pipeline Diagram

```mermaid
flowchart LR
    ETL_SCRIPT["ETL Pipeline\n(pipeline.py)"] --> CELERY["Celery Worker\n(tasks/app.py)"]
    CELERY --> EXTRACT["Extract\n(extract_tasks.py)"]
    CELERY --> TRANSFORM["Transform\n(transform_tasks.py)"]
    CELERY --> LOAD["Load\n(load_tasks.py)"]
    EXTRACT --> PNDA_API["PNDA API"]
    LOAD --> PINECONE["Pinecone"]
    CELERY --> REDIS["Redis\n(Broker/Backend)"]
    style ETL_SCRIPT fill:#f9fbe7
    style CELERY fill:#e8f5e9
    style EXTRACT fill:#e1f5fe
    style TRANSFORM fill:#fffde7
    style LOAD fill:#f3e5f5
    style PNDA_API fill:#e1f5fe
    style PINECONE fill:#fff3e0
    style REDIS fill:#fbe9e7
```

---

## 📝 License

This project is licensed under the [Apache License 2.0](LICENSE).

---


(correct)
./etl/celery_worker.sh

(correct)
python -m etl.pipeline


crontab -e

SHELL=/bin/bash
*/1 * * * * /Users/ivan/Workspace/mcp-projects/pnda-mcp/etl/cron.sh

ESC + :wq + ENTER

crontab -l

crontab -r

---
/Users/ivan/miniconda3/bin/python3

*/2 * * * * /Users/ivan/Workspace/mcp-projects/pnda-mcp/etl/cron.sh

SHELL=/bin/bash
*/2 * * * * /Users/ivan/Workspace/mcp-projects/pnda-mcp/etl/cron.sh

chmod +x /Users/ivan/Workspace/mcp-projects/pnda-mcp/etl/cron.sh

:wq

crontab -e

dd -> to delete
esc + :wq

crontab -l

crontab -r ->delete



SHELL=/bin/bash
*/1 * * * * /Users/ivan/Workspace/mcp-projects/pnda-mcp/etl/cron.sh