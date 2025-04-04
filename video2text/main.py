import yt_dlp
import speech_recognition as sr
from pydub import AudioSegment
import os

# FFmpeg yolunu doğrudan belirtiyoruz
os.environ['PATH'] += os.pathsep + r'C:\ffmpeg-2025-03-31-git-35c091f4b7-full_build\bin'


def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': 'audio',
        'ffmpeg_location': r'C:\ffmpeg-2025-03-31-git-35c091f4b7-full_build\bin\ffmpeg.exe'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return 'audio.wav'
    except Exception as e:
        print(f"İndirme hatası: {e}")
        return None


def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    text = ""

    try:
        audio = AudioSegment.from_wav(audio_file)
        chunk_length = 30 * 1000  # 30 seconds

        # Add progress bar here
        from tqdm import tqdm
        for i in tqdm(range(0, len(audio), chunk_length), desc="Transcribing", unit="chunk"):
            chunk = audio[i:i + chunk_length]
            chunk_name = f"temp_chunk_{i}.wav"
            chunk.export(chunk_name, format="wav")

            with sr.AudioFile(chunk_name) as source:
                audio_data = recognizer.record(source)
                try:
                    text += recognizer.recognize_google(audio_data, language='tr-TR') + " "
                except sr.UnknownValueError:
                    print(f"\nChunk {i//chunk_length} could not be understood")  # \n for new line
                except sr.RequestError as e:
                    print(f"\nAPI error: {e}")

            os.remove(chunk_name)

    except Exception as e:
        print(f"\nProcessing error: {e}")

    return text

def save_to_text(content, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Kayıt hatası: {e}")
        return False


def main():
    video_url = 'https://www.youtube.com/watch?v=TkbY-OXKO-Q&t=330s'

    print("Ses indiriliyor...")
    audio_file = download_audio(video_url)
    if not audio_file:
        return

    print("Metne çevriliyor...")
    transcript = transcribe_audio(audio_file)

    if transcript:
        print("Dosyaya yazılıyor...")
        if save_to_text(transcript, 'transkript.txt'):
            print("Başarıyla tamamlandı!")
        else:
            print("Dosya yazma hatası")
    else:
        print("Metin çıkarılamadı")

    if os.path.exists(audio_file):
        os.remove(audio_file)


if __name__ == "__main__":
    main()
