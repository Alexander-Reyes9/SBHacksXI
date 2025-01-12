import librosa
import numpy as np
import librosa.display
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Load the audio file
def load_audio(filename):
    y, sr = librosa.load(filename)
    return y, sr

# Compute tempo and beat frames
def get_tempo(y, sr):
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    return tempo

# Compute spectral energy (energy content)
def get_energy(y):
    energy = np.sum(librosa.feature.rms(y=y) ** 2)
    return energy

# Function to normalize between 0 and 1
def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value)

# Determine the "party score"
def calculate_party_score(y, sr):
    # Extract features
    tempo = get_tempo(y, sr)
    energy = get_energy(y)

    # Normalize values
    normalized_tempo = normalize(tempo, 60, 200)  # Assuming tempos range from 60 to 200 BPM
    normalized_energy = normalize(energy, 0, 1)  # Assuming energy ranges from 0 to 1

    # Combine features into a party score (could adjust weights as needed)
    party_score = (normalized_tempo + normalized_energy) / 2

    return party_score

# Analyze the song
def analyze_song(filename):
    try:
        y, sr = load_audio(filename)
        party_score = calculate_party_score(y, sr)
        return party_score
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return None

def process_playlist_folder():
    # Get the current working directory
    current_dir = os.getcwd()
    playlist_dir = os.path.join(current_dir, "playlist")
    
    # Check if playlist directory exists
    if not os.path.exists(playlist_dir):
        print("Error: 'playlist' folder not found!")
        return
    
    # Get all MP3 files in the playlist directory
    mp3_files = [f for f in os.listdir(playlist_dir) if f.lower().endswith('.mp3')]
    
    if not mp3_files:
        print("No MP3 files found in the playlist folder!")
        return
    
    # Dictionary to store results
    results = {}
    
    # Process each MP3 file
    for mp3_file in mp3_files:
        file_path = os.path.join(playlist_dir, mp3_file)
        party_score = analyze_song(file_path)
        
        if party_score is not None:
            # Extract scalar value from the party score
            party_score_value = party_score.item() if isinstance(party_score, np.ndarray) else party_score
            results[mp3_file] = party_score_value
    
    # Normalize the party scores
    if results:
        min_score = min(results.values())
        max_score = max(results.values())

        for song in results:
            results[song] = normalize(results[song], min_score, max_score)
    
    # Sort results by normalized party score (ascending order)
    sorted_results = dict(sorted(results.items(), key=lambda x: x[1]))

    # Print results
    print("\nNormalized Party Scores for all songs (ascending order):")
    print("-" * 50)
    for song, score in sorted_results.items():
        print(f"{song}: {score:.2f}")
    
    # Calculate average party score
    if results:
        avg_score = sum(results.values()) / len(results)
        print("\nAverage normalized party score: {:.2f}".format(avg_score))

if __name__ == "__main__":
    process_playlist_folder()
