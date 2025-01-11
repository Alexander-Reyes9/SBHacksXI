import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt

def warp_audio_with_dtw(x, wp, fs, hop_length=512):
    """
    Warp the audio signal based on the DTW path.
    
    Parameters:
    -----------
    x : np.ndarray
        Audio signal to be warped
    wp : np.ndarray
        Warping path
    fs : int
        Sampling rate
    hop_length : int, optional
        Hop length used for feature extraction
    
    Returns:
    --------
    np.ndarray
        Warped audio signal
    """
    # Map frame indices to time
    time_warped = librosa.frames_to_samples(wp[:, 1], hop_length=hop_length) / fs
    audio_time = np.arange(len(x)) / fs

    # Interpolate audio signal to align with the warped timeline
    warped_audio = np.interp(audio_time, time_warped, x)
    return warped_audio

def create_full_transition(x_1, x_2, wp_s, fs, crossfade_duration=1.0):
    """
    Create a full audio file containing the entire first track that transitions into the second track.
    
    Parameters:
    -----------
    x_1 : np.ndarray
        First audio signal (played in full)
    x_2 : np.ndarray
        Second audio signal (transitioned into)
    wp_s : np.ndarray
        Warping path in seconds
    fs : int
        Sampling rate
    crossfade_duration : float, optional
        Duration of the crossfade between tracks in seconds
    
    Returns:
    --------
    np.ndarray
        The complete audio signal with transition
    """
    # Convert crossfade duration to samples
    crossfade_samples = int(crossfade_duration * fs)
    
    # Calculate lengths
    transition_start = len(x_1) - crossfade_samples
    if transition_start < 0:
        raise ValueError("First audio signal is too short for the specified crossfade duration.")
    
    total_length = len(x_1) + len(x_2) - crossfade_samples
    
    # Create output array
    output = np.zeros(total_length)
    
    # Copy the first signal
    output[:len(x_1)] = x_1
    
    # Create crossfade weights
    fade_out = np.linspace(1, 0, crossfade_samples)
    fade_in = np.linspace(0, 1, crossfade_samples)
    
    # Apply crossfade
    output[transition_start:transition_start + crossfade_samples] = (
        x_1[transition_start:transition_start + crossfade_samples] * fade_out +
        x_2[:crossfade_samples] * fade_in
    )
    
    # Add the rest of x_2
    output[transition_start + crossfade_samples:] = x_2[crossfade_samples:]
    
    return output

def main():
    try:
        # Load audio files
        print("Loading audio files...")
        x_1, fs = librosa.load('bunny.mp3', sr=None, duration=200)
        x_2, fs = librosa.load('music.mp3', sr=None, duration=200)

        print("Calculating chroma features...")
        # Calculate chroma features
        hop_length = 1024
        x_1_chroma = librosa.feature.chroma_cqt(y=x_1, sr=fs, hop_length=hop_length)
        x_2_chroma = librosa.feature.chroma_cqt(y=x_2, sr=fs, hop_length=hop_length)

        print("Computing DTW...")
        # Compute DTW
        D, wp = librosa.sequence.dtw(X=x_1_chroma, Y=x_2_chroma, metric='cosine')

        print("Warping second audio signal...")
        # Warp the second audio signal
        x2_warped = warp_audio_with_dtw(x_2, wp, fs, hop_length=hop_length)

        print("Creating transition...")
        # Create full audio with transition
        full_audio = create_full_transition(x_1, x2_warped, wp, fs, crossfade_duration=2.0)

        print("Saving output file...")
        # Save the result
        sf.write('full_transition.wav', full_audio, fs)
        print("Done! Output saved as 'full_transition.wav'")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
