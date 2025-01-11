import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt


def align_audio_with_dtw(x, wp, fs, hop_length=512):
    """
    Align an audio signal using a DTW warping path.

    Parameters:
    -----------
    x : np.ndarray
        Audio signal to align
    wp : np.ndarray
        Warping path (frames)
    fs : int
        Sampling rate
    hop_length : int, optional
        Hop length used for feature extraction

    Returns:
    --------
    np.ndarray
        Aligned audio signal
    """
    # Map frames to samples
    time_warped = librosa.frames_to_samples(wp[:, 1], hop_length=hop_length)
    time_original = librosa.frames_to_samples(wp[:, 0], hop_length=hop_length)

    # Interpolate the audio signal based on the warping path
    aligned_audio = np.interp(
        np.arange(time_original[-1] + 1),
        time_warped,
        x[:min(len(x), len(time_warped))],
    )
    return aligned_audio


def create_full_transition(x_1, x_2, wp, fs, crossfade_duration=1.0):
    """
    Create a full audio file containing the entire first track that transitions into the second track.

    Parameters:
    -----------
    x_1 : np.ndarray
        First audio signal (played in full)
    x_2 : np.ndarray
        Second audio signal (transitioned into)
    wp : np.ndarray
        Warping path (frames)
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

    # Align the second track using the warping path
    aligned_x2 = align_audio_with_dtw(x_2, wp, fs)

    # Ensure the first track is long enough for the crossfade
    transition_start = len(x_1) - crossfade_samples
    if transition_start < 0:
        raise ValueError("First audio signal is too short for the specified crossfade duration.")

    # Calculate the total length of the output signal
    total_length = max(len(x_1), transition_start + len(aligned_x2))

    # Create the output array
    output = np.zeros(total_length)

    # Copy the first signal
    output[:len(x_1)] = x_1

    # Create crossfade weights
    fade_out = np.linspace(1, 0, crossfade_samples)
    fade_in = np.linspace(0, 1, crossfade_samples)

    # Adjust lengths to match the transition region
    aligned_x2 = aligned_x2[:len(output) - transition_start]

    # Debugging shape mismatches
    print(f"Output shape: {output[transition_start:transition_start + crossfade_samples].shape}")
    print(f"Fade out shape: {fade_out.shape}")
    print(f"Aligned x2 fade in shape: {aligned_x2[:crossfade_samples].shape}")

    # Apply the crossfade
    output[transition_start:transition_start + crossfade_samples] *= fade_out
    aligned_x2[:crossfade_samples] *= fade_in

    # Add the second signal starting at the transition point
    output[transition_start:transition_start + len(aligned_x2)] += aligned_x2

    return output


def main():
    try:
        # Load audio files
        print("Loading audio files...")
        x_1, fs = librosa.load("bunny.mp3", sr=None)
        x_2, fs = librosa.load("music.mp3", sr=None)

        # Ensure mono audio
        if x_1.ndim > 1:
            x_1 = np.mean(x_1, axis=1)
        if x_2.ndim > 1:
            x_2 = np.mean(x_2, axis=1)

        print("Calculating chroma features...")
        # Calculate chroma features
        hop_length = 1024
        x_1_chroma = librosa.feature.chroma_cqt(y=x_1, sr=fs, hop_length=hop_length)
        x_2_chroma = librosa.feature.chroma_cqt(y=x_2, sr=fs, hop_length=hop_length)

        print("Computing DTW...")
        # Compute DTW
        D, wp = librosa.sequence.dtw(X=x_1_chroma, Y=x_2_chroma, metric="cosine")

        print("Creating transition...")
        # Create full audio with transition
        full_audio = create_full_transition(x_1, x_2, wp, fs, crossfade_duration=2.0)

        print("Saving output file...")
        # Save the result
        sf.write("full_transition.wav", full_audio, fs)
        print("Done! Output saved as 'full_transition.wav'")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
