import os
import re
from typing import List, Dict, Tuple
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
from dotenv import load_dotenv
import google.auth
from google.cloud import aiplatform
from collections import Counter

# Load environment variables
load_dotenv()
EMAIL_STORAGE_PATH = os.getenv("EMAIL_STORAGE_PATH", "emails")
PROJECT_ID = os.getenv("PROJECT_ID")  # Google Cloud Project ID
LOCATION = os.getenv("LOCATION", "us-central1")  # Region

# Initialize Vertex AI
aiplatform.init(project=PROJECT_ID, location=LOCATION)


# Define email categories, entities and intents.
EMAIL_CATEGORIES = [
    "Account Inquiry",
    "Transaction Dispute",
    "Loan Application",
    "Mortgage Inquiry",
    "Fraud Report",
    "Service Request",
    "Complaint",
    "Feedback",
    "General Inquiry",
]
EMAIL_ENTITIES = [
    "Account Number",
    "Transaction ID",
    "Customer Name",
    "Phone Number",
    "Email Address",
    "Date",
    "Amount",
    "Product Type",
]
EMAIL_INTENTS = [
    "Request Information",
    "Report a Problem",
    "Apply for a Service",
    "Provide Feedback",
    "Seek Help",
]
EMAIL_SENTIMENTS = ["Positive", "Negative", "Neutral"]


def clean_email_content(email_content: str) -> str:
    """
    Cleans the email content by removing HTML tags, extraneous formatting,
    and noise.

    Args:
        email_content (str): The raw email content.

    Returns:
        str: The cleaned email content.
    """
    # Remove HTML tags
    cleaned_text = re.sub(r"<[^>]+>", "", email_content)
    # Remove extraneous whitespace and newline characters
    cleaned_text = " ".join(cleaned_text.split())
    return cleaned_text



def extract_email_metadata(email_bytes: bytes) -> Dict[str, str]:
    """
    Extracts relevant metadata from the email.

    Args:
        email_bytes (bytes): The raw email bytes.

    Returns:
        dict: A dictionary containing the extracted metadata.
    """
    parser = BytesParser(policy=policy.default)
    email_message = parser.parsebytes(email_bytes)

    sender_email = email_message.get("From")
    subject = email_message.get("Subject")
    timestamp = email_message.get("Date")
    # attachments = [
    #     filename
    #     for filename in email_message.iter_attachments()
    # ]  # Simplified attachment extraction
    attachments = []
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_filename():
                attachments.append(part.get_filename())

    return {
        "sender_email": str(sender_email),
        "subject": str(subject),
        "timestamp": str(timestamp),
        "attachments": attachments,
    }



def classify_email(email_content: str) -> str:
    """
    Classifies the email into predefined categories using a LLM (Gemini).

    Args:
        email_content (str): The cleaned email content.

    Returns:
        str: The classified email category.
    """
    prompt = f"""
    Classify the following email into one of these categories: {', '.join(EMAIL_CATEGORIES)}.
    Provide *only* the category name.
    Email: {email_content}
    """
    try:
        response = client.chat_model.predict(prompt).text
        return response.strip()
    except Exception as e:
        print(f"Error classifying email: {e}")
        return "General Inquiry"  # Default category



def extract_entities(email_content: str) -> Dict[str, str]:
    """
    Extracts key data points from the email using a LLM (Gemini).

    Args:
        email_content (str): The cleaned email content.

    Returns:
        dict: A dictionary containing the extracted entities.
    """
    prompt = f"""
    Extract the following information from the email. If a piece of information is not present, output 'N/A'.
    {chr(10).join([f'{entity}:' for entity in EMAIL_ENTITIES])}
    Email: {email_content}
    """
    try:
        response = client.chat_model.predict(prompt).text
        lines = response.splitlines()
        extracted_entities = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                extracted_entities[key.strip()] = value.strip()
        return extracted_entities
    except Exception as e:
        print(f"Error extracting entities: {e}")
        return {entity: "N/A" for entity in EMAIL_ENTITIES}



def recognize_intent(email_content: str) -> str:
    """
    Determines the primary purpose of the email using a LLM (Gemini).

    Args:
        email_content (str): The cleaned email content.

    Returns:
        str: The recognized intent.
    """
    prompt = f"""
    What is the primary intent of this email? Choose one of the following: {', '.join(EMAIL_INTENTS)}.
    Email: {email_content}
    """
    try:
        response = client.chat_model.predict(prompt).text
        return response.strip()
    except Exception as e:
        print(f"Error recognizing intent: {e}")
        return "General Inquiry"  # Default intent



