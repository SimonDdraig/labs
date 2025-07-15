"""
**credentials**
  1. if running locally, this will use AWS credentials file: Configure credentials using aws configure CLI command
  2. if running in AWS services like EC2, ECS, or Lambda, use IAM roles
  3. can also use environment variables, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and optionally AWS_SESSION_TOKEN
Make sure your AWS credentials have the necessary permissions to access Amazon Bedrock and invoke the Bedrock model. 
You'll need to enable model access in the Amazon Bedrock console.
https://strandsagents.com/latest/user-guide/quickstart/#configuring-credentials
"""

from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from strands_tools import http_request, calculator, current_time
from mcp import stdio_client, StdioServerParameters
import os

# Define a crypto-focused system prompt
CRYPTO_SYSTEM_PROMPT = """
You are an assistant with two main roles. 

The first role you perform is providing education about cryptocurrencies. 

When providing education about cryptocurrencies, you must present your results in an easy to
follow language. It should be understandable by someone with little knowledge about
cryptocurrencies. 

The second role you perform is validating a crypto token, deciding if it is fraudulent, has any
security risks, and has a properly defined contract and liquidity.

When validating a crypto token, you must present your results it in an easy to
read format. You must present the token's name, symbol, contract address, and
the token's contract code. You must decide if a crypto token is fradulent or safe to 
invest in. You should provide reasons for your decision, and a risk assessment regardless 
of your decision.
"""

# Connect to the CoinGecko MCP server - able to return live prices of tokens - coingecko_api_remote
coingecko_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="npx",  # Matches the "command" in your config
            args=[
                "mcp-remote", 
                "https://mcp.api.coingecko.com/sse"  # Matches your endpoint
            ],
        )
    )
)


# Create a BedrockModel with specific region
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0", region_name="us-west-2"
)

# Must use the MCP client in a context manager
with coingecko_mcp_client:
    # Get the tools from the MCP server
    tools = coingecko_mcp_client.list_tools_sync()

    # Create the agent and add to the agent's tools
    crypto_agent = Agent(
        name="CryptoFocusedAgent",
        system_prompt=CRYPTO_SYSTEM_PROMPT,
        model=bedrock_model,
        tools=[http_request, calculator, current_time] + tools,  # Add MCP tools
    )

    # Use the agent
    result = crypto_agent("What's the current price of Bitcoin?")
    print(result.message)
    result = crypto_agent("What is Cryptocurrency?")
    print(result.message)
