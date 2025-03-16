import M5
from audio import Recorder
import time
import os
import urequests
import ujson
import network
import ubinascii
import urandom
import struct
import ujson
import json

SSID = ""
PASSWORD = ""


OPENAI_API_KEY = ""



SAMPLE_RATE = 8000
BITS_PER_SAMPLE = 16
CHANNELS = 2  
RECORD_DURATION = 10
M5.Lcd.setFont(M5.Lcd.FONTS.EFontJA24)

RAW_FILE_URL = "file://flash/res/audio/test.raw"
RAW_FILE_PATH = "/flash/res/audio/test.raw"
WAV_FILE_PATH = "/flash/res/audio/test.wav"

WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"

wlan = network.WLAN(network.STA_IF)
recorder = Recorder(SAMPLE_RATE, BITS_PER_SAMPLE, CHANNELS == 2)
recording = False
processing = False
start_time = None
M5.Lcd.setFont(M5.Lcd.FONTS.EFontJA24)

def connect_wifi():
    wlan.active(True)
    if not wlan.isconnected():
        M5.Lcd.clear()
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.print("Connecting Wi-Fi...")
        print("Connecting to Wi-Fi...")

        wlan.connect(SSID, PASSWORD)
        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        M5.Lcd.clear()
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.print("Wi-Fi Connected!")
        print(f"Wi-Fi Connected! IP: {wlan.ifconfig()[0]}")
        return True
    else:
        M5.Lcd.clear()
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.print("Wi-Fi Failed!")
        print("Wi-Fi Connection Failed!")
        return False


def generate_boundary():
    return ubinascii.hexlify(bytes([urandom.getrandbits(8) for _ in range(8)])).decode()

def create_wav_from_raw(raw_path, wav_path, sample_rate, bits_per_sample, channels):
    try:
        raw_size = os.stat(raw_path)[6]
        byte_rate = sample_rate * channels * bits_per_sample // 8
        block_align = channels * bits_per_sample // 8
        data_chunk_size = raw_size
        riff_chunk_size = 36 + data_chunk_size

        wav_header = bytearray()
        # "RIFF"
        wav_header.extend(b'RIFF')
        # size
        wav_header.extend(struct.pack('<I', riff_chunk_size))
        # "WAVE"
        wav_header.extend(b'WAVE')
        # "fmt "
        wav_header.extend(b'fmt ')
        # Subchunk1Size (16 for PCM)
        wav_header.extend(struct.pack('<I', 16))
        # AudioFormat (1=PCM)
        wav_header.extend(struct.pack('<H', 1))
        # NumChannels
        wav_header.extend(struct.pack('<H', channels))
        # SampleRate
        wav_header.extend(struct.pack('<I', sample_rate))
        # ByteRate
        wav_header.extend(struct.pack('<I', byte_rate))
        # BlockAlign
        wav_header.extend(struct.pack('<H', block_align))
        # BitsPerSample
        wav_header.extend(struct.pack('<H', bits_per_sample))
        # "data"
        wav_header.extend(b'data')
        # data chunk size
        wav_header.extend(struct.pack('<I', data_chunk_size))

        with open(raw_path, 'rb') as f_in, open(wav_path, 'wb') as f_out:
            f_out.write(wav_header)
            while True:
                chunk = f_in.read(1024)
                if not chunk:
                    break
                f_out.write(chunk)
        print("WAV generated:", wav_path)
    except Exception as e:
        print("ERROR:", e)


def chunk_text(text, text_size=2):
    
    char_width = 6 * text_size 
    screen_width = 310
    max_chars_per_line = screen_width // char_width

    lines = []
    pos = 0
    while pos < len(text):
        line = text[pos:pos + max_chars_per_line]
        lines.append(line)
        pos += max_chars_per_line
    return lines


def display_user_and_ai(user_text, ai_text, text_size=2, user_color=0xFFFF, ai_color=0x07E0, bg_color=0x0000, delay=3):
 
    user_lines = chunk_text(user_text, text_size)

    ai_lines = chunk_text(ai_text, text_size)
    combined_lines = []
    for line in user_lines:
        combined_lines.append((line, user_color))

    combined_lines.append(("", user_color))
    for line in ai_lines:
        combined_lines.append((line, ai_color))

    line_height = text_size * 12
    screen_height = 240
    lines_per_screen = screen_height // line_height
    total_pages = (len(combined_lines) + lines_per_screen - 1) // lines_per_screen

    idx = 0
    for page in range(total_pages):
        M5.Lcd.clear(bg_color)
        y = 10
        start_line = page * lines_per_screen
        end_line = min(start_line + lines_per_screen, len(combined_lines))

        for i in range(start_line, end_line):
            text_line, color = combined_lines[i]
            M5.Lcd.setCursor(10, y)
            M5.Lcd.setTextSize(text_size)
            M5.Lcd.setTextColor(color)
            M5.Lcd.print(text_line)
            y += line_height

      
        time.sleep(delay)