def analyze_sentiment(email_content: str) -> str:
    """
    Analyzes the tone of the email using a LLM (Gemini).

    Args:
        email_content (str): The cleaned email content.

    Returns:
        str: The sentiment of the email.
    """
    prompt = f"""
    What is the sentiment of this email? Choose one of the following: {', '.join(EMAIL_SENTIMENTS)}.
    Email: {email_content}
    """
    try:
        response = client.chat_model.predict(prompt).text
        return response.strip()
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return "Neutral"  # Default sentiment



def summarize_email(email_content: str) -> str:
    """
    Generates a concise summary of the email's content using a LLM (Gemini).

    Args:
        email_content (str): The cleaned email content.

    Returns:
        str: The summarized email content.
    """
    prompt = f"""
    Summarize the following email in three sentences or less:
    {email_content}
    """
    try:
        response = client.chat_model.predict(prompt).text
        return response.strip()
    except Exception as e:
        print(f"Error summarizing email: {e}")
        return "Summary not available."



def route_email(
    category: str,
    entities: Dict[str, str],
    intent: str,
    sentiment: str,
    summary: str,
    email_metadata: Dict[str, str]
) -> Tuple[str, Dict[str, str]]:
    """
    Routes the email based on the analysis and triggers appropriate actions.

    Args:
        category (str): The classified email category.
        entities (dict): The extracted entities.
        intent (str): The intent of the email.
        sentiment (str): The sentiment of the email.
        summary (str): A summary of the email.
        email_metadata (dict): extracted email metadata

    Returns:
        tuple: A tuple containing the routing destination and any actions taken.
    """
    # Default routing
    destination = "General Inquiry Department"
    actions = {}

    # Routing logic based on category and other factors
    if category == "Fraud Report":
        destination = "Fraud Department"
        actions["create_ticket"] = {"system": "CRM", "priority": "High"}
        actions["send_acknowledgment"] = {
            "type": "FraudReportReceived",
            "to": email_metadata["sender_email"],
        }
    elif category == "Loan Application":
        destination = "Loan Department"
        actions["create_ticket"] = {"system": "LoanOriginationSystem", "priority": "Medium"}
    elif category == "Account Inquiry":
        destination = "Customer Service Department"
        actions["send_acknowledgment"] = {
            "type": "AccountInquiryReceived",
            "to": email_metadata["sender_email"],
        }
    elif category == "Transaction Dispute":
        destination = "Dispute Resolution Department"
        actions["create_ticket"] = {"system": "DisputeTrackingSystem", "priority": "High"}
    elif category == "Mortgage Inquiry":
        destination = "Mortgage Department"
        actions["create_ticket"] = {"system": "MortgageOriginationSystem", "priority": "Medium"}
    elif category == "Service Request":
        destination = "Customer Service Department"
        actions["create_ticket"] = {"system": "CRM", "priority": "Medium"}
    elif category == "Complaint":
        destination = "Customer Relations Department"
        actions["create_ticket"] = {"system": "CRM", "priority": "High"}
        if sentiment == "Negative":
            actions["escalate"] = True
    elif category == "Feedback":
        destination = "Product Development Department"
    elif category == "General Inquiry":
        destination = "Customer Service Department"

    # Add a log entry
    print(
        f"Routed to: {destination}, Actions: {actions}, Category: {category}, Intent: {intent}, Sentiment: {sentiment}"
    )
    return destination, actions


def calculate_similarity_score(
    extracted_entities: Dict[str, str], expected_entities: Dict[str, str]
) -> float:
    """
    Calculates a similarity score between extracted and expected entities.
    Uses a simple string matching approach.

    Args:
        extracted_entities (dict): The extracted entities.
        expected_entities (dict): The expected entities.

    Returns:
        float: The similarity score (between 0 and 1).
    """
    match_count = 0
    total_count = 0
    for key in expected_entities:
        if key in extracted_entities:
            total_count += 1
            if extracted_entities[key] == expected_entities[key]:
                match_count += 1
    if total_count == 0:
        return 0.0  # Avoid division by zero
    return match_count / total_count



