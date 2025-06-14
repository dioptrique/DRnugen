# Example filename: main.py
import subprocess
import logging
from deepgram.utils import verboselogs
import threading
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)
from yad import run_yad_with_timeout
from nugen import fact_check
from system_notif import notify_linux, popup_text
import threading
import json
import time

def keep_alive_loop(ws, interval=5):
    keep_alive_msg = json.dumps({"type": "KeepAlive"})
    while True:
        try:
            ws.send(keep_alive_msg)
            time.sleep(interval)
        except Exception as e:
            print(f"KeepAlive error or connection closed: {e}")
            break

# 🔐 Your Deepgram API Key
DEEPGRAM_API_KEY = "963b0fb257c544b1539aeb8fa53f8796b2ef8fea"

# 🎙️ PulseAudio monitor device
MONITOR_DEVICE = "alsa_output.pci-0000_00_1f.3-platform-skl_hda_dsp_generic.HiFi__hw_sofhdadsp__sink.monitor"

# 🎧 FFmpeg command to capture system audio
FFMPEG_COMMAND = [
    'ffmpeg',
    '-f', 'pulse',
    '-i', MONITOR_DEVICE,
    '-ac', '1',
    '-ar', '16000',
    '-f', 's16le',
    '-loglevel', 'quiet',
    'pipe:1'
]

# URL for the realtime streaming audio you would like to transcribe
URL = "http://stream.live.vc.bbcmedia.co.uk/bbc_world_service"


def main():
    paragraph =[]
    try:
        # use default config
        deepgram: DeepgramClient = DeepgramClient(DEEPGRAM_API_KEY)
        # Create a websocket connection to Deepgram
        dg_connection = deepgram.listen.websocket.v("1")
        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            paragraph.append(sentence)
            print(len(paragraph), "sentences collected")
            new_paragraph = False

            
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        # connect to websocket
        options = LiveOptions(
            model="nova-3",
            encoding="linear16",
            sample_rate=16000,
            channels=1,
            punctuate=True,
            interim_results=False,
            language="en-US",
            diarize=True
        )
        # Set up loggin
        print("\n\nPress Enter to stop recording...\n\n")
        if dg_connection.start(options) is False:
            print("Failed to start connection")
            return
        # After creating your connection dg_connection
        keep_alive_thread = threading.Thread(target=keep_alive_loop, args=(dg_connection,), daemon=True)
        keep_alive_thread.start()

        # ✅ Start FFmpeg subprocess
        process = subprocess.Popen(FFMPEG_COMMAND, stdout=subprocess.PIPE, bufsize=0)

        while True:
            data = process.stdout.read(1024)
            if not data:
                print("No more data from FFmpeg, stopping...")
                break
            # Check if data is silence
            if data == b'\x00' * len(data):
                if len(paragraph) > 0:
                    # Call fact-checking API with the collected paragraph
                    claim = " ".join(paragraph)

                    print(f"Fact-checking claim: {claim}")
                    # Here you would call your fact-checking API
                    # For example:
                    response = fact_check(claim)
                    if response:
                        print(f"Fact-checking result: {response}")
                        notify_linux("💡 Dr Nugen", response)
                        popup_text("💡 Dr Nugen", response)
                    else:
                        print("No response from fact-checking API.")

                paragraph = []
                continue
            #print(len(data), "bytes of audio data received")
            dg_connection.send(data)
                
        # Indicate that we've finished
        dg_connection.finish()
        print("Finished")
    except Exception as e:
        print(f"Could not open socket: {e}")
        return
    finally:
        dg_connection.finish()
        process.kill()

if __name__ == "__main__":
    main()
