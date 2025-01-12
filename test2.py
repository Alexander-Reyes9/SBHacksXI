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
    decay_envelope = np.exp(-np.linspace(0, decay, tail_length) / (room_size * 1.5))
    
    # Create room impulse response with less damping for more echo
    impulse = np.random.randn(tail_length) * decay_envelope
    impulse = impulse * (1 - damping * np.linspace(0, 1, tail_length))
    
    # Normalize impulse response with stronger presence
    impulse = impulse / np.sum(np.abs(impulse)) * 1.2
    
    # Apply convolution for reverb
    reverb_tail = fftconvolve(audio, impulse)[:len(audio) + tail_length]
    
    # Normalize reverb tail while keeping it more prominent
    input_rms = np.sqrt(np.mean(audio**2))
    reverb_rms = np.sqrt(np.mean(reverb_tail**2))
    if reverb_rms > 0:
        reverb_tail = reverb_tail * (input_rms / reverb_rms) * 1.1
    
    return reverb_tail

try:
    # Load the first and second songs
    print("Loading songs...")
    song1 = pd.AudioSegment.from_mp3("lana.mp3")
    song2 = pd.AudioSegment.from_mp3("bunny.mp3")

    # Define transition length (in milliseconds)
    transition_length = 5000  # 5 seconds

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
        room_size=0.8,
        damping=0.4,
        decay=3.0
    )

    # Calculate the overlap window
    overlap_start = transition_point - transition_samples
    overlap_length = len(reverb_tail)

    # Create overlapping fade curves
    fade_out = np.linspace(1, 0, overlap_length)**1.5
    fade_in = np.linspace(0, 1, overlap_length)**1.5

    # Create output array
    output_length = transition_point + len(reverb_tail)
    transition = np.zeros(output_length)

    # Add first song up to the end
    transition[:transition_point] = y1[:transition_point]

    # Add reverb tail with fade out
    reverb_start = overlap_start
    reverb_end = reverb_start + overlap_length
    transition[reverb_start:reverb_end] = \
        transition[reverb_start:reverb_end] * fade_out + reverb_tail * fade_out * 0.85

    # Add second song with fade in starting at the same point
    second_song_fade = y2[:overlap_length]
    transition[reverb_start:reverb_end] += second_song_fade * fade_in * 0.95

    # Add the rest of the second song
    remaining_start = reverb_end
    remaining_samples = len(y2[overlap_length:])
    if remaining_samples > 0:
        remaining_end = remaining_start + remaining_samples
        if remaining_end > len(transition):
            remaining_end = len(transition)
        transition[remaining_start:remaining_end] += y2[overlap_length:overlap_length + (remaining_end - remaining_start)]

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
    print("Transition with overlapping fades created and saved as reverb_transition.mp3")

except Exception as e:
    print(f"An error occurred: {str(e)}")


def create_scratch_transition(x_1, x_2, x_disc, fs, transition_point_ratio=0.75):
    """
    Create a transition using disc scratch sound between two songs
    
    Parameters:
    -----------
    x_1 : np.ndarray
        First audio signal
    x_2 : np.ndarray
        Second audio signal
    x_disc : np.ndarray
        Disc scratch sound effect
    fs : int
        Sampling rate
    transition_point_ratio : float
        Position in first song where transition occurs (0-1)
    """
    try:
        # Ensure mono audio
        if x_1.ndim > 1:
            x_1 = np.mean(x_1, axis=1)
        if x_2.ndim > 1:
            x_2 = np.mean(x_2, axis=1)
        if x_disc.ndim > 1:
            x_disc = np.mean(x_disc, axis=1)

        # Normalize audio
        x_1 = x_1 / np.max(np.abs(x_1))
        x_2 = x_2 / np.max(np.abs(x_2))
        x_disc = x_disc / np.max(np.abs(x_disc))

        # Calculate transition point
        transition_point = int(len(x_1) * transition_point_ratio)
        
        # Create short fade out for first song (100ms)
        fade_samples = int(0.1 * fs)
        fade_out = np.linspace(1, 0, fade_samples)
        x_1[transition_point-fade_samples:transition_point] *= fade_out

        # Calculate total length
        disc_duration = len(x_disc)
        total_length = transition_point + disc_duration + len(x_2)
        
        # Create output array
        output = np.zeros(total_length)
        
        # Add first song up to transition
        output[:transition_point] = x_1[:transition_point]
        
        # Add disc scratch
        output[transition_point:transition_point+disc_duration] = x_disc
        
        # Create short fade in for second song (100ms)
        fade_in = np.linspace(0, 1, fade_samples)
        x_2_start = transition_point + disc_duration
        
        # Add second song after disc scratch
        if fade_samples < len(x_2):
            x_2[:fade_samples] *= fade_in
            output[x_2_start:x_2_start+len(x_2)] = x_2

        # Normalize final output
        output = output / np.max(np.abs(output))
        
        return output

    except Exception as e:
        print(f"Error in create_scratch_transition: {str(e)}")
        return None

