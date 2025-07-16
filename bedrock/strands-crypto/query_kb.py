from strands import Agent
from strands_tools import retrieve

# Create agent with your specific model and the retrieve tool
agent = Agent(
    model="arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
    tools=[retrieve],
    tool_config={"retrieve": {"knowledge_base_id": "KP0ZO3GCYU"}}
)

# Query your Knowledge Base
response = agent("What information do you have about cryptocurrency?")
print(response.message)