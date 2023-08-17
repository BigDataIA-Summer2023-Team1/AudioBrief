## AudioBrief: Live application Links :octopus:

- Please use this application responsibly, as we have limited free credits remaining.
### Production Links
[![codelabs](https://img.shields.io/badge/Initial%20Plan%20Documentation-4285F4?style=for-the-badge&logo=codelabs&logoColor=white)](https://codelabs-preview.appspot.com/?file_id=1tawz6aVeswcHqI2OKAxYyYzYdJ5Nxs-1t2lzuXzI5OU)

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](http://34.138.113.236:30006)

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](http://34.138.113.236:30005/docs)

[![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-007A88?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)](http://34.138.113.236:8080)

[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](http://34.138.113.236:6379)

### Initial Plan
[![colab-notebook](https://img.shields.io/badge/POC%20Notebook-yellow?style=for-the-badge&logo=codelabs&logoColor=white)](https://colab.research.google.com/drive/1COctuUYK7zId6TwHbA3vvXOj1GPeIDFI?usp=sharing)

## Problem Statement :memo:
The aim of this project is to develop an inclusive and user-friendly application that caters to the needs of the blind community and individuals who are not fond of reading books by providing them with an accessible and engaging platform to convert written content into audio books and obtain summarized chapter insights.

The application seeks to address two key challenges:
Accessibility for the Blind: The visually impaired face significant barriers when accessing printed content, limiting their access to literature and knowledge. This application aims to provide a seamless solution by converting written material into audio books using text-to-speech technology, enabling blind users to enjoy books effortlessly.
Engaging Reading Experience: For individuals who do not enjoy traditional reading, the application will offer a summarization feature that provides concise and insightful overviews of each chapter. By doing so, it enhances user engagement and encourages more people to explore literature and gain knowledge through an alternative medium.
The successful development of this application will empower the visually impaired community and inspire more individuals to engage with literature, promoting knowledge dissemination and enriching the lives of users from diverse backgrounds.


## Project Goals :dart:


## Technologies Used :computer:
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)
[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)
[![GitHub Actions](https://img.shields.io/badge/Github%20Actions-282a2e?style=for-the-badge&logo=githubactions&logoColor=367cfe)](https://github.com/features/actions)
![Google Cloud Run](https://img.shields.io/badge/Google_Cloud-Green?style=for-the-badge&logo=google-cloud&logoColor=white)


## Data Source :flashlight:
1. https://www.kaggle.com/datasets/nahidcse/pdfdrive-ebook-data-downloads-and-metadata <br>
PDFDrive eBook Data: Downloads & Metadata contains information about more than 9000 eBooks available on the PDFDrive website. The dataset includes the URL, title, author, category, publication date, page count, file size (in MB), and the number of times each eBook has been downloaded. The data was gathered by web scraping the PDFDrive website. This data is scrapped on May 9th 2023.
- ID: This column contains a unique identifier for each eBook or row in this dataset.

- URL: This column contains the web link or URL for each eBook on the PDFDrive website.

- Title: This column contains the title of each eBook as listed on the PDFDrive.

- Author: This column contains the name of the author(s) of each eBook.

- Category: This column contains the category or genre of each eBook as listed on the PDFDrive website, such as Technology, Biology, Time Management, etc.

- Publish: This column contains the publication year of each eBook.

- Page: This column contains the number of pages of each eBook as listed on the PDFDrive website.

- Size (MB): This column contains the file size of each eBook in megabytes (MB).

- Downloads: This column contains the number of times each eBook has been downloaded from the PDFDrive website as of the time the data was scraped.



## Architecture Diagram


## Project Structure
```
📦 
├─ .github
│  └─ workflows
│     └─ test.yml
├─ .gitignore
├─ LICENSE
├─ Makefile
├─ README.md
├─ airflows
│  ├─ .gitignore
│  ├─ Dockerfile
│  ├─ dags
│  │  ├─ adhoc_scrape.py
│  │  └─ scrape.py
│  ├─ requirements.txt
│  └─ utils
│     ├─ __init__.py
│     ├─ cloud_sql.py
│     ├─ file_processing.py
│     ├─ gcs_service.py
│     ├─ logger.py
│     └─ pub_sub.py
├─ api
│  ├─ Dockerfile
│  ├─ audio_test.py
│  ├─ main.py
│  ├─ models
│  │  └─ user.py
│  ├─ requirements.txt
│  └─ utils
│     ├─ cloud_logger.py
│     ├─ cloud_sql.py
│     ├─ gcs_service.py
│     ├─ jwt_validations.py
│     └─ rate_limiter.py
├─ cloud-functions
│  ├─ process_chapters
│  │  ├─ cloud_logger.py
│  │  ├─ file_processing.py
│  │  ├─ main.py
│  │  ├─ pub_sub.py
│  │  └─ requirements.txt
│  ├─ summerize_documents
│  │  ├─ main.py
│  │  ├─ requirements.txt
│  │  └─ utils.py
│  └─ synthesize_long_audio
│     ├─ main.py
│     └─ requirements.txt
├─ dataset
│  ├─ pdf_data.csv
│  └─ test-data.csv
├─ demo-deck
│  ├─ final-presentation
│  │  └─ scrape.py
│  └─ project-plan
│     └─ pdf-scarpe.js
├─ docker-compose-local.yml
├─ frontend
│  ├─ Dockerfile
│  ├─ main.py
│  ├─ pages
│  │  ├─ auth.py
│  │  └─ summary.py
│  └─ requirements.txt
└─ terraform
   ├─ Makefile
   ├─ install.sh
   ├─ main.tf
   ├─ output.tf
   ├─ terraform.tfvars
   └─ variables.tf
```
©generated by [Project Tree Generator](https://woochanleee.github.io/project-tree-generator)

## How to run Application locally
To run the application locally, follow these steps:
1. Clone the repository to get all the source code on your machine.

2. Install docker desktop on your system

3. Create a .env file in the root directory with the following variables:
    ``` 
      # Snowflake Variables
    ```

4. Once you have set up your environment variables, Start the application by executing
  ``` 
    Make build-up
  ```

5. Once the docker containers spin up, Access the application at following links
    ``` 
     1. Stremlit UI: http://localhost:30006/
    ```

6. To delete all active docker containers execute
     ``` 
     Make down
     ``` 

## References



## Team Information and Contribution

Name | Contributions 
--- | --- |
Sanjana Karra | Cloud functions for converting TTS and store to Cloud SQL & Buckets, function to generate the summary to chapters 
Nikhil Reddy Polepally | Designed streamlit screens, Build API for the use cases with rate limmiter
Shiva Sai Charan Ruthala | Airflow Pipeline with threading, Deployment and Infrastructure setup, Logging, User Dashboard, Testing, Documentation
