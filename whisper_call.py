import whisper
import math
import logging

# Configure logging
logger = logging.getLogger("whisper")
logger.setLevel(logging.INFO)

# Only add handler if not already set (to avoid duplicate logs when reloading)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[Whisper] %(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class Speach_to_text:

    def __init__(self):
        logger.info("Loading Whisper model: tiny")
        self.model = whisper.load_model("tiny")
        logger.info("Whisper model loaded successfully.")

    def transcribe(self, mp3_file):
        logger.info(f"Transcribing file: {mp3_file}")
        result = self.model.transcribe(mp3_file)

        text = result["text"]
        avg_logprob = result["segments"][0]["avg_logprob"]

        confidence_score = self.calculate_confidence(avg_logprob)

        logger.info(f"Transcript: {text}")
        logger.info(f"Avg logprob: {avg_logprob:.4f}")
        logger.info(f"Confidence score: {confidence_score:.4f}")
        logger.info(f"Returning transcript and confidence.")

        return text, confidence_score

    def calculate_confidence(self, avg_logprob):
        confidence_score = 1 / (1 + math.exp(-avg_logprob))
        return confidence_score
