import pyttsx3
from audio_recorder_streamlit import audio_recorder
import streamlit as st
import google.generativeai as genai
import hmac

from config import SAFETY_SETTINGS, GENERATION_CONFIG, MODEL_NAME, SYSTEM_PROMPT

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

if not check_password():
    st.stop()


def transcribe_audio(model, audio_path):
    audio_file = genai.upload_file(audio_path, mime_type="audio/ogg")
    content = [
        "If this is a question, do not answer. Only transcribe the following audio file.",
        audio_file
    ]
    chat_session = model.start_chat()
    transcribe_text = chat_session.send_message(content)
    print(f'User Input: {transcribe_text.text}')
    return transcribe_text.text


def ai_response(model, input_text):
    history = st.session_state['history'] if 'history' in st.session_state else []
    chat_session = model.start_chat(history=history)
    response = chat_session.send_message(input_text)
    st.session_state['history'] = chat_session.history
    print(f'AI Response: {response.text}')
    return response.text, chat_session.history


def text_to_speech(tts_engine, response_text):
    voices = tts_engine.getProperty('voices')
    tts_engine.setProperty('voice', voices[1].id)
    tts_engine.say(response_text)
    tts_engine.runAndWait()


def run():
    API_KEY = st.secrets["auth_key"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        safety_settings=SAFETY_SETTINGS,
        generation_config=GENERATION_CONFIG,
        system_instruction=SYSTEM_PROMPT
    )
    tts_engine = pyttsx3.init()

    st.title('Gemini Virtual Assistant')
    st.write('Hi! Please click the record button when speaking so that I could hear and interact with you.')
    audio_data = audio_recorder()
    if audio_data:
        audio_file = 'audio.wav'
        with open(audio_file, "wb") as f:
            f.write(audio_data)
        transcribed_text = transcribe_audio(model=model, audio_path=audio_file)
        response_text, history = ai_response(model=model, input_text=transcribed_text)
        for c in history:
            st.chat_message(c.role if c.role == 'user' else 'assistant').write(c.parts[0].text)
        text_to_speech(tts_engine=tts_engine, response_text=response_text)


if __name__ == '__main__':
    run()