def scratch_transition_main():
    try:
        # Load audio files
        print("Loading audio files...")
        x_1, fs = lb.load("bunny.mp3", sr=None)
        x_2, fs = lb.load("music.mp3", sr=None)
        x_disc, fs = lb.load("disc.mp3", sr=None)
        x_disc = x_disc[:int(fs * 3)]  # Limit disc scratch to 100ms

        print("Creating scratch transition...")
        # Create transition
        full_audio = create_scratch_transition(x_1, x_2, x_disc, fs)

        if full_audio is not None:
            print("Saving output file...")
            # Save the result
            sf.write("scratch_transition.mp3", full_audio, fs)
            print("Done! Output saved as 'scratch_transition.wav'")
        else:
            print("Failed to create transition")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

scratch_transition_main()
def create_scratch_crossfade(x_1, x_2, x_disc, fs, transition_point_ratio=0.75, overlap_duration=1.0):
    """
    Create a crossfade transition with overlapping songs and disc scratch effect
    """
    try:
        # Ensure mono audio
        if x_1.ndim > 1:
            x_1 = np.mean(x_1, axis=1)
        if x_2.ndim > 1:
            x_2 = np.mean(x_2, axis=1)
        if x_disc.ndim > 1:
            x_disc = np.mean(x_disc, axis=1)

        # Normalize audio
        x_1 = x_1 / np.max(np.abs(x_1))
        x_2 = x_2 / np.max(np.abs(x_2))
        x_disc = x_disc / np.max(np.abs(x_disc)) * 0.8

        # Calculate transition points
        transition_point = int(len(x_1) * transition_point_ratio)
        overlap_samples = int(overlap_duration * fs)
        
        # Create crossfade envelopes
        fade_out = np.linspace(1, 0, overlap_samples)**1.5
        fade_in = np.linspace(0, 1, overlap_samples)**1.5

        # Calculate disc timing
        disc_start = transition_point + int(overlap_samples * 0.3)
        disc_duration = len(x_disc)
        
        # Calculate total length needed
        total_length = max(transition_point + overlap_samples, disc_start + disc_duration)
        
        # Create output array
        output = np.zeros(total_length)
        
        # Add first song up to transition point
        output[:transition_point] = x_1[:transition_point]
        
        # Handle the crossfade region
        crossfade_end = min(transition_point + overlap_samples, len(x_1))
        actual_overlap = crossfade_end - transition_point
        
        # Adjust fade curves to match actual overlap length
        fade_out = fade_out[:actual_overlap]
        fade_in = fade_in[:actual_overlap]
        
        # Apply crossfade
        output[transition_point:crossfade_end] = \
            x_1[transition_point:crossfade_end] * fade_out
        
        # Add second song with fade in
        if len(x_2) >= actual_overlap:
            output[transition_point:crossfade_end] += \
                x_2[:actual_overlap] * fade_in
            
            # Add remainder of second song
            remaining_start = crossfade_end
            remaining_length = len(output) - remaining_start
            if remaining_length > 0:
                samples_to_add = min(remaining_length, len(x_2) - actual_overlap)
                output[remaining_start:remaining_start + samples_to_add] += \
                    x_2[actual_overlap:actual_overlap + samples_to_add]
        
        # Add disc scratch during crossfade
        if disc_duration > 0:
            # Create disc fade envelope
            disc_fade_in_samples = int(disc_duration * 0.1)
            disc_fade_out_samples = int(disc_duration * 0.1)
            disc_sustain_samples = disc_duration - disc_fade_in_samples - disc_fade_out_samples
            
            disc_envelope = np.concatenate([
                np.linspace(0, 1, disc_fade_in_samples),
                np.ones(max(0, disc_sustain_samples)),
                np.linspace(1, 0, disc_fade_out_samples)
            ])
            
            # Ensure disc envelope matches disc length
            disc_envelope = disc_envelope[:disc_duration]
            
            # Add disc with envelope
            disc_end = min(disc_start + disc_duration, len(output))
            actual_disc_samples = disc_end - disc_start
            output[disc_start:disc_end] += x_disc[:actual_disc_samples] * disc_envelope[:actual_disc_samples]

        # Normalize final output
        output = output / np.max(np.abs(output)) * 0.95
        
        return output

    except Exception as e:
        print(f"Error in create_scratch_crossfade: {str(e)}")
        return None

def scratch_crossfade_main():
    try:
        # Load audio files
        print("Loading audio files...")
        x_1, fs = lb.load("bunny.mp3", sr=None)
        x_2, fs = lb.load("music.mp3", sr=None)
        x_disc, fs = lb.load("disc.mp3", sr=None)

        print("Creating scratch crossfade transition...")
        # Create transition with 1.5 second overlap
        full_audio = create_scratch_crossfade(x_1, x_2, x_disc, fs, 
                                            transition_point_ratio=0.75,
                                            overlap_duration=1.5)

        if full_audio is not None:
            print("Saving output file...")
            sf.write("scratch_crossfade.mp3", full_audio, fs)
            print("Done! Output saved as 'scratch_crossfade.mp3'")
        else:
            print("Failed to create transition")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run the transition
scratch_crossfade_main()