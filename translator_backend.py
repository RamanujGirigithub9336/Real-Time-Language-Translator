# translator_backend.py
import os
import torch
import whisper
import speech_recognition as sr
from gtts import gTTS
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import sounddevice as sd
import soundfile as sf
import platform

# Load models
whisper_model = whisper.load_model("medium")
recognizer = sr.Recognizer()
translator_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")

LANGUAGES = {
    "English": "eng_Latn", "Hindi": "hin_Deva", "Bengali": "ben_Beng", "Punjabi": "pan_Guru",
    "Marathi": "mar_Deva", "Gujarati": "guj_Gujr", "Tamil": "tam_Taml", "Telugu": "tel_Telu",
    "Kannada": "kan_Knda", "Malayalam": "mal_Mlym", "Urdu": "urd_Arab", "Assamese": "asm_Beng",
    "Bhojpuri": "bho_Deva", "Maithili": "mai_Deva", "Konkani": "kok_Deva", "Sanskrit": "san_Deva",
    "Rajasthani": "raj_Deva", "Awadhi": "awa_Deva", "Magahi": "mag_Deva", "Odia": "ory_Orya",
    "Sindhi": "snd_Arab", "Nepali": "npi_Deva", "Kashmiri": "kas_Arab", "Dogri": "doi_Deva",
    "Manipuri": "mni_Beng", "Santali": "sat_Olck", "Bodo": "brx_Deva"
}

WHISPER_LANG_CODES = {
    "English": "en", "Hindi": "hi", "Bengali": "bn", "Tamil": "ta", "Telugu": "te",
    "Gujarati": "gu", "Kannada": "kn", "Malayalam": "ml", "Marathi": "mr", "Punjabi": "pa",
    "Urdu": "ur", "Assamese": "as", "Bhojpuri": "hi", "Maithili": "hi", "Konkani": "mr",
    "Sanskrit": "hi", "Rajasthani": "hi", "Awadhi": "hi", "Magahi": "hi", "Odia": "or",
    "Sindhi": "ur", "Nepali": "hi", "Kashmiri": "ur", "Dogri": "hi", "Manipuri": "bn",
    "Santali": "hi", "Bodo": "hi"
}

GTTS_LANG_CODES = {
    "English": "en", "Hindi": "hi", "Bengali": "bn", "Tamil": "ta", "Telugu": "te",
    "Gujarati": "gu", "Kannada": "kn", "Malayalam": "ml", "Marathi": "mr", "Punjabi": "pa",
    "Urdu": "ur", "Assamese": "bn", "Bhojpuri": "hi", "Maithili": "hi", "Konkani": "mr",
    "Sanskrit": "hi", "Rajasthani": "hi", "Awadhi": "hi", "Magahi": "hi", "Odia": "hi",
    "Sindhi": "ur", "Nepali": "hi", "Kashmiri": "ur", "Dogri": "hi", "Manipuri": "bn",
    "Santali": "hi", "Bodo": "hi"
}

def record_audio(duration=6, sample_rate=16000):
    num_frames = int(duration * sample_rate)
    audio = sd.rec(num_frames, samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return audio.flatten(), sample_rate

def transcribe_audio(audio_path, lang_code="en"):
    try:
        whisper_result = whisper_model.transcribe(audio_path, language=lang_code, task="transcribe")
        text = whisper_result.get("text", "").strip()
    except Exception:
        text = ""

    if not text or len(text.split()) < 3:
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language=f"{lang_code}-IN")
        except Exception:
            text = "[Unrecognized speech]"

    return text.strip()

def translate_text(text, source_lang, target_lang):
    tokenizer.src_lang = LANGUAGES[source_lang]
    tgt_lang_code = LANGUAGES[target_lang]
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        translated = translator_model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_lang_code)
        )
    return tokenizer.decode(translated[0], skip_special_tokens=True)

def speak_text(text, target_lang):
    lang_code = GTTS_LANG_CODES.get(target_lang, "en")
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save("output.mp3")
        system = platform.system().lower()
        if system == "windows":
            os.system("start output.mp3")
        elif system == "darwin":
            os.system("afplay output.mp3")
        else:
            os.system("mpg123 output.mp3")
    except Exception as e:
        print("TTS error:", e)
 
def process_translation(source_lang, target_lang):
    audio, sr_rate = record_audio()
    temp_file = "temp.wav"
    sf.write(temp_file, audio, sr_rate)

    whisper_lang = WHISPER_LANG_CODES.get(source_lang, "en")
    transcription = transcribe_audio(temp_file, whisper_lang)
    translation = translate_text(transcription, source_lang, target_lang)
    speak_text(translation, target_lang)

    os.remove(temp_file)
    return transcription, translation
