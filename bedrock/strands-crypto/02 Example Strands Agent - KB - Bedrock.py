"""
**credentials**
  1. if running locally, this will use AWS credentials file: Configure credentials using aws configure CLI command
  2. if running in AWS services like EC2, ECS, or Lambda, use IAM roles
  3. can also use environment variables, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and optionally AWS_SESSION_TOKEN
Make sure your AWS credentials have the necessary permissions to access Amazon Bedrock and invoke the Bedrock model.

**model access**
You'll need to enable model access in the Amazon Bedrock console.

**links**
https://strandsagents.com/latest/user-guide/quickstart/#configuring-credentials
"""

# This example queries the Bedrock knowledge base created in previous lab
# You will need to know its ID

from strands import Agent
from strands.models import BedrockModel
from strands_tools import retrieve

# kb created in previous lab
kb_id = "KP0ZO3GCYU"

# inference model to use
inference_model = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

# region
region = "us-west-2"

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

# Create a BedrockModel with specific LLM and region
bedrock_model = BedrockModel(model_id=inference_model, region_name=region)

# Create the strands agent and add the KB to the agent's tools
kb_agent = Agent(
    name="CryptoFocusedAgent",
    system_prompt=CRYPTO_SYSTEM_PROMPT,
    model=bedrock_model,
    tools=[retrieve],
)

# Query your Knowledge Base
response = kb_agent.tool.retrieve(
    text="What information do you have about cryptocurrency?",
    numberOfResults=5,
    #score=0.7,
    knowledgeBaseId=kb_id,
    region=region,
)
print(response)
