from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from whisper_call import Speach_to_text
from gpt import gpt_api_call
from twilio.twiml.voice_response import VoiceResponse
from contextlib import asynccontextmanager
import os, shutil, requests, time, subprocess, sys
from datetime import datetime
from requests.auth import HTTPBasicAuth

speech_to_text = None
ngrok_process = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global speech_to_text, ngrok_process

    print("Running ngrok + Twilio setup...")
    ngrok_process = subprocess.Popen([sys.executable, "ngrok_twilio_setup.py"])
    time.sleep(3)
    print("Loading Whisper model before serving...")
    speech_to_text = Speach_to_text()
    print("Whisper model is ready.")
    yield
    print("Shutting down...")
    if ngrok_process:
        ngrok_process.terminate()
        try:
            ngrok_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ngrok_process.kill()
        print("ngrok tunnel terminated.")

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def main():
    return open("fe.html").read()

@app.post("/upload_audio/")
async def upload_audio(file: UploadFile = File(...)):
    os.makedirs("temp_audio", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(file.filename)[-1] or ".mp3"
    safe_filename = f"user_audio_{timestamp}{file_ext}"
    file_path = os.path.join("temp_audio", safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    transcript, confidence_score = speech_to_text.transcribe(file_path)
    response = gpt_api_call(transcript)

    if not response:
        return {
            "error": "GPT response failed. Please try again."
        }

    return {
        "transcript": transcript,
        "language": response.get("language"),
        "language_code": response.get("language_code"),
        "intent": response.get("intent"),
        "response": response.get("response"),
        "confidence": confidence_score
    }

@app.post("/incoming_call")
async def incoming_call(request: Request):
    response = VoiceResponse()
    response.say("Hello! Please tell me how I can help you after the beep.", voice='Polly.Joanna', language='en-US')
    response.record(
        action="/process_recording",
        method="POST",
        max_length=20,
        timeout=5,
        transcribe=False
    )
    return Response(content=str(response), media_type="application/xml")

@app.post("/process_recording")
async def process_recording(RecordingUrl: str = Form(...)):
    print("Received recording:", RecordingUrl)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("temp_audio", exist_ok=True)
    file_path = f"temp_audio/recorded_call_{timestamp}.wav"

    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    auth = HTTPBasicAuth(TWILIO_SID, TWILIO_AUTH_TOKEN)

    for attempt in range(3):
        r = requests.get(RecordingUrl, stream=True, auth=auth)
        if r.status_code == 200:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            print(f"Recording saved to {file_path}")
            break
        else:
            print(f"[Attempt {attempt+1}] Recording not ready (status {r.status_code}), retrying in 2s...")
            time.sleep(2)
    else:
        return Response(content="<Response><Say>Sorry, there was a problem retrieving your recording.</Say></Response>", media_type="application/xml")

    transcript, confidence = speech_to_text.transcribe(file_path)
    response_data = gpt_api_call(transcript)

    if not response_data:
        twiml = VoiceResponse()
        twiml.say("Sorry, there was a processing error. Please try again later.", voice="Polly.Joanna", language="en-US")
        return Response(content=str(twiml), media_type="application/xml")

    voice = "Polly.Joanna"
    lang = response_data.get("language_code", "en-US")
    if lang == "es-ES": voice = "Polly.Conchita"
    elif lang == "fr-FR": voice = "Polly.Celine"
    elif lang == "de-DE": voice = "Polly.Marlene"
    elif lang == "it-IT": voice = "Polly.Carla"
    elif lang == "hi-IN": voice = "Polly.Aditi"
    elif lang == "ja-JP": voice = "Polly.Mizuki"

    twiml = VoiceResponse()
    if lang == "NA":
        twiml.say("Sorry, I can't speak your language yet. Please try English.", voice="Polly.Joanna", language="en-US")
    else:
        twiml.say(response_data["response"], voice=voice, language=lang)
        twiml.redirect("/follow_up", method="POST")
    return Response(content=str(twiml), media_type="application/xml")

@app.post("/follow_up")
async def follow_up():
    response = VoiceResponse()
    response.say("Do you need any more help? Please respond after the beep.", voice='Polly.Joanna', language='en-US')
    response.record(
        action="/process_recording",
        method="POST",
        max_length=20,
        timeout=5,
        transcribe=False
    )
    return Response(content=str(response), media_type="application/xml")
