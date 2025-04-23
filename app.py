import os
import time
import json
import paho.mqtt.client as paho
import streamlit as st
from PIL import Image
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# --- CONFIGURACIÓN MQTT ---
BROKER = "157.230.214.127"
PORT = 1883
CLIENT_ID = "CONTROL-VOZ-MQTT"

message_received = ""

def on_publish(client, userdata, result):
    print("✅ Mensaje MQTT enviado.")

def on_message(client, userdata, message):
    global message_received
    time.sleep(1)
    message_received = str(message.payload.decode("utf-8"))
    st.success(f"📩 MQTT dice: {message_received}")

client = paho.Client(CLIENT_ID)
client.on_message = on_message

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Control por Voz", layout="centered")
st.markdown("""
    <style>
    .big-title { font-size:36px; font-weight:bold; text-align:center; color:#4CAF50; }
    .section-title { font-size:24px; margin-top:30px; color:#333; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🎧 Sistema de Control por Voz con MQTT</p>', unsafe_allow_html=True)

# Imagen decorativa
st.image("voice_ctrl.jpg", width=250, caption="Control por Voz Activado")

# Expansor para instrucciones
with st.expander("🧭 ¿Cómo usar esta aplicación?"):
    st.markdown("""
    1. Haz clic en el botón de inicio.
    2. Di una orden en voz alta como `"encender luz"` o `"apagar motor"`.
    3. Tu comando será enviado vía MQTT al servidor remoto.
    4. Si todo sale bien, verás la respuesta abajo.
    """)

# Botón Bokeh personalizado
st.markdown('<p class="section-title">🎙️ Presiona para hablar</p>', unsafe_allow_html=True)

stt_button = Button(label="🔵 Iniciar Reconocimiento de Voz", width=300)
stt_button.js_on_event("button_click", CustomJS(code="""
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

# Captura del evento
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listener",
    refresh_on_update=False,
    override_height=100,
    debounce_time=0
)

# Resultado del reconocimiento
if result and "GET_TEXT" in result:
    command = result.get("GET_TEXT").strip()

    st.markdown('<p class="section-title">📋 Comando Reconocido:</p>', unsafe_allow_html=True)
    st.code(command, language='markdown')

    client.on_publish = on_publish
    client.connect(BROKER, PORT)
    msg = json.dumps({"Act1": command})
    client.publish("voice_ctrl", msg)

    os.makedirs("temp", exist_ok=True)