def process_email(email_bytes: bytes) -> None:
    """
    Processes a single email.

    Args:
        email_bytes (bytes): The raw email bytes.
    """
    try:
        # 1. Extract metadata
        email_metadata = extract_email_metadata(email_bytes)
        print(f"Email metadata: {email_metadata}")

        # 2. Extract the body.
        parser = BytesParser(policy=policy.default)
        email_message = parser.parsebytes(email_bytes)
        if email_message.is_multipart():
            # Iterate over the parts of the email
            for part in email_message.walk():
                # Check if the part is plain text
                if part.get_content_type() == "text/plain":
                    email_content = part.get_payload(decode=True)
                    break
        else:
            # If the email is not multipart, get the payload directly
            email_content = email_message.get_payload(decode=True)
        email_content = email_content.decode("utf-8", errors="ignore")

        # 3. Clean the email content
        cleaned_content = clean_email_content(email_content)
        # print(f"Cleaned email content: {cleaned_content}") #too verbose

        # 4. Analyze the email using GenAI
        category = classify_email(cleaned_content)
        entities = extract_entities(cleaned_content)
        intent = recognize_intent(cleaned_content)
        sentiment = analyze_sentiment(cleaned_content)
        summary = summarize_email(cleaned_content)

        print(f"Category: {category}")
        print(f"Entities: {entities}")
        print(f"Intent: {intent}")
        print(f"Sentiment: {sentiment}")
        print(f"Summary: {summary}")

        # 5. Route the email and trigger actions
        destination, actions = route_email(
            category, entities, intent, sentiment, summary, email_metadata
        )
        print(f"Routing destination: {destination}")
        print(f"Actions: {actions}")

        # 6. Calculate similarity score (example with expected entities)
        expected_entities = {
            "Account Number": "1234567890",
            "Transaction ID": "N/A",
            "Customer Name": "John Smith",
            "Phone Number": "555-123-4567",
            "Email Address": "customer@example.com",
            "Date": "2024-07-24T10:00:00",
            "Amount": "1000",
            "Product Type": "N/A",
        }
        similarity_score = calculate_similarity_score(entities, expected_entities)
        print(f"Similarity Score: {similarity_score:.2f}")

    except Exception as e:
        print(f"Error processing email: {e}")




def create_sample_email() -> bytes:
    """
    Creates a sample email message.

    Returns:
        bytes: The raw bytes of the email message.
    """
    message = EmailMessage()
    message["From"] = "customer@example.com"
    message["To"] = "bank@example.com"
    message["Subject"] = "Urgent: Unauthorized Transaction"
    message["Date"] = "2024-07-24T10:00:00"
    message.set_content(
        """
Dear Bank Support,

I am writing to report an unauthorized transaction on my account.  The transaction was for $1000 on July 23, 2024, and I do not recognize it. My account number is 1234567890. Please investigate this issue immediately.

Sincerely,
John Smith
Phone: 555-123-4567
"""
    )
    # Create an attachment
    attachment_content = b"This is a dummy attachment."
    attachment_filename = "document.txt"
    message.add_attachment(attachment_content, filename=attachment_filename)

    return message.as_bytes()



def main() -> None:
    """
    Main function to process emails from a directory.
    """
    # Ensure the email storage directory exists
    if not os.path.exists(EMAIL_STORAGE_PATH):
        os.makedirs(EMAIL_STORAGE_PATH)

    # Create a sample email if the directory is empty
    if not os.listdir(EMAIL_STORAGE_PATH):
        sample_email_bytes = create_sample_email()
        with open(os.path.join(EMAIL_STORAGE_PATH, "sample_email.eml"), "wb") as f:
            f.write(sample_email_bytes)
        print("Created sample email: sample_email.eml")

    # Process each email file in the directory
    for filename in os.listdir(EMAIL_STORAGE_PATH):
        if filename.endswith(".eml"):
            filepath = os.path.join(EMAIL_STORAGE_PATH, filename)
            try:
                with open(filepath, "rb") as f:
                    email_bytes = f.read()
                print(f"Processing email: {filename}")
                process_email(email_bytes)
            except Exception as e:
                print(f"Error reading or processing email file {filename}: {e}")



if __name__ == "__main__":
    main()
    print("Email processing complete.")

