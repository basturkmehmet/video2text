import yt_dlp
import speech_recognition as sr
from pydub import AudioSegment
import os

# Explicitly set FFmpeg path in system environment variables
os.environ['PATH'] += os.pathsep + r'C:\ffmpeg-2025-03-31-git-35c091f4b7-full_build\bin'


def download_audio(url):
    """Download audio from YouTube video and save as WAV file"""
    ydl_opts = {
        'format': 'bestaudio/best',  # Select best quality audio stream
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',  # Use WAV format for better compatibility
            'preferredquality': '192',  # Audio quality setting
        }],
        'outtmpl': 'audio',  # Output template filename
        'ffmpeg_location': r'C:\ffmpeg-2025-03-31-git-35c091f4b7-full_build\bin\ffmpeg.exe'  # FFmpeg binary path
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return 'audio.wav'  # Return the generated filename
    except Exception as e:
        print(f"Download error: {e}")
        return None


def transcribe_audio(audio_file):
    """Convert audio file to text using speech recognition"""
    recognizer = sr.Recognizer()
    text = ""

    try:
        audio = AudioSegment.from_wav(audio_file)
        chunk_length = 30 * 1000  # Process in 30 second chunks

        # Add progress bar for transcription process
        from tqdm import tqdm
        for i in tqdm(range(0, len(audio), chunk_length), 
                     desc="Transcribing", 
                     unit="chunk"):
            chunk = audio[i:i + chunk_length]
            chunk_name = f"temp_chunk_{i}.wav"
            chunk.export(chunk_name, format="wav")

            with sr.AudioFile(chunk_name) as source:
                audio_data = recognizer.record(source)
                try:
                    # Recognize Turkish speech using Google API
                    text += recognizer.recognize_google(audio_data, language='tr-TR') + " "
                except sr.UnknownValueError:
                    print(f"\nChunk {i//chunk_length} could not be understood")
                except sr.RequestError as e:
                    print(f"\nAPI error: {e}")

            os.remove(chunk_name)  # Clean up temporary chunk file

    except Exception as e:
        print(f"\nProcessing error: {e}")

    return text


def save_to_text(content, filename):
    """Save transcribed text to file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"File save error: {e}")
        return False


def main():
    """Main execution flow"""
    video_url = 'https://www.youtube.com/watch?v=TkbY-OXKO-Q&t=330s'

    print("Downloading audio...")
    audio_file = download_audio(video_url)
    if not audio_file:
        return

    print("Transcribing audio to text...")
    transcript = transcribe_audio(audio_file)

    if transcript:
        print("Saving to text file...")
        if save_to_text(transcript, 'transcript.txt'):
            print("Successfully completed!")
        else:
            print("Error saving file")
    else:
        print("Failed to extract text")

    # Clean up audio file
    if os.path.exists(audio_file):
        os.remove(audio_file)


if __name__ == "__main__":
    main()
