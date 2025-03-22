import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import azure.cognitiveservices.speech as speechsdk
import numpy as np
import av
import threading


speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
audio_stream_format = speechsdk.audio.AudioStreamFormat(samples_per_second=16000, bits_per_sample=16, channels=1)
audio_input = speechsdk.audio.PushAudioInputStream(audio_stream_format)
audio_config = speechsdk.audio.AudioConfig(stream=audio_input)
recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# WebRTC Client Settings (updated)
rtc_configuration = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
media_stream_constraints = {"audio": True, "video": False}

# Initialize session state
if 'recognized_text' not in st.session_state:
    st.session_state['recognized_text'] = ""

def audio_callback(frame: av.AudioFrame) -> av.AudioFrame:
    audio_data = frame.to_ndarray()
    audio_data = audio_data.mean(axis=1).astype(np.int16).tobytes()  # Convert to mono, int16
    audio_input.write(audio_data)
    return frame

def recognize_continuously():
    while True:
        result = recognizer.recognize_once()
        st.session_state['recognized_text'] = "Recognized: {}".format(result.text)

st.title("Streamlit Web Microphone to Azure Speech SDK")

webrtc_ctx = webrtc_streamer(
    key="speech-recognition",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=rtc_configuration,
    media_stream_constraints=media_stream_constraints,
    audio_processor_factory=lambda: audio_callback,
)

if st.button("Start Recognition"):
    recognition_thread = threading.Thread(target=recognize_continuously)
    recognition_thread.start()

# Display the recognized text from session state
st.write(st.session_state['recognized_text'])
