#pip install google-genai
#pip install google-cloud-speech
import streamlit as st, os, base64, time
from google import genai
from google.genai import types
from google.cloud import texttospeech
from audio_recorder_streamlit import audio_recorder
from google.cloud import speech
import vertexai

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

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

if not check_password():
    st.stop()

def page_setup():
    st.header("Use a voice bot to interact with your PDF file!", anchor=False, divider="blue")

    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.sidebar.markdown("Non-Streaming Version")




def main():
    
    uploaded_files = st.file_uploader("Choose your pdf file",  accept_multiple_files=False)
    if uploaded_files:
        file_name=uploaded_files.name
        file_upload = client.files.upload(path=file_name)

                    
        audio_bytes = audio_recorder(recording_color="#6aa36f", neutral_color="#e82c58")
        if audio_bytes:
                    
        audio = speech.RecognitionAudio(content=audio_bytes)
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            #sample_rate_hertz=44100,
            language_code="en-US",
            model="default",
            audio_channel_count=2,
            enable_word_confidence=True,
            enable_word_time_offsets=True,
            )
        
        operation = client3.long_running_recognize(config=config, audio=audio)
        
        conversion = operation.result(timeout=90)
                    
        for result in conversion.results:
            #st.write("Transcript: {}".format(result.alternatives[0].transcript))
                pass
                      
        prompt = (result.alternatives[0].transcript)

        response = client.models.generate_content(
            model=MODEL_ID,
            config=types.GenerateContentConfig(
            system_instruction="You are a helpful assistant. Your answers need to be brief and concise.",
            temperature=1.0,
            top_p=0.95,
            top_k=20,
            max_output_tokens=100,
            ),
            contents=[
            types.Content(
            role="user",
            parts=[
            types.Part.from_uri(
            file_uri=file_upload.uri,
            mime_type=file_upload.mime_type),
            ]),
            prompt,
            ]
        )

                        
        file_ = open("spkr.gif", "rb")
            contents = file_.read()
            data_url = base64.b64encode(contents).decode("utf-8")
            file_.close()
            placeholder = st.empty()
            placeholder = st.markdown(
            f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
            unsafe_allow_html=True,
        )
        playsound("output.wav")
        placeholder.empty()

            
if __name__ == '__main__':
    page_setup()
    api_key=st.secrets["auth_key"]
    client = genai.Client(api_key=api_key)
    MODEL_ID = "gemini-2.0-flash-exp"
    vertexai.init(project=projectid, location="us-central1")
    client3 = speech.SpeechClient()
    main()
