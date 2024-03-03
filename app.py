import telebot
from gtts import gTTS
from pydub import AudioSegment
from zello_thin import main as start_zello
import json

with open("config.json") as f:
    config = json.load(f)

# Initialize the Telegram Bot with your bot's token
bot = telebot.TeleBot((config.get("telegram")).get("token"))


        
# Dictionary mapping message thread IDs to forum names
forums = {
    22: "Poliisi",
    2: "Turvallisuuspoikkeamat",
    6: "De-eskalointi",
    1: "Roudaus",
    8: "Ensiapu",
    10: "Outreach",
    46: "Hyvinvointi",
    49: "Tiedotteet"
}

# Function to generate TTS audio in Opus format
def generate_tts_opus(text, output_filename="output.opus"):
    tts = gTTS(text=text, lang='fi')
    tts.save("temp.mp3")  # Save as temporary MP3 file
    audio = AudioSegment.from_mp3("temp.mp3")
    audio.export(output_filename, format="opus")  # Export as Opus format

# Function to build notification message based on forum/channel
def build_notification(message) -> str:
    channel_name = forums.get(message.message_thread_id)
    sender_name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
    
    if channel_name == "Poliisi":
        notification = f"Tiedoksi kaikille tukiroolilaisille! Poliisi on antanut ohjeistuksen: {message.text}."
    elif channel_name == "Turvallisuuspoikkeamat":
        notification = f"HUOMIO KAIKKI TUKIROOLIT! VAARATIEDOTE: {message.text}. TOISTAN. Vaaratiedote: {message.text}. Kaikki tukiroolit valmiuteen."
    elif channel_name == "Tiedotteet":
        notification = f"Tiedote: {message.text}"
    elif channel_name == "De-eskalointi":
        notification = f"Huomio de-eskaloijat: {sender_name} kaipaa de-eskaloijaa sijainnissa {message.text}."
    elif channel_name in ["Roudaus", "Ensiapu", "Outreach", "Hyvinvointi"]:
        notification = f"Tiedoksi kaikille tukiroolilaisille! Uusi ilmoitus kanavalla {channel_name}: {message.text}."
    else:
        notification = f"{sender_name} sanoo {message.text}"
    
    return notification

# Handler function for messages received in the specific Telegram channel
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(message.message_thread_id)
    text = build_notification(message)
    if message.from_user.username == "versovuo":
        bot.delete_message(message.chat.id, message.id)
    generate_tts_opus(text)
    start_zello(config.get("zello"))

# Start the bot
bot.polling()
