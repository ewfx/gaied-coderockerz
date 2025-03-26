# 🚀 Project Name--> Gen AI Based Email Classification and OCR 
#   Team Name--> coderockerz

## 📌 Table of Contents
- [Introduction](#introduction)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)

---

## 🎯 Introduction
We are attempting to create a solution for Gen AI-Based Email Classification and OCR.
We are using Google Gemini here. Apart from classifying the emails into defines groups/categories, we are also calculating similarity
score.
 
🖼️ Screenshots:

Screenshot->  https://drive.google.com/file/d/1m6CogP-v6lOGYmc-NHXKtc6784XLFgfe/view?usp=share_link



## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone [https://github.com/your-repo.git](https://github.com/ewfx/gaied-coderockerz.git)
   ```
2. Install dependencies  
   ```sh
   Ensure that you have set up your Google Cloud environment:

3) Create a Google Cloud project.

Enable the Vertex AI API.

Authenticate your application to access the API. You can do this by running:
--> Ensure that you have set up your Google Cloud environment:

a)Create a Google Cloud project.

b)Enable the Vertex AI API.

c)Authenticate your application to access the API. You can do this by running:
gcloud auth application-default login

4) Set up your Python environment:

Install Python.

Install the required libraries:

pip install python-dotenv google-cloud-aiplatform

pip install python-dotenv google-cloud-aiplatform
   ```
3. Run the project  
   ```sh
   python my_script.py
   ```

Challenges Faced:
Challenges:
	1.	Handling Ambiguity in Language
	•	Emails and documents often contain vague or context-dependent information, making accurate classification difficult.
	2.	Data Privacy & Security
	•	Ensuring compliance with GDPR, HIPAA, or internal corporate policies when processing sensitive data.
	3.	Integration with Legacy Systems
	•	Many organizations rely on outdated infrastructure, making seamless AI integration complex.
	4.	Scalability & Performance
	•	Handling large volumes of unstructured data efficiently while maintaining low latency in routing.
	5.	Bias & Model Accuracy
	•	Avoiding bias in AI predictions and ensuring high accuracy across different languages, industries, and document formats.

Tech Used: Python

