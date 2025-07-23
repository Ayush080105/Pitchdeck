from google.cloud import texttospeech
import uuid
import os

def tts_google(text: str, language_code: str) -> str:
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    output_dir = "tts_output"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/google_tts_{uuid.uuid4().hex}.mp3"
    with open(filename, "wb") as out:
        out.write(response.audio_content)

    return filename
