# WindCare – Maintenance AI agent (Microsoft Foundry)

Maintenance assistant for the fictional **Mendibeltz Wind Farm** (Haizea Renewables, 4 EKW-3.2 turbines).
Built for the MADI Cloud Computing Challenge (Day 4).

## Agent (configured in Microsoft Foundry)
- **Model:** gpt-5.4-mini (existing deployment in the Foundry project)
- **Instructions:** maintenance assistant rules (cite documents, safety first, structured diagnosis)
- **Code Interpreter:** SCADA data analysis and charts
- **Knowledge (RAG):** company PDFs (maintenance manual, alarm codes, safety procedures, spare parts) indexed in Azure AI Search
- **MCP:** GitHub MCP server – maintenance tickets as GitHub Issues (read, comment, create work orders)

## Programs (Foundry SDK – `azure-ai-projects`)
- `windcare_terminal.py` – terminal chat with the agent, including MCP approval handling (human-in-the-loop)
- `windcare_web.py` – web chat interface with Streamlit (EXTRA)

Authentication uses `DefaultAzureCredential` (Azure CLI login). No API keys in the code.

## Run in GitHub Codespaces
1. **Code → Codespaces → Create codespace on main** (Python, Azure CLI and libraries are installed automatically).
2. Log in to Azure:
   ```
   az login --use-device-code
   ```
3. Terminal version:
   ```
   python windcare_terminal.py
   ```
4. Web version:
   ```
   streamlit run windcare_web.py
   ```
   Open the forwarded port **8501** when Codespaces asks.
