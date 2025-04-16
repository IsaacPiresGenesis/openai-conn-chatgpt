import asyncio
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosedOK
import base64
import json
import wave
import dotenv
import os

dotenv.load_dotenv()

# Configurações gerais
API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT = os.getenv("OPENAI_ENDPOINT")
VOZ_OPENAI = "nova"
IDIOMA = "pt"
ARQUIVO_RESPOSTA = "saida/audio_resposta.wav"

# Configuração de áudio para gravação
DURACAO_SEGUNDOS = 5
FREQ = 16000
CANAL = 1



async def envia_audio(websocket, caminho):
    print("Enviando audio...")
    with open(caminho, "rb") as f:
        audio_data = f.read()
    b64_audio = base64.b64encode(audio_data).decode("utf-8")

    mensagem = {
        "type": "input_audio_buffer.append",
        "audio": b64_audio
    }
    await websocket.send(json.dumps(mensagem))

async def recebe_audio(websocket):
    print("salvando dados")
    try:
        deltas = ""
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(data)
            if data["type"] == "response.audio.delta":
                print("🔊 Recebendo áudio de resposta...")
                deltas += data["delta"]
                print("Adicionando deltas")
            if data["type"] == "response.audio.done":
                audio_bytes = base64.b64decode(deltas)
                with wave.open(ARQUIVO_RESPOSTA, mode="wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 16 bits = 2 bytes
                    wf.setframerate(24000)
                    wf.writeframes(audio_bytes)

                print(f"✅ Áudio salvo: {ARQUIVO_RESPOSTA}")
    except ConnectionClosedOK:
        print("🔌 Conexão encerrada normalmente pelo servidor.")

async def main():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }

    arquivo_entrada = "audio1.wav"

    ws = await connect(ENDPOINT, additional_headers=headers)
    await envia_audio(ws, arquivo_entrada)
    await recebe_audio(ws)

if __name__ == "__main__":
    asyncio.run(main())
