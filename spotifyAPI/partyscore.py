import librosa
import numpy as np
import os


# Load the audio file
def load_audio(filename):
    """
    Load an audio file using librosa.

    Args:
        filename (str): Path to the audio file.

    Returns:
        tuple: Audio time series and sampling rate.
    """
    return librosa.load(filename)


# Compute tempo using onset strength
def compute_tempo(y, sr):
    """
    Calculate the tempo of an audio signal.

    Args:
        y (ndarray): Audio time series.
        sr (int): Sampling rate.

    Returns:
        float: Tempo in beats per minute.
    """
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    return tempo


# Calculate the energy of an audio signal
def compute_energy(y):
    """
    Compute the spectral energy of an audio signal.

    Args:
        y (ndarray): Audio time series.

    Returns:
        float: Energy value.
    """
    return np.sum(librosa.feature.rms(y=y) ** 2)


# Normalize a value between a specified range
def normalize(value, min_value, max_value):
    """
    Normalize a value to a range of 0 to 1.

    Args:
        value (float): Value to normalize.
        min_value (float): Minimum range value.
        max_value (float): Maximum range value.

    Returns:
        float: Normalized value.
    """
    return (value - min_value) / (max_value - min_value) if max_value > min_value else 0


# Calculate the "party score" for a song
def calculate_party_score(y, sr):
    """
    Calculate the party score of a song based on tempo and energy.

    Args:
        y (ndarray): Audio time series.
        sr (int): Sampling rate.

    Returns:
        float: Party score.
    """
    tempo = compute_tempo(y, sr)
    energy = compute_energy(y)

    normalized_tempo = normalize(tempo, 60, 200)  # Expected tempo range: 60-200 BPM
    normalized_energy = normalize(energy, 0, 1)  # Expected energy range: 0-1

    return (normalized_tempo + normalized_energy) / 2


# Analyze a single song and return its party score
def analyze_song(filename):
    """
    Analyze a song to compute its party score.

    Args:
        filename (str): Path to the audio file.

    Returns:
        float: Party score or None in case of an error.
    """
    try:
        y, sr = load_audio(filename)
        return calculate_party_score(y, sr)
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None


# Append song scores to an external dictionary
def append_song_scores_to_dict(folder_path, results_dict):
    """
    Process all MP3 files in the specified folder and append their scores to a dictionary.

    Args:
        folder_path (str): Path to the folder containing MP3 files.
        results_dict (dict): Dictionary to append results to.

    Returns:
        None
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist!")
        return

    # Get all MP3 files in the folder
    mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')]

    if not mp3_files:
        print(f"No MP3 files found in folder '{folder_path}'!")
        return

    # Process each MP3 file
    for mp3_file in mp3_files:
        file_path = os.path.join(folder_path, mp3_file)
        party_score = analyze_song(file_path)

        if party_score is not None:
            # Ensure scalar values are stored
            score_value = party_score.item() if isinstance(party_score, np.ndarray) else party_score
            results_dict[mp3_file] = score_value

    print(f"Processed {len(mp3_files)} files and updated the results dictionary.")


if __name__ == "__main__":
    # Define the folder containing the playlist
    playlist_folder = os.path.join(os.getcwd(), "playlist")

    # Initialize an empty dictionary to hold results
    party_scores = {}

    # Append scores to the dictionary
    append_song_scores_to_dict(playlist_folder, party_scores)

    # Normalize the scores and print results
    if party_scores:
        min_score = min(party_scores.values())
        max_score = max(party_scores.values())

        for song in party_scores:
            party_scores[song] = normalize(party_scores[song], min_score, max_score)

        print("\nNormalized Party Scores:")
        for song, score in sorted(party_scores.items(), key=lambda x: x[1]):
            print(f"{song}: {score:.2f}")
