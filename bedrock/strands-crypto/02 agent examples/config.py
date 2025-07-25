# ===== CONFIGURATION =====
# Inference model to use
#INFERENCE_MODEL = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
INFERENCE_MODEL = "amazon.nova-pro-v1:0"

# AWS region
REGION = "us-east-1"

# Your Bedrock Knowledge Base ID
KB_ID = "aXXXXXXXX"

if KB_ID == "XXXXXXXX":
    raise RuntimeError("⚠️ Execution stopped: KB_ID is not configured properly.\nFind your Bedrock Knowledge Base ID from a previous lab or in your console, and set in config.py!")