from openai import OpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Define the response data structure
class Response(BaseModel):
    transcript: str
    language: str
    language_code: str
    intent: str
    response: str

# Define the API request function
def gpt_api_call(transcript, model="gpt-4o"):
    client = OpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")

    # System prompt describing the assistant's role
    system_prompt = """You are a multilingual healthcare assistant that helps patients with various healthcare-related inquiries. 
    You should be able to classify patient inquiries into categories such as appointment scheduling, billing inquiries, and prescription refills. 
    Additionally, you generate responses based on these inquiries with the context provided."""

    # Prompt to classify intent and generate a response
    prompt = (
        f"""A patient has sent a message. The message has been transcribed as follows:
        "{transcript}"

        Your task is to:
        1. Classify the intent of the message into one of the following categories:
            - "appointment_scheduling"
            - "billing_inquiry"
            - "prescription_refill"
            - "general_inquiry"
            - "insurance_coverage"
        2. Generate an appropriate response to the patient's message in the same language as the message.
        3. Return the result in a structured JSON format as follows:

        {{
            "transcript": "{transcript}",
            "language": "<language_name>",
            "language_code": "<twilio_language_code>",
            "intent": "<classified_intent>",
            "response": "<generated_response>"
        }}

        Make sure the language_code field uses one of the following supported Twilio codes:
        - "en-US" for English (US)
        - "es-ES" for Spanish (Spain)
        - "fr-FR" for French (France)
        - "de-DE" for German
        - "it-IT" for Italian
        - "hi-IN" for Hindi
        - "ja-JP" for Japanese

        If the language is not one of these, return "NA" for the language_code.

        Ensure the response is helpful, polite, and culturally appropriate.
        """)

    try:
        # Request GPT API completion with the provided prompt
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format=Response
        )
    except Exception as e:
        print(f"Error in GPT API: {e}")
        return None

    # Return the JSON response content
    response_dict = json.loads(response.choices[0].message.content)
    print(response_dict)
    return response_dict
