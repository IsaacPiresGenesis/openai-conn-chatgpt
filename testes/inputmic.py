import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import queue
import wave


fs=44100
duration = 5  # seconds
# myrecording = sd.rec(duration * fs, samplerate=fs, channels=1, dtype='float64')
# print ("Recording Audio")
# sd.wait()
# print ("Audio recording complete , Play Audio")
# sd.play(myrecording, fs)
# sd.wait()
# print ("Play Audio Complete")



q_audio = queue.Queue()

def callback(indata, frames, time, status):
    print(indata)
    if status:
        print(status)
    q_audio.put(indata.copy())
    

print("🎙️ Gravando...")
with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        frames = []
        for _ in range(int(fs * duration)):
            frames.append(q_audio.get())
        print("Gravado...")
        audio_data = np.concatenate(frames)
        arquivo = "entrada_temp.wav"
        with wave.open(arquivo, mode="wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())