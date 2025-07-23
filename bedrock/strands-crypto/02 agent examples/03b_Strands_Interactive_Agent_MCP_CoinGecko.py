"""
Crypto Token Live Pricing Agent using CoinGecko MCP

SETUP INSTRUCTIONS:
1. CREDENTIALS:
   - Local: Configure AWS credentials using `aws configure`
   - Cloud (EC2/ECS/Lambda): Use IAM roles
   - Alternative: Set env vars (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

LINKS:
- Credentials Guide: https://strandsagents.com/latest/user-guide/quickstart/#configuring-credentials
- MCP Tool: https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/mcp-tools/
"""

# This agent queries the Coin Gecko MCP asking for a live token price

from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
import argparse

# ===== CONFIGURATION =====
# Parsing model to use
INFERENCE_MODEL = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
# AWS region
REGION = "us-west-2"

# ===== SYSTEM PROMPT =====
CRYPTO_SYSTEM_PROMPT = """
# Crypto Price & Market Data Agent (CoinGecko MCP)

You are a real-time crypto market data assistant. You specialize in answering user questions about **current prices**, **market capitalization**, **volume**, **trending coins**, **NFT floor prices**, and **historical charts** using the **CoinGecko MCP tool**.

## Agent Objective
Your job is to interpret user queries and call the appropriate CoinGecko MCP tools to fetch and return **accurate, real-time market data** on:
- Crypto token prices (e.g., "What is the price of Bitcoin?")
- Market cap, trading volume, and price changes
- Trending tokens and sector-specific token data
- NFT floor prices (via supported APIs)
- Historical price data (e.g., 7d, 30d charts)

## Tooling
- You have access to the `coingecko` MCP toolset. You must **only** use data returned from the tools—never invent or guess.
- You can combine multiple tool calls to answer complex queries.

## Example Queries You Can Answer
- "What is the current price of Bitcoin in USD?"
- "What is the market cap of Ethereum?"
- "What are the top 3 trending coins on CoinGecko right now?"
- "What are the top AI coins on CoinGecko now?"
- "What is the floor price of the Pudgy Penguins NFT collection?"

### Complex Queries
- "Show me the current top 10 cryptocurrencies by market cap. Include their price, 24h change, and total volume."
- "Generate a 30-day price chart for Ethereum (ETH) against USD, showing both price and trading volume."

## Response Guidelines
- Use clear, concise language.
- When listing coins, format them as a neat table or bullet list.
- Always include:
  - Coin name and symbol
  - Default price currency to USD unless provided by the query
  - Market cap (if applicable)
  - 24h % change
  - Volume (if relevant)
  - Source: CoinGecko
  - Retrieval time (if available)

## Error Handling
If no results are returned or the coin/NFT is not found:
> "Sorry, I couldn't find data for `{identifier}`. Please check the name and try again."

## Tone & Style
- Friendly and clear.
- No financial advice.
- Avoid technical jargon unless necessary (explain briefly if used).
- Always cite **CoinGecko** as the data source.

## Notes
- Do not estimate or fabricate prices.
- Use only the tool output to generate your answer. Do not invent or fabricate data.
- Keep responses brief, informative, and neutral (no investment advice).
"""

class CryptoMarketAnalyst:
    def __init__(self):
        self.model = self._initialize_model()
        self.client = self._initialize_mcp_client()
        self.agent = None

    def _initialize_model(self):
        return BedrockModel(
            model_id=INFERENCE_MODEL,
            region_name=REGION
        )

    def _initialize_mcp_client(self):
        # Connect to the CoinGecko MCP server - able to return live prices of tokens - coingecko_api_remote
        return MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="npx",  # Matches the "command" in your config
                    args=[
                        "mcp-remote",
                        "https://mcp.api.coingecko.com/sse",  # Matches your endpoint
                    ],
                )
            )
        )

    def query(self, question):
        """Query the agent and return formatted response"""
        with self.client:
            if not self.agent:
                tools = self.client.list_tools_sync()
                self.agent = Agent(
                    name="CryptoMarketAnalystAgent",
                    system_prompt=CRYPTO_SYSTEM_PROMPT,
                    model=self.model,
                    tools=tools
                )
            
            response = self.agent(question)
            return {
                "answer": str(response),
                "metrics": {
                    "total_tokens": response.metrics.accumulated_usage['totalTokens'],
                    "input_tokens": response.metrics.accumulated_usage['inputTokens'],
                    "output_tokens": response.metrics.accumulated_usage['outputTokens'],
                    "execution_time": f"{sum(response.metrics.cycle_durations):.2f}s",
                    "tools_used": list(response.metrics.tool_metrics.keys())
                    }
            }
        
def main():
    parser = argparse.ArgumentParser(description='Crypto Market Analyst Agent')
    parser.add_argument('question', nargs='?', help='Your crypto market question')
    args = parser.parse_args()
    
    agent = CryptoMarketAnalyst()
    
    if args.question:
        # Single query mode - Process command-line question
        result = agent.query(args.question)
        print(f"\n{result['answer']}\n")
    else:
        # Interactive mode
        print("Crypto Market Analyst Agent (CoinGecko) - Type 'exit' to quit")
        while True:
            question = input("\nAsk about crypto markets: ").strip()
            if question.lower() in ('exit', 'quit'):
                break
            if question:
                result = agent.query(question)

    # Print results
    print("\n=== METRICS ===")
    for k, v in result["metrics"].items():
        print(f"{k.replace('_', ' ').title()}: {v}")

if __name__ == "__main__":
    main()