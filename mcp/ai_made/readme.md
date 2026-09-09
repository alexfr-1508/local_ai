This dir contains mcp tools modifiable by the AI model itself via the terminal mcp server.
As long as the files stay executable and imports are installed tools defined here should be usable.
MCP servers are using the venv "/app/mcp/venv".
You can ignore the stdio file. It's mainly for connecting to LiteLLM and is just a template. Though since env variables are configured during connecting LiteLLM to the mcp servers, it will break unless stdio is reconfigured on LiteLLM side. Look at references of the other mcp servers if needed.