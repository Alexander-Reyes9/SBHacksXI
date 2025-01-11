import pydub as pd
import librosa as lb
import numpy as np
import soundfile as sf

# Load the first and second songs
song1 = pd.AudioSegment.from_mp3("music.mp3")
song2 = pd.AudioSegment.from_mp3("music3.mp3")

# Skip the first 10 seconds and last 10 seconds for analysis
song1_trimmed = song1[10000:-10000]
song2_trimmed = song2[10000:-10000]

# Convert AudioSegment to numpy array
y1 = np.array(song1_trimmed.get_array_of_samples())
y2 = np.array(song2_trimmed.get_array_of_samples())

# Handle stereo audio (if present) by selecting the first channel
def handle_stereo(audio_array, channels):
    return audio_array[::channels] if channels > 1 else audio_array

# Get the number of channels for each song
y1 = handle_stereo(y1, song1.channels)
y2 = handle_stereo(y2, song2.channels)

# Resample to 22050 Hz for librosa processing
# Fix: Updated resample function calls with correct parameter names
y1 = lb.resample(y=y1.astype(np.float32), orig_sr=song1.frame_rate, target_sr=22050)
y2 = lb.resample(y=y2.astype(np.float32), orig_sr=song2.frame_rate, target_sr=22050)

# Beat tracking
tempo1, beats1 = lb.beat.beat_track(y=y1, sr=22050)
tempo2, beats2 = lb.beat.beat_track(y=y2, sr=22050)

# Find the beat times
beat_times1 = lb.frames_to_time(beats1, sr=22050)
beat_times2 = lb.frames_to_time(beats2, sr=22050)

# Find the transition point (most similar beats, excluding the first and last 10 seconds)
min_diff = float('inf')
transition_point1 = None
transition_point2 = None

for bt1 in beat_times1:
    if bt1 < 10 or bt1 > (len(y1) / 22050) - 10:
        continue  # Skip beats within the first and last 10 seconds

    for bt2 in beat_times2:
        if bt2 < 10 or bt2 > (len(y2) / 22050) - 10:
            continue  # Skip beats within the first and last 10 seconds

        diff = abs(bt1 - bt2)
        if diff < min_diff:
            min_diff = diff
            transition_point1 = bt1
            transition_point2 = bt2

# Calculate the number of samples for transition points
transition_samples1 = int(transition_point1 * 22050)
transition_samples2 = int(transition_point2 * 22050)

# Create the transition by merging segments
transition = np.concatenate((y1[:transition_samples1], y2[transition_samples2:]))

# Normalize the audio to prevent clipping
transition = transition / np.max(np.abs(transition))

# Convert back to AudioSegment
transition_segment = pd.AudioSegment(
    (transition * 32767).astype(np.int16).tobytes(), 
    frame_rate=22050, 
    sample_width=2,  # 16-bit audio
    channels=1
)

# Export the result
transition_segment.export("transition_output.mp3", format="mp3")

print("Transition created and saved as transition_output.mp3")