def convert_text_to_unicode(text):

    if any(ord(c) > 127 for c in text):
        return ' '.join(f"U+{ord(c):04X}" for c in text)
    else:
        return text
def chat_with_gpt(text):
    converted_text = convert_text_to_unicode(text)+"If you receive Unicode, please respond to the question in the represented language. You DONT need to analyze other information,you only need to return the answer content.If it’s Chinese, please reply in Traditional Chinese.Your answer:"
    print(f"📨 Sending to GPT-4: {converted_text}")
    

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": converted_text}]
    }
    response = urequests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        gpt_reply = result["choices"][0]["message"]["content"]
        print(f"GPT-4 Reply: {(gpt_reply)}")
        return gpt_reply
    else:
        print(f"GPT-4 Failed: {response.text}")
        return "Error calling GPT-4!"
    
def process_audio(wav_path):
    global processing

    if not connect_wifi():
        processing = False
        return

    try:
        with open(wav_path, "rb") as f:
            audio_data = f.read()

        boundary = generate_boundary()
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="test.wav"\r\n'
            f"Content-Type: audio/wav\r\n\r\n"
        ).encode() + audio_data + (
            f"\r\n--{boundary}\r\n"
            f'Content-Disposition: form-data; name="model"\r\n\r\n'
            f"whisper-1\r\n"
            f"--{boundary}--\r\n"
        ).encode()

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }

        print("Sending request to Whisper API with WAV...")
        response = urequests.post(WHISPER_API_URL, headers=headers, data=body)

        print("API Response Code:", response.status_code)
        print("API Response Text:", response.text)

        if response.status_code == 200:
            result = ujson.loads(response.text)
            user_text = result.get("text", "")
            print(f"Transcribed text: {user_text}")

         
            ai_reply = chat_with_gpt(user_text)

      
            display_user_and_ai(
                user_text,
                ai_reply,
                text_size=2,
                user_color=0xFFFF,   
                ai_color=0x07E0,     
                bg_color=0x0000,     
                delay=3
            )
        else:
            print(f"Whisper API Failed: {response.text}")
            M5.Lcd.clear(0x0000)
            M5.Lcd.setCursor(10, 10)
            M5.Lcd.print("Whisper Failed!")
    except Exception as e:
        print(f"Error: {e}")
        M5.Lcd.clear(0x0000)
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.print("API Error!")


    try:
        os.remove(wav_path)
        print(f"Deleted file: {wav_path}")
    except OSError:
        print(f"Failed to delete {wav_path}")

    processing = False


def start_recording():
    global recording, start_time, processing
    if not recording and not processing:
        print("Recording started...")
        M5.Lcd.clear(0x0000)
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.print("Press and hold the screen -> Recording in progress")

        recorder.record(RAW_FILE_URL, RECORD_DURATION, False)
        recording = True
        start_time = time.time()

def stop_recording():
    global recording, processing
    if recording:
        recorder.stop()
        recording = False
        processing = True
        print(f"Recording saved to {RAW_FILE_PATH}")
        M5.Lcd.clear(0x0000)
        M5.Lcd.setCursor(10, 10)
        M5.Lcd.print("Processing...")

        if "test.raw" in os.listdir("/flash/res/audio"):
            print("Raw PCM file saved.")
           
            create_wav_from_raw(RAW_FILE_PATH, WAV_FILE_PATH, SAMPLE_RATE, BITS_PER_SAMPLE, CHANNELS)
          
            process_audio(WAV_FILE_PATH)

          
            try:
                os.remove(RAW_FILE_PATH)
            except:
                pass
        else:
            print("Error: Raw PCM File not found!")
            processing = False
            M5.Lcd.clear(0x0000)
            M5.Lcd.setCursor(10, 10)
            M5.Lcd.print("File Error!")

def wait_for_touch():
    global recording, processing
    was_touched = False
    while True:
        M5.update()
        touch_count = M5.Touch.getCount()
        if not processing:
            is_touched = (touch_count > 0)
            if is_touched and not was_touched:
                print("Touch DOWN => Start Recording")
                start_recording()
            if not is_touched and was_touched:
                print("Touch UP => Stop Recording")
                stop_recording()
            was_touched = is_touched
        time.sleep(0.1)


if __name__ == "__main__":
    connect_wifi()
    wait_for_touch()