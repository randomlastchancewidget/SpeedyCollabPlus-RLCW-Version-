import os
import re
from moviepy import (VideoFileClip, AudioFileClip,
                     CompositeVideoClip, concatenate_videoclips)
from moviepy.video.fx import *
from moviepy.video.VideoClip import TextClip
from pydub import AudioSegment

import librosa
import soundfile as sf
import tempfile

def clean_temp_folder(path, pattern=None):
    if not os.path.exists(path):
        print(f"Path {path} does not exist.")
        return

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            if pattern is None or re.match(pattern, filename):
                os.remove(file_path)
                print(f"Deleted: {file_path}")

def put_text_on_video(video_clip, text_to_write, font_size, color, font, position):
    """Overlay text on a video clip with centered alignment and an outline."""
    # Create the main text clip
    text_clip = TextClip(
        text=text_to_write,
        font_size=font_size,
        color=color,
        text_align="center",
        font=font
    ).with_duration(video_clip.duration)

    # Create an outline for the text by duplicating it with a thicker stroke
    outline_clip = TextClip(
        text=text_to_write,
        font_size=font_size,
        color="black",
        text_align="center",  # Outline color
        font=font,
        stroke_color="black",  # Stroke color
        stroke_width=3  # Thickness of the outline
    ).with_duration(video_clip.duration)

    # Position both the text and outline in the center
    outline_clip = outline_clip.with_position(position)
    text_clip = text_clip.with_position(position)

    # Combine the outline and text on top of the video
    return CompositeVideoClip([video_clip, outline_clip, text_clip])

def speed_up_video_with_pitch(input_clip, speed_amount=2):

    semitones= -12
  
    clip = input_clip

    new_clip = MultiplySpeed(factor=speed_amount).apply(clip)

    # Step 1: Extract audio to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        audio_path = temp_audio.name
        new_clip.audio.write_audiofile(audio_path, codec='pcm_s16le')  # uncompressed WAV

    # Step 2: Load with librosa
    y, sr = librosa.load(audio_path, sr=None)

    # Step 3: Pitch shift
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitones)
    y_shifted = librosa.util.normalize(y_shifted)

    # Step 4: Write to new temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_shifted:
        shifted_path = temp_shifted.name
        sf.write(shifted_path, y_shifted, sr)

    # Step 5: Load shifted audio into moviepy
    new_audio = AudioFileClip(shifted_path)

    # Step 6: Replace audio and write final video
    new_clip.audio = new_audio
    # final.write_videofile(output_file, audio_codec='aac')

    final_video = CompositeVideoClip([new_clip])

    return final_video

def double_and_concat(input_clip, output_file):

    sped_up_clip = speed_up_video_with_pitch(input_clip, speed_amount=2)

    # Here is where we apply effects

    #inverted = InvertColors().apply(sped_up_clip)


    #quad_clip = clips_array([[sped_up_clip, sped_up_clip],
    #                        [sped_up_clip, sped_up_clip]])

    new_clip = concatenate_videoclips([sped_up_clip,
                                       sped_up_clip])

    print("Clip is doubled and concat, now write to: ", output_file)

    new_clip.write_videofile(output_file, audio_codec='aac')

    new_clip.close()
    sped_up_clip.close()

    return output_file


def adjust_audio_pitch(audio_file_path, output_path, semitones):
    # Load with librosa
    y, sr = librosa.load(audio_file_path, sr=None)

    # Shift pitch while preserving tempo
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitones)

    # Save to temp wav file
    sf.write("temp_shifted.wav", y_shifted, sr)

    # Optionally load into pydub again
    shifted = AudioSegment.from_wav("temp_shifted.wav")
    shifted.export(output_path, format="mp3")  # or 'wav', 'flac', etc.
    return output_path
