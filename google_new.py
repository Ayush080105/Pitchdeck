from google.cloud import speech
from pydub import AudioSegment
import io
import tempfile

def convert_to_wav_linear16(input_path: str) -> str:
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio.export(temp_wav.name, format="wav")
    return temp_wav.name

def transcribe_streaming_google(audio_path: str, language_code: str = "en-US") -> str:
    audio_path = convert_to_wav_linear16(audio_path)

    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=False,
        single_utterance=False,
    )

    def generate_requests():
        with io.open(audio_path, "rb") as audio_file:
            while chunk := audio_file.read(4096):
                yield speech.StreamingRecognizeRequest(audio_content=chunk)

    responses = client.streaming_recognize(
        config=streaming_config,
        requests=generate_requests()
    )

    transcript = ""
    for response in responses:
        for result in response.results:
            if result.is_final:
                transcript += result.alternatives[0].transcript + " "

    return transcript.strip()
