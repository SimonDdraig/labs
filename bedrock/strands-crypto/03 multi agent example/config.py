# ===== CONFIGURATION =====
# Inference model to use
#INFERENCE_MODEL = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
INFERENCE_MODEL = "amazon.nova-pro-v1:0"

# AWS region
REGION = "us-east-1"

# Your Bedrock Knowledge Base ID
# REPLACE THIS WITH YOURS
KB_ID = "XXXXXXXX"

# DO NOT REPLACE THIS ONE
if KB_ID == "XXXXXXXX":
    raise RuntimeError("⚠️ Execution stopped: KB_ID is not configured properly.\nFind your Bedrock Knowledge Base ID from a previous lab or in your console, and set in config.py!")