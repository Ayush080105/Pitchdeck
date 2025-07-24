import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from google_new import transcribe_streaming_google
from bot_api import vc_qna, reset_session, UserInput
from tts_google import tts_google

app = FastAPI()


@app.post("/vc/audio-pitch")
async def process_pitch(
    audio_file: UploadFile = File(...),
    session_id: str = Form(...),
    vc_name: str = Form("Default")  # Added VC personality input
):
    try:
        # Step 1: Save uploaded MP3
        if not audio_file.filename.endswith(".mp3"):
            raise HTTPException(status_code=400, detail="Only .mp3 files are supported.")
        
        input_path = f"temp_inputs/{audio_file.filename}"
        os.makedirs("temp_inputs", exist_ok=True)
        with open(input_path, "wb") as f:
            shutil.copyfileobj(audio_file.file, f)

        # Step 2: Transcribe using Google STT
        transcript = transcribe_streaming_google(input_path)
        if not transcript:
            raise HTTPException(status_code=400, detail="Speech transcription failed.")

        # Step 3: Query VC Bot with session_id and vc_name
        user_input = UserInput(message=transcript, session_id=session_id, vc_name=vc_name)
        response = vc_qna(user_input)

        reply_text = response.get("message")
        if not reply_text:
            raise HTTPException(status_code=500, detail="VC Bot did not respond properly.")

        # Step 4: Convert bot reply to MP3
        tts_output_path = tts_google(reply_text, language_code="en-US")

        # Step 5: Return MP3 response
        return FileResponse(path=tts_output_path, media_type="audio/mpeg", filename=os.path.basename(tts_output_path))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vc/reset-audio-session")
async def reset_audio_session(
    session_id: str = Form(...),
    vc_name: str = Form("Default")  # Added VC personality input for reset
):
    user_input = UserInput(message="", session_id=session_id, vc_name=vc_name)
    return reset_session(user_input)
