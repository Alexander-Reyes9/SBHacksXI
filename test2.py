import pydub as pd
import librosa as lb
import numpy as np
from scipy.signal import fftconvolve
import soundfile as sf

def create_reverb_tail(audio, sr=22050, room_size=0.8, damping=0.4, decay=3.0):
    """
    Create a more pronounced reverb tail for smooth transition
    """
    # Create decay envelope with longer decay
    tail_length = int(decay * sr)
    decay_envelope = np.exp(-np.linspace(0, decay, tail_length) / (room_size * 1.5))  # Slower decay
    
    # Create room impulse response with less damping for more echo
    impulse = np.random.randn(tail_length) * decay_envelope
    impulse = impulse * (1 - damping * np.linspace(0, 1, tail_length))
    
    # Normalize impulse response with stronger presence
    impulse = impulse / np.sum(np.abs(impulse)) * 1.2  # Increased reverb intensity
    
    # Apply convolution for reverb
    reverb_tail = fftconvolve(audio, impulse)[:len(audio) + tail_length]
    
    # Normalize reverb tail while keeping it more prominent
    input_rms = np.sqrt(np.mean(audio**2))
    reverb_rms = np.sqrt(np.mean(reverb_tail**2))
    if reverb_rms > 0:
        reverb_tail = reverb_tail * (input_rms / reverb_rms) * 1.1  # Increased reverb volume
    
    return reverb_tail

try:
    # Load the first and second songs
    print("Loading songs...")
    song1 = pd.AudioSegment.from_mp3("lana.mp3")
    song2 = pd.AudioSegment.from_mp3("bunny.mp3")

    # Define transition length (in milliseconds)
    transition_length = 5000  # 5 seconds (longer transition for more echo)

    # Convert AudioSegment to numpy array
    y1 = np.array(song1.get_array_of_samples())
    y2 = np.array(song2.get_array_of_samples())

    # Handle stereo audio (if present) by selecting the first channel
    def handle_stereo(audio_array, channels):
        return audio_array[::channels] if channels > 1 else audio_array

    # Get the number of channels for each song
    y1 = handle_stereo(y1, song1.channels)
    y2 = handle_stereo(y2, song2.channels)

    # Normalize input audio
    y1 = y1.astype(np.float32) / np.max(np.abs(y1))
    y2 = y2.astype(np.float32) / np.max(np.abs(y2))

    # Match volumes using RMS
    rms1 = np.sqrt(np.mean(y1**2))
    rms2 = np.sqrt(np.mean(y2**2))
    y2 = y2 * (rms1 / rms2)

    # Resample to 22050 Hz for processing
    y1 = lb.resample(y=y1, orig_sr=song1.frame_rate, target_sr=22050)
    y2 = lb.resample(y=y2, orig_sr=song2.frame_rate, target_sr=22050)

    # Calculate transition points (75% through first song)
    transition_point = int(len(y1) * 0.75)
    transition_samples = int((transition_length / 1000) * 22050)

    # Create reverb tail for the end of first song
    reverb_segment = y1[transition_point-transition_samples:transition_point]
    reverb_tail = create_reverb_tail(
        reverb_segment, 
        sr=22050,
        room_size=0.8,    # Larger room size for more echo
        damping=0.4,      # Less damping for longer echoes
        decay=3.0         # Longer decay time
    )

    # Create smooth crossfade curves (adjusted for more echo overlap)
    fade_out = np.linspace(1, 0, len(reverb_tail))**1.5  # Less aggressive fade out
    fade_in = np.linspace(0, 1, len(reverb_tail))**1.5   # Less aggressive fade in

    # Create output array
    output_length = transition_point + len(reverb_tail) + (len(y2) - transition_samples)
    transition = np.zeros(output_length)

    # Add first song up to transition point
    transition[:transition_point] = y1[:transition_point]

    # Add reverb tail with fade out (increased reverb mix)
    reverb_start = transition_point - transition_samples
    reverb_end = reverb_start + len(reverb_tail)
    transition[reverb_start:reverb_end] = \
        transition[reverb_start:reverb_end] * fade_out + reverb_tail * fade_out * 0.85  # Increased reverb mix

    # Add second song with fade in
    second_song_start = transition_point
    fade_in_samples = min(len(fade_in), len(y2))
    
    # Ensure the arrays match in size for the fade-in portion
    fade_in = fade_in[:fade_in_samples]
    second_song_fade = y2[:fade_in_samples]
    
    # Add second song with balanced presence
    transition[second_song_start:second_song_start + fade_in_samples] += second_song_fade * fade_in * 0.95
    
    # Add the rest of the second song
    remaining_samples = len(transition) - (second_song_start + fade_in_samples)
    if remaining_samples > 0:
        samples_to_add = min(remaining_samples, len(y2[fade_in_samples:]))
        transition[second_song_start + fade_in_samples:second_song_start + fade_in_samples + samples_to_add] += \
            y2[fade_in_samples:fade_in_samples + samples_to_add]

    # Final volume normalization while preserving dynamics
    max_amplitude = np.max(np.abs(transition))
    if max_amplitude > 0:
        transition = transition * (0.95 / max_amplitude)

    # Convert back to AudioSegment
    transition_segment = pd.AudioSegment(
        (transition * 32767).astype(np.int16).tobytes(), 
        frame_rate=22050, 
        sample_width=2,
        channels=1
    )

    # Export the result
    transition_segment.export("reverb_transition.mp3", format="mp3")
    print("Transition with enhanced reverb tail created and saved as reverb_transition.mp3")

except Exception as e:
    print(f"An error occurred: {str(e)}")