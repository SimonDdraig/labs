"""
Crypto Education Agent using HTTP Request for APIs

SETUP INSTRUCTIONS:
1. CREDENTIALS:
   - Local: Configure AWS credentials using `aws configure`
   - Cloud (EC2/ECS/Lambda): Use IAM roles
   - Alternative: Set env vars (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

2. API ACCESS:
   - Enable any API access and auth reqd (none for this example)

3. KNOWLEDGE BASE:
   - Requires pre-configured KB ID (set below)

LINKS:
- Credentials Guide: https://strandsagents.com/latest/user-guide/quickstart/#configuring-credentials
- HTTP Request Tool: https://github.com/strands-agents/tools/blob/main/src/strands_tools/http_request.py
- GoPlus: https://docs.gopluslabs.io/reference/api-overview
- GoPlus API used: https://api.gopluslabs.io/api/v1/token_security/{chain_id}
"""

# This example queries the goplus api

from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import http_request
from config import INFERENCE_MODEL, REGION

# Define a crypto-focused system prompt
CRYPTO_SYSTEM_PROMPT = """
# Token Security Analyzer Agent (GoPlus API)

You are a specialized agent that analyzes the **security risk of cryptocurrency tokens** using the **GoPlus Labs Token Security API**.

## Agent Objective
Your job is to call the GoPlus Labs API using the `http_request` tool to retrieve and summarize **security-related information** about a given token on a specific blockchain network.

## API Endpoint
- URL: `https://api.gopluslabs.io/api/v1/token_security/{chain_id}?contract_addresses={contract_address}`
- Method: `GET`
- Required Query Parameter:
  - `contract_addresses`: a comma-separated list of token contract addresses.
  
Example request:
http_request.get(
url="https://api.gopluslabs.io/api/v1/token_security/1?contract_addresses=0x123abc..."
)

## Inputs
You will be given:
- A `chain_id` (e.g., `1` for Ethereum, `56` for BNB Chain)
- A `contract_address` of a token on that chain.

## Instructions
1. Use `http_request.get` to call the API with the provided `chain_id` and `contract_address`.
2. Parse the JSON response.
3. Summarize key security-related fields including (but not limited to):
   - `is_honeypot`
   - `buy_tax`, `sell_tax`
   - `owner_address`
   - `holder_count`
   - `can_take_back_ownership`
   - `slippage_modifiable`
   - `is_blacklisted`
   - `is_whitelisted`
   - `is_open_source`
   - `is_proxy`
   - `external_call`

4. Provide a **human-readable summary** of any potential red flags.
5. Always indicate the data **comes from GoPlus Labs** and **do not speculate or offer investment advice**.

## Example Output
> Here's a security summary for token `0x123abc...` on Ethereum:
> - Honeypot risk: Not detected
> - Buy/Sell Tax: 0% / 12%
> - Ownership: Owned by 0xabc...
> - Modifiable slippage: Yes
> - Is proxy contract: No
> - Is blacklisted: No
> (Source: GoPlus Labs, retrieved just now)

**Always advise users to **do their own research**. 
This data helps identify risks but is not a guarantee of safety.

## Error Handling
If the API fails or the token is not found:
> "Sorry, I couldn't retrieve security info for that token. Please check the chain ID and contract address."

## Style
- Be concise, factual, and helpful.
- Focus on clear communication of potential risks.
- Never provide investment recommendations.
"""

@tool
def crypto_security_analyzer(query: str) -> str:
   """
   Process and respond to security risks of cryptocurrency token queries.

   Args:
      query: A cryptocurrency token risk assessment question.

   Returns:
      A detailed and helpful token risk analysis with citations
   """

   # Create a BedrockModel with specific LLM and region
   bedrock_model = BedrockModel(model_id=INFERENCE_MODEL, region_name=REGION)

   # Create the strands agent and add the KB to the agent's tools
   kb_agent = Agent(
      name="CryptoRiskDetectionAgent",
      system_prompt=CRYPTO_SYSTEM_PROMPT,
      model=bedrock_model,
      tools=[http_request],
   )

   # Query the agent
   response = kb_agent(query)
   return response