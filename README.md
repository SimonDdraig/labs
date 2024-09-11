# Simon's Labs
Welcome to the **Simon's Labs**! This repository contains all the resources, files, and notebooks you'll need to get started with AWS services.
## Note
These are typically POC labs and do not feature production hardened solutions. Please ensure if used, you implement best practice security and auth controls where necessary. 

In saying that, all IAM created is typically with least privilege, but public facing services may need additional auth.

## Setup
To get started, you'll need to set up your environment. Ensure you have the following prerequisites:

- Python 3.8 or higher
- AWS CLI configured with your credentials
- Necessary Python libraries (listed in each notebook)
- Access to Bedrock Models

## Files and Notebooks

| Lab                              | File/Notebook                        | Description                                               |
|----------------------------------|--------------------------------------|-----------------------------------------------------------|
|**Bedrock** | | AWS Bedrock Gen AI Labs |
| | **/Quick** | Quick labs demoing the unified API |
| | Image Generation.pynb | Generate images using Stability Diffusion or Amazon Titan |
| | Image Parsing.pynb | Use llm models to parse images |
| | Image Generation.pynb | Generate images using Stability Diffusion or Amazon Titan |
| | **/Quick/Resources** | Resources required by the Quick labs |
| | receipt.png | Scanned receipt image used in OCR example |
| | receipt rotated.png | Scanned receipt rotated image used in OCR example |
| | **/Receipt Chatbot**| Lab which creates a knowledge base and agent - The agent in an international chef expert in Thai, Japanese and Italian cuisines |
| | 01 Create Knowledge Base.ipynb | Creates a postgres vector db and knowledge base |
| | 02 Create Lambda and Agents.ipynb | Creates an agent, and 2 action groups for 2 lambdas |
| | **/Receipt Chatbot/Resources** | Resources required by the Receipt Chatbot labs |
| | **Receipt Chatbot/Resources/DataSource** | Files used as data sources for the knowledge base |
| |.pdf files | PDF files containing the text used for the knowledge base |
| |.pdf.metadata.json files | json files used to provide metadata describing each pdf file |
| | **/Receipt Chatbot/Resources/Lambda** | Files used as data sources for the knowledge base |
| |doit-bedrock-recipe-chatbot-order-delivery-fn.py| Python lambda simulating the order of ingredients from an online store |
| |doit-bedrock-recipe-chatbot-order-delivery-fn.zip| Zip used to create the lambda |
| |doit-bedrock-recipe-chatbot-send-recipe-email-fn.py| Python lambda which send the recipe to a recipient email |
| |doit-bedrock-recipe-chatbot-send-recipe-email-fn.zip| Zip used to create the lambda |
|**QuickSight** | Work In Progress | AWS QuickSight Labs |
|**Redshift** | Work In Progress | AWS Redshift Labs |

---

## Getting Started
Open the notebooks and Python files in Jupyter or any compatible environment and follow the instructions provided in each.
