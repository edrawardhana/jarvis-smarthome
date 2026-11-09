import sys
import time
import re
import urllib.parse
import urllib.request
import webbrowser
import pyttsx3
import speech_recognition as sr
from gnews import GNews

# Force UTF-8 encoding untuk terminal Windows
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

# 1. Inisialisasi Text-to-Speech Engine
try:
    engine = pyttsx3.init("sapi5")
except Exception:
    engine = pyttsx3.init()

engine.setProperty("rate", 160)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")
for voice in voices:
    if "zira" in voice.name.lower() or "david" in voice.name.lower():
        engine.setProperty("voice", voice.id)
        break

# Inisialisasi GNews untuk topik Teknologi dan Sains
google_news = GNews(language="en", country="US", max_results=5)


def speak(text):
    """Membacakan teks dan memastikan audio selesai sebelum lanjut."""
    print(f"🤖 Jarvis: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
        time.sleep(0.5)
    except Exception as e:
        print(f"[Audio Error]: {e}")


def play_on_youtube(query):
    """Mencari URL YouTube secara manual dan langsung membukanya di browser."""
    try:
        search_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={search_query}"
        
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        html = urllib.request.urlopen(req).read().decode("utf-8")
        
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        if video_ids:
            target_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            print(f"🔗 Opening YouTube: {target_url}")
            webbrowser.open(target_url)
        else:
            webbrowser.open(url)
    except Exception as e:
        print(f"[YouTube Error]: {e}")
        webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}")


def listen_command():
    """Mendengarkan input dari mikrofon."""
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("\n🎤 Jarvis is listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.6)
        recognizer.pause_threshold = 0.8

        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
            print("⏳ Processing voice...")
            command = recognizer.recognize_google(audio, language="en-US")
            print(f"🗣️ You: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            speak("Network error. Please check your connection.")
            return ""


def get_latest_tech_news():
    """Mengambil 3 berita teknologi/AI/sains dan menawarkan untuk membuka artikelnya."""
    speak("Fetching the latest technology, AI, and science news for you, Sir.")
    try:
        # Mencari berita spesifik kategori Technology, AI, Science, Education
        query = "artificial intelligence technology science education"
        news_list = google_news.get_news(query)

        if not news_list:
            speak("Sorry, I couldn't fetch the news right now.")
            return

        # Ambil 3 berita teratas
        top_news = news_list[:3]

        speak("Here are the top 3 tech and science headlines:")
        for i, item in enumerate(top_news, 1):
            title = item.get("title", "").split(" - ")[0]
            speak(f"Option {i}: {title}.")

        # Tanyakan ke user berita mana yang ingin dibuka
        speak("Which headline would you like me to open for you, Sir? Say option 1, 2, or 3.")

        # Mendengarkan jawaban pilihan user
        choice_command = listen_command()

        selected_index = None
        if "1" in choice_command or "one" in choice_command or "first" in choice_command:
            selected_index = 0
        elif "2" in choice_command or "two" in choice_command or "second" in choice_command:
            selected_index = 1
        elif "3" in choice_command or "three" in choice_command or "third" in choice_command:
            selected_index = 2

        if selected_index is not None and selected_index < len(top_news):
            target_article = top_news[selected_index]
            article_url = target_article.get("url", "")
            article_title = target_article.get("title", "").split(" - ")[0]

            speak(f"Opening option {selected_index + 1} in your browser: {article_title}")
            print(f"🔗 Opening Article: {article_url}")
            webbrowser.open(article_url)
            time.sleep(4)
        else:
            speak("I didn't catch a valid option number. Returning to main system.")

    except Exception as e:
        print(f"[News Error]: {e}")
        speak("There was an issue fetching the tech news.")


def run_jarvis():
    speak("Welcome home! Jarvis system is online and ready.")

    WAKE_WORDS = ["jarvis", "jefferson", "travis", "service", "harvest"]

    while True:
        command = listen_command()

        if not command:
            continue

        has_wake_word = any(word in command for word in WAKE_WORDS)
        is_shutdown_command = any(
            phrase in command
            for phrase in [
                "turn off",
                "stop",
                "exit",
                "matikan",
                "good night",
                "goodnight",
                "please turn off",
            ]
        )

        is_play_command = any(k in command for k in ["play", "song", "music", "youtube"])
        is_news_command = any(k in command for k in ["news", "headline", "update", "berita", "tech", "technology", "ai", "science"])

        if has_wake_word or is_shutdown_command or is_play_command or is_news_command:
            clean_cmd = command
            for word in WAKE_WORDS:
                clean_cmd = clean_cmd.replace(word, "")
            clean_cmd = clean_cmd.strip()

            # 1. PERINTAH SHUTDOWN
            if is_shutdown_command:
                farewell_text = (
                    "Have a good rest, Sir! Please take care of your health. "
                    "I hope all your plans and tasks go smoothly tomorrow. Amen! "
                    "Shutting down system now."
                )
                speak(farewell_text)
                engine.stop()
                time.sleep(1)
                sys.exit()

            # 2. PERINTAH BERITA TEKNOLOGI & SAINS
            elif is_news_command:
                get_latest_tech_news()

            # 3. PERINTAH PUTAR LAGU YOUTUBE
            elif is_play_command:
                song_name = (
                    clean_cmd.replace("play", "")
                    .replace("song", "")
                    .replace("music", "")
                    .replace("putar", "")
                    .replace("search", "")
                    .replace("on youtube", "")
                    .replace("youtube", "")
                    .replace("please", "")
                    .strip()
                )

                if song_name:
                    speak(f"Playing {song_name} on YouTube")
                    play_on_youtube(song_name)
                    print("🌐 Browser launched. Pausing listening for 6 seconds...")
                    time.sleep(6)
                else:
                    speak("What song would you like to play, Sir?")

            else:
                speak("Command not recognized, Sir.")


if __name__ == "__main__":
    run_jarvis()