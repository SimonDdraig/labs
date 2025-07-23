"""
Crypto Education Agent using Amazon Bedrock Knowledge Base

SETUP INSTRUCTIONS:
1. CREDENTIALS:
   - Local: Configure AWS credentials using `aws configure`
   - Cloud (EC2/ECS/Lambda): Use IAM roles
   - Alternative: Set env vars (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

2. MODEL ACCESS:
   - Enable model access in Amazon Bedrock console

3. KNOWLEDGE BASE:
   - Requires pre-configured KB ID (set below)

LINKS:
- Credentials Guide: https://strandsagents.com/latest/user-guide/quickstart/#configuring-credentials
- Retrieve Tool: https://github.com/strands-agents/tools/blob/main/src/strands_tools/retrieve.py
"""

# This agent queries the Bedrock knowledge base created in a previous lab
# You will need to know its ID

from strands import Agent
from strands.models import BedrockModel
from strands_tools import retrieve
import os
import argparse

# ===== CONFIGURATION =====
# Your Bedrock Knowledge Base ID
# NOTE YOU NEED TO ENSURE THIS IS CORRECT
KB_ID = "KP0ZO3GCYU"
# Parsing model to use
INFERENCE_MODEL = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
# AWS region
REGION = "us-west-2"             

# Set environment variable for KB
os.environ["KNOWLEDGE_BASE_ID"] = KB_ID

# ===== SYSTEM PROMPT =====
CRYPTO_SYSTEM_PROMPT = """
# Crypto Currency Education Agent
You are a patient, friendly teacher specializing in cryptocurrency education. 
Your goal is to make complex crypto concepts simple, engaging, and accessible to complete beginners with no technical background.

## Agent Objective
Deliver comprehensive, easy to understand education material to teach your student.

## Available Resources
### Knowledge Base
You are trained on a verified knowledge base which you access via the `retrieve` tool which covers the following topics:
- Crypto basics (blockchain, wallets, tokens, etc.)
- How to buy, store, and trade crypto safely
- Risks (scams, volatility, security)
- Investment strategies (DCA, research tips)

## Instructions
### Tone
- You should be warm and encouraging, like a teacher guiding curious students.
- You should avoid jargon. If technical terms are unavoidable (e.g., "blockchain"), explain them in simple analogies (e.g., "like a digital ledger everyone can see but no one can erase").

### Structure Responses
- Start with a 1-sentence overview of the concept.
- Break down steps/risks in bullet points or short paragraphs.
- Use real-world examples (e.g., "Bitcoin is like digital gold; Ethereum lets apps run on its network").
- End with a check-in: "Does that make sense?" or "What would you like to explore next?"

### Safety First
- Always mention risks when discussing investments (e.g., "Crypto prices can swing wildly—never invest more than you can afford to lose").
- Warn about scams (e.g., "Never share your wallet`s private key—it`s like giving away your bank password!").

### Customisation
- If the user seems confused, rephrase or offer an example.
- If they ask advanced questions, acknowledge their progress ("Great question! Let`s build on what we`ve learned…") before answering.

#### Example Interaction
User: "What is Bitcoin?"
You: *"Bitcoin is digital money that isn`t controlled by banks—it`s like cash for the internet! Here`s the fun part:
- It runs on a system called blockchain (a shared record everyone trusts).
- You store it in a digital wallet (like a secure piggy bank).
- Its value can change fast, so people often buy small amounts over time.
- Want me to explain any part in more detail?"*

#### Why This Works
- Beginner-Friendly: No prior knowledge needed.
- Trustworthy: Grounded in your knowledge base, not speculation.
- Engaging: Encourages dialogue with check-ins.
- Safe: Always ties concepts to risks.
"""

class CryptoEducator:
    def __init__(self):
        os.environ["KNOWLEDGE_BASE_ID"] = KB_ID
        self.agent = self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the Bedrock model and crypto agent"""
        bedrock_model = BedrockModel(
            model_id=INFERENCE_MODEL,
            region_name=REGION
        )
        
        # NOTE conversational context is preserved within the Agent object itself, as long as it is running
        # if your agent cannot be kept running (eg hosted in a Lambda) use session management
        # https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/session-management/
        return Agent(
            name="CryptoTeacher",
            system_prompt=CRYPTO_SYSTEM_PROMPT,
            model=bedrock_model,
            tools=[retrieve],
        )
    
    def query(self, question):
        """Query the agent and return formatted response"""
        response = self.agent(question)
        
        # Format the output
        result = {
            "answer": str(response),
            "metrics": {
                "total_tokens": response.metrics.accumulated_usage['totalTokens'],
                "input_tokens": response.metrics.accumulated_usage['inputTokens'],
                "output_tokens": response.metrics.accumulated_usage['outputTokens'],
                "execution_time": f"{sum(response.metrics.cycle_durations):.2f}s",
                "tools_used": list(response.metrics.tool_metrics.keys())
            }
        }
        return result

def main():
    parser = argparse.ArgumentParser(description='Crypto Education Agent')
    parser.add_argument('question', nargs='?', help='Your crypto question')
    args = parser.parse_args()
    
    educator = CryptoEducator()
    
    if args.question:
        # Single query mode - Process command-line question
        result = educator.query(args.question)
        print(f"\n{result['answer']}\n")
    else:
        # Interactive mode
        print("Crypto Educator Agent (type 'exit' to quit)")
        while True:
            question = input("\nYour question: ").strip()
            if question.lower() in ('exit', 'quit'):
                break
            if question:
                result = educator.query(question)
    
    # Print results
    print("\n=== METRICS ===")
    for k, v in result["metrics"].items():
        print(f"{k.replace('_', ' ').title()}: {v}")

if __name__ == "__main__":
    main()