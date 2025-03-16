# Micropython-LLM-Chat-for-M5Stack-CoreS3-ESP32-S3-Box
> **Note:** 2025/3/16 This is the initial version(complete within one day) without full code cleanup. The project will be gradually improved over time.

This project enables real-time audio transcription and conversation with LLMs API like GPT-4 using an M5Stack CoreS3 or ESP32-S3-Box.
## Features
- Voice recording and conversion to text using OpenAI's Whisper API
- Chatting with GPT-4 (or other LLMs)
- Supports English, Japanese, and Chinese
- Wi-Fi connectivity and real-time interaction
- You don’t need to handle any `urequest` issues when sending messages in different languages—OpenAI's API automatically processes multilingual input.
- You are not restricted to OpenAI's API—you can modify the script to use any other LLM provider.

## Requirements
- M5Stack CoreS3 or ESP32-S3-Box
- Micropython firmware (This project is based on M5Stack's component library)
- OpenAI API key
- A network environment with Wi-Fi connectivity

## Setup
1. Flash Micropython to your device.
2. Configure Wi-Fi credentials in the script.
3. Provide an OpenAI API key.
4. Run the script and interact with the AI!

## License
MIT License

---

### **Contribute & Connect**
I’d love to hear your feedback and improvement suggestions! Feel free to connect with me on LinkedIn, and let's explore microcontrollers together as a team. 🚀 
🔗 **LinkedIn:** `kangying0501 [at] linkedin [dot] com`
