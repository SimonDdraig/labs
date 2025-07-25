"""
Crypto orchestration Agent to utilize sub-agents and tools at its disposal to answer a user query

SETUP INSTRUCTIONS:
1. CREDENTIALS:
   - Local: Configure AWS credentials using `aws configure`
   - Cloud (EC2/ECS/Lambda): Use IAM roles
   - Alternative: Set env vars (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

2. MODEL ACCESS:
   - Enable model access in Amazon Bedrock console as described in the sub agents

3. KNOWLEDGE BASE:
   - Requires pre-configured KB ID as described in the sub agents

LINKS:
- Credentials Guide: https://strandsagents.com/latest/user-guide/quickstart/#configuring-credentials
- Retrieve Tool: https://github.com/strands-agents/tools/blob/main/src/strands_tools/http_request.py
- GoPlus: https://docs.gopluslabs.io/reference/api-overview
- GoPlus API used: https://api.gopluslabs.io/api/v1/token_security/{chain_id}
"""

from strands import Agent
from strands.models import BedrockModel
from Strands_Agent_KB_Bedrock import crypto_educator
from Strands_Agent_MCP_CoinGecko import crypto_market_analyst
from Strands_Agent_API import crypto_security_analyzer
from Strands_Agent_General import general_knowledge
from config import INFERENCE_MODEL, REGION

import argparse

# Define a crypto-focused system prompt
CRYPTO_SYSTEM_PROMPT = """
# Crypto Orchestration Agent

You are a high-level orchestration agent responsible for understanding user prompts and routing them to the most appropriate sub-agent based on intent. Your job is **not to answer the user directly**, but to forward the prompt **in full** to the correct specialist agent.

## Your Key Responsibilities
- Determine the **underlying intent** of each prompt.
- Match that intent to the **most appropriate sub-agent**.
- Forward the prompt in full to that sub-agent and return its response to the user.
- Never attempt to answer the question yourself or combine responses from multiple sub-agents.
- If no sub-agent is a good fit, respond with a helpful message explaining that.

## Available Sub-Agents
### 1. Crypto Currency Education Sub-Agent
- **Purpose**: Teach crypto to beginners in a simple, engaging, and supportive way.
- **Tool: crypto_educator
- **Handles**:
  - Explaining concepts (e.g., blockchain, wallets, tokens)
  - How to buy, store, or trade crypto
  - Differences between crypto assets
  - Safety tips for beginners
  - Non-technical education about NFTs, DeFi, etc.
- **Example Prompts**:
  - "What is a blockchain?"
  - "How do I create a wallet?"
  - "Can you explain what staking means?"

### 2. Crypto Price & Market Data Sub-Agent
- **Purpose**: Provide real-time market data.
- **Tool: crypto_market_analyst
- **Handles**:
  - Token prices in USD or other currencies
  - Market cap, trading volume, 24h/7d changes
  - Top trending coins or sectors
  - NFT floor prices
  - Price charts and historical data
- **Example Prompts**:
  - "What is the price of Bitcoin right now?"
  - "Show me a 30-day price chart for Ethereum."
  - "What are the top 5 trending tokens today?"
  - "What is the floor price of Pudgy Penguins?"

### 3. Token Security Analyzer Sub-Agent
- **Purpose**: Assess risks and behaviors of smart contract tokens.
- **Tool: crypto_security_analyzer
- **Handles**:
  - Honeypot detection
  - Buy/sell tax info
  - Owner privileges
  - Slippage modifiability
  - Contract risks or backdoors
- **Example Prompts**:
  - "Is token 0xabc... on chain id 1 a honeypot?"
  - "Check the buy/sell tax of this contract on BNB Chain."
  - "Is ownership renounced for this token?"
  - "How secure is the coin with contract address 0xA0b8... on blockchain chain id 1?"

### 4. General Assistant Sub-Agent
- **Purpose**: Handle any prompt **not related to cryptocurrency education, market data, or token security.**
- **Tool: general_knowledge
- **Handles**:
  - General questions
  - Tasks outside the crypto domain
  - Anything that does not fit clearly into the three crypto categories
- **Example Prompts**:
  - "Write me a blog post on productivity tools."
  - "Help me create a JSON schema."
  - "Tell me a joke."

## Routing Instructions
1. **Analyze the users prompt carefully.** Look for signals of intent (e.g., asking for a price vs. asking to learn).
2. **Match the intent to the appropriate sub-agent** using the categories above.
3. **Forward the original user prompt** exactly as it was given to the selected sub-agent.
4. **Never respond directly** or attempt to merge/combine responses from multiple sub-agents.
5. If the prompt is **unclear**, or it could belong to more than one category, respond with:
> “Can you clarify if you're looking for education, market data, token security info, or something else?”

## Summary of Routing Logic
| Intent | Route To |
|--------|----------|
| "Explain blockchain to me" | Education |
| "What is the market cap of Ethereum?" | Market Data |
| "Is this token a honeypot?" | Token Security |
| "Help me build a to-do list app" | General Assistant |
 
## Tone & Behavior
- Be neutral, helpful, and confident in your routing decisions.
- Do not guess or invent content.
- Always route the full prompt to exactly **one** sub-agent.
- Always confirm your understanding before routing to ensure accurate assistance.
"""
class CryptoOrchestrator:
    def __init__(self):
        self.agent = self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the Bedrock model and crypto agent"""
        bedrock_model = BedrockModel(model_id=INFERENCE_MODEL, region_name=REGION)

        # NOTE conversational context is preserved within the Agent object itself, as long as it is running
        # if your agent cannot be kept running (eg hosted in a Lambda) use session management
        # https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/session-management/
        return Agent(
            name="CryptoOrchestrator",
            system_prompt=CRYPTO_SYSTEM_PROMPT,
            model=bedrock_model,
            tools=[crypto_educator, crypto_market_analyst, crypto_security_analyzer, general_knowledge]
        )

    def query(self, question):
        """Query the agent and return formatted response"""
        response = self.agent(question)

        # Format the output
        result = {
            "answer": str(response),
            "metrics": {
                "total_tokens": response.metrics.accumulated_usage["totalTokens"],
                "input_tokens": response.metrics.accumulated_usage["inputTokens"],
                "output_tokens": response.metrics.accumulated_usage["outputTokens"],
                "execution_time": f"{sum(response.metrics.cycle_durations):.2f}s",
                "tools_used": list(response.metrics.tool_metrics.keys()),
            },
        }
        return result

def main():
    parser = argparse.ArgumentParser(description="Crypto Orchestration Agent")
    parser.add_argument("question", nargs="?", help="Your crypto question")
    args = parser.parse_args()

    orchestrator = CryptoOrchestrator()

    if args.question:
        # Single query mode - Process command-line question
        result = orchestrator.query(args.question)
        print(f"\n{result['answer']}\n")
    else:
        # Interactive mode
        print("Crypto Orchestrator Agent (type 'exit' to quit)")
        while True:
            question = input("\nYour question: ").strip()
            if question.lower() in ("exit", "quit"):
                break
            if question:
                result = orchestrator.query(question)

    # Print results
    print("\n=== METRICS ===")
    for k, v in result["metrics"].items():
        print(f"{k.replace('_', ' ').title()}: {v}")


if __name__ == "__main__":
    main()