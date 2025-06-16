# 🗣️ AI Voice Assistant (FastAPI + Whisper + GPT-4o + Twilio)

This is a fully automated voice-based AI assistant that:

- Receives incoming phone calls via **Twilio**
- Transcribes user speech using **OpenAI Whisper**
- Classifies intent and generates contextual replies using **GPT-4o**
- Speaks responses back to the user using **Twilio**'s voice API (Polly-supported voices)

---

## ⚙️ Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg (Required by Whisper)

Install FFmpeg for audio decoding:

- **Ubuntu/Debian**
  ```bash
  sudo apt update && sudo apt install ffmpeg
  ```
- **Arch Linux**
  ```bash
  sudo pacman -S ffmpeg
  ```
- **macOS (Homebrew)**
  ```bash
  brew install ffmpeg
  ```
- **Windows (Chocolatey)**
  ```bash
  choco install ffmpeg
  ```

### 3. Install Ngrok (For Public URL Exposure)

Ngrok is required to expose your local FastAPI server to the internet (for Twilio to reach it).

- **Ubuntu/Debian**
  ```bash
  sudo snap install ngrok
  ```
- **Arch Linux**
  ```bash
  yay -S ngrok
  ```
- **macOS (Homebrew)**
  ```bash
  brew install ngrok
  ```
- **Windows (Chocolatey)**
  ```bash
  choco install ngrok
  ```

Or download directly: https://ngrok.com/download

> You don't need to run Ngrok manually — the app starts it automatically via `ngrok_twilio_setup.py`.

---

### 4. Create a `.env` File

Create a `.env` file in the project root with your credentials:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
```

---

### 5. Run the Application

Start the FastAPI server:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

What happens:
- Ngrok tunnel is launched automatically
- Twilio webhook is updated dynamically
- Whisper model is loaded into memory
- FastAPI begins serving on port `8000`

Visit the app (if UI exists) at:

```
http://localhost:8000
```

---

## 📞 Example Use Case

1. Dial the Twilio number from your `.env`
2. Say:  
   > “Hi, I need to refill my prescription.”
3. System flow:
   - Audio is transcribed using Whisper
   - Intent classified as `prescription_refill`
   - GPT-4o generates a contextual response
   - Response is synthesized and spoken back to the user via Twilio

---

## 📌 Production Notes for Healthcare Use

### 1. No Separate Intent Classifier Needed
GPT-4o handles both:
- Intent detection (via structured prompt engineering)
- Natural response generation  
This reduces infra complexity and cost — no external NLU or ML model required.

### 2. Storage & Logging Strategy
Use:
- **Amazon S3** for storing MP3 files
- **DynamoDB** or any NoSQL DB for logging transcripts, classifications, timestamps

Benefits:
- Durable storage for audits or retraining
- Decouples compute from storage
- Supports tracing and debugging

### 3. Knowledge-Driven Answers with Vector Stores
For accurate answers to hospital-specific queries:
- Integrate a vector store like **Pinecone** or **ChromaDB**
- Embed PDF/docs of hospital policies, FAQs
- Retrieve context chunks and pass to GPT for better factual grounding

### 4. Scalable Twilio Architecture
To support multiple simultaneous callers:
- Assign multiple numbers/webhooks per use-case or geography
- Use **async** FastAPI endpoints with concurrency
- Scale using containers or Twilio SIP infrastructure
- Consider **TaskRouter** for routing logic

---

## ✅ You're All Set

Enjoy your multilingual, voice-enabled, real-time AI assistant!

---



## 👨‍💻 Author

Maheshvar Chandrasekar  
https://linkedin.com/in/maheshvar | maheshvarchandrasekar96@gmail.com
