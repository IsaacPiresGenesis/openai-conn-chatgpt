# example requires websocket-client library:
# pip install websocket-client

import os
import json
import websocket
import base64
import struct
import soundfile as sf

API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT = os.getenv("OPENAI_ENDPOINT")
ARQUIVO_RESPOSTA = "saida/audio_resposta.wav"

headers = [
    "Authorization: Bearer " + API_KEY,
    "OpenAI-Beta: realtime=v1"
]

def on_open(ws):
    print("Connected to server.")

def on_message(message):
    print("Received event:", json.dumps(data, indent=2))
    while True:
        data = json.loads(message)

        if data.get("type") == "audio":
            print("🔊 Recebendo áudio de resposta...")
            b64_audio = data["audio"]
            audio_bytes = base64.b64decode(b64_audio)

            with open(ARQUIVO_RESPOSTA, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ Áudio salvo: {ARQUIVO_RESPOSTA}")
            break

ws = websocket.WebSocketApp(
    ENDPOINT,
    header=headers,
    on_open=on_open,
    on_message=on_message,
)

# ... create websocket-client named ws ...

def float_to_16bit_pcm(float32_array):
    clipped = [max(-1.0, min(1.0, x)) for x in float32_array]
    pcm16 = b''.join(struct.pack('<h', int(x * 32767)) for x in clipped)
    return pcm16

def base64_encode_audio(float32_array):
    pcm_bytes = float_to_16bit_pcm(float32_array)
    encoded = base64.b64encode(pcm_bytes).decode('ascii')
    return encoded

def send_audio():
    print("enviando audio")
    files = [
        'audio1.wav',
    ]

    for filename in files:
        data, samplerate = sf.read(filename, dtype='float32')  
        channel_data = data[:, 0] if data.ndim > 1 else data
        base64_chunk = base64_encode_audio(channel_data)
        
        # Send the client event
        event = {
            "type": "input_audio_buffer.append",
            "audio": base64_chunk
        }
        ws.send(json.dumps(event))

ws.run_forever()