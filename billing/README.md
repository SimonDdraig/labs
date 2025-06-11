# Simon's Labs - Billing  
This repository contains all the resources, files, and notebooks you'll need to get started with AWS Billing recommendations.  

## Note  
These are typically POC labs and do not feature production hardened solutions. Please ensure if used, you implement best practice security and auth controls where necessary.  

In saying that, all IAM created is typically with least privilege, but public facing services may need additional auth.  

## Setup  
To get started, you'll need to set up your environment. Ensure you have the following prerequisites:  

- Python 3.8 or higher - see the comment in the Jupyter Notebook for minimum Python version  
- AWS CLI configured with your credentials  
- Necessary Python libraries (listed in each notebook)  

## Getting Started  
Open the notebooks and Python files in Jupyter or any compatible environment and follow the instructions provided in each.  

## Architecture  
This project creates the following architecture:  

- S3 bucket  
  - The folder "dataexport_cur2.0" is where you can upload your data export billing files to - a sample is provided with this lab but you can replace with your own example if you wish  
  - It writes a markdown file to the same folder, named the same as the data export file except with a .md extension   
- IAM Role  
  - Creates a role to allow the lambda to:  
    - Write logs  
    - Read from and write to S3  
- Lambda  
  - Creates a lambda layer which contains the requests library  
    - The requests library is required to use https to reach github where the markdown files are stored  
  - Creates a lambda which processes the data export file, builds the recommendations report with content retrieved from github, and writes the report to S3 as a markdown file  
- Databrew  
  - Optionally creates a databrew project which allows you to review the data export data  
  - Not required by the project to create the report, just a tool if you want to see your data
- Github  
  - Github contains individual markdown files with recommendation building blocks that are selected based on what is found in the data export  
    - For example, if the data export contains use of S3, S3 recommendations are included in the report  

## Report Orchestration  
The report is created when the recommendations.json file is iterated through. There is a recommendations.json file present in each service folder. The file contains a json construct which describes the order to build the report with. Each entry in the construct, typically for each feature of the service, contains details on what and how to look for keywords in the data export billing file. For example:  

    {
      "File": "family-burstable",
      "Parent": "family-header",
      "Service": "RDS|AURORA",
      "Columns": "product_instance_type|line_item_product_code",
      "Keywords": "db.t|AmazonRDS",
      "Description": "Used if any RDS or Aurora instance is found, and its a burstable"
    },

Where:  

- File  
  - The file to add to the report  
  - This is a .md file  
  - Header files are typically used to include titles/headers in the report, there are different types of naming conventions being user:  
    - **mandatory-header**  
      - If the rest of the recommendations file depends on this service being present in the data export billing file, this MUST be the first entry in the recommendations.json file and MUST be called mandatory-header  
      - It MUST include a value in the Columns and Keywords key  
        - This is needed to check if the service is present in the data export billing file  
        - If the keyword is found in the column in the data export billing file, it continues to process the recommendations file  
        - If the keyword is NOT found in the column in the data export billing file, there is no use of the service and therefore none of these recommendations are relevant  
      - If this is NOT included as the first entry in the recommendations.json file, the file continues to be processed  
    - **general-header**  
      - This represents a file that contains header/introduction text for a feature of a service  
      - It does not have any Column or Keyword values as does not require conditional logic to be used  
      - It is always included as general advice
    - ***cccccc*-header**  
      - This represents content to describe a feature (typically the *ccccc*) of the service  
      - Can be used either GENERAL-ly or with conditional logic  
- Parent  
  - The owning header  
  - Used for information only to help build the recommendations file  
- Service  
  - The service that this entry relates to  
- Columns  
  - The column/field in the data export file to look for the Keywords value in  
  - If left blank, there is no column to look in and the File will be included without condition  
  - If more than one column needs to be included, use the | character, the number of keywords must match the number of columns - these are considered ANDs in the logic  
- Keywords  
  - The value to look for in the Column provided  
  - If left blank, there is no field to look in and the File will be included without condition  
  - If more than one keyword needs to be included, use the | character, the number of keywords must match the number of columns - these are considered ANDs in the logic  
- Description  
  - Just a description used in the JSON file to add some meta data to help identify the entry  

### Tips  
- Use the word GENERAL in the Keywords key, leaving the Columns key blank, to include any File with no conditional logic required before including it  
