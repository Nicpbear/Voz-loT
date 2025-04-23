import os
import time
import glob
import json
import paho.mqtt.client as paho
import streamlit as st
from PIL import Image
from gtts import gTTS
from googletrans import Translator
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# MQTT Configuración y Callbacks
broker = "157.230.214.127"
port = 1883
client_id = "GIT-HUBC"

message_received = ""

def on_publish(client, userdata, result):
    print("✅ Dato publicado con éxito.\n")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.success(f"📩 Mensaje recibido: {message_received}")

client = paho.Client(client_id)
client.on_message = on_message

# Interfaz de Streamlit
st.title("🎙️ Interfaces Multimodales")
st.subheader("🗣️ Control por Voz")

# Imagen decorativa
image = Image.open("voice_ctrl.jpg")
st.image(image, width=200)

st.markdown("#### Presiona el botón y empieza a hablar:")

# Botón Bokeh para reconocimiento de voz
voice_button = Button(label="🎤 Iniciar Reconocimiento de Voz", width=250)
voice_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value !== "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", { detail: value }));
        }
    };
    recognition.start();
"""))

# Captura de eventos de voz
result = streamlit_bokeh_events(
    voice_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# Procesamiento de comando de voz
if result and "GET_TEXT" in result:
    comando = result.get("GET_TEXT").strip()
    st.info(f"📝 Comando recibido: `{comando}`")
    
    client.on_publish = on_publish
    client.connect(broker, port)
    
    msg = json.dumps({"Act1": comando})
    client.publish("voice_ctrl", msg)

    # Crear carpeta temporal si no existe
    os.makedirs("temp", exist_ok=True)
