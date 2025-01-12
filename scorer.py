import librosa
import numpy as np
import librosa.display
import matplotlib.pyplot as plt
import os


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

    # Convert party score to an integer
    return int(party_score * 100)  # Scale the party score for integer representation


# Analyze the song
def analyze_song(filename):
    # Extract file name
    file_name = os.path.basename(filename)

    y, sr = load_audio(filename)
    party_score = calculate_party_score(y, sr)

    return file_name, party_score

