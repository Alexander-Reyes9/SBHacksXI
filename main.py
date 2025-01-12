import librosa
import numpy as np
import requests
import time
import random
from scipy import signal
import sounddevice as sd
import threading
from collections import deque
from fastdtw import fastdtw
from queue import Queue


class MoodBasedMusicPlayer:
    def __init__(self):
        self.songs = None
        self.TS_VAL = 0.20
        self.SAMPLE_RATE = 22050
        self.current_song = None
        self.next_song = None
        self.mood_values = deque(maxlen=1000)
        self.is_playing = False
        self.playback_queue = Queue()
        self.mood_ready = threading.Event()
        self.next_song_ready = threading.Event()

    def get_current_mood(self):
        try:
            response = requests.get("http://0.0.0.0:5001/get_mood")
            return response.json()["current_mood"]
        except Exception as e:
            print(f"Error getting mood: {e}")
            return 0.5

    def find_closest_song(self, target_mood):
        closest_song = min(self.songs.items(),
                           key=lambda x: abs(x[1] - target_mood))
        print(f"Target mood: {target_mood}")
        print(f"Selected next song: {closest_song[0]} with energy {closest_song[1]}")
        return closest_song[0]

    def load_and_partition_song(self, song_name):
        """Load song and create partitions"""
        print(f"Loading and partitioning song: {song_name}")
        try:
            y, sr = librosa.load(song_name, sr=self.SAMPLE_RATE)
            print(f"Successfully loaded {song_name}, duration: {len(y) / self.SAMPLE_RATE:.2f}s")
        except Exception as e:
            print(f"Error loading {song_name}: {e}")
            return None

        # Remove first and last 10 seconds
        trim_samples = 30 * sr
        y = y[trim_samples:-trim_samples]

        total_duration = len(y)
        transition_duration = int(total_duration * 0.15)
        sample_duration = int(total_duration * self.TS_VAL)

        partitions = {
            'pre_transition': y[:transition_duration],
            'sample': y[transition_duration:transition_duration + sample_duration],
            'post_transition': y[transition_duration + sample_duration:]
        }

        print(f"Partition lengths (samples):")
        for name, part in partitions.items():
            print(f"- {name}: {len(part)} ({len(part) / self.SAMPLE_RATE:.2f}s)")

        return partitions

    def create_simple_crossfade(self, end_segment, start_segment, crossfade_duration=2.0):
        """Create a simple crossfade between segments"""
        print("Creating crossfade transition")

        # Convert duration to samples
        crossfade_length = int(crossfade_duration * self.SAMPLE_RATE)

        # Ensure segments are long enough
        if len(end_segment) < crossfade_length or len(start_segment) < crossfade_length:
            crossfade_length = min(len(end_segment), len(start_segment))
            print(f"Adjusted crossfade length to {crossfade_length} samples")

        # Create fade curves
        fade_out = np.linspace(1.0, 0.0, crossfade_length)
        fade_in = np.linspace(0.0, 1.0, crossfade_length)

        # Apply crossfade
        end_fade = end_segment[-crossfade_length:] * fade_out
        start_fade = start_segment[:crossfade_length] * fade_in

        # Combine with crossfade
        transition = end_fade + start_fade

        print(f"Created transition of length: {len(transition) / self.SAMPLE_RATE:.2f}s")
        return transition

    def sample_mood_thread(self, duration):
        """Thread function for sampling mood"""
        print(f"Starting mood sampling for {duration} seconds")
        start_time = time.time()
        self.mood_values.clear()

        while time.time() - start_time < duration:
            mood = self.get_current_mood()
            self.mood_values.append(mood)
            time.sleep(0.1)

        average_mood = np.mean(list(self.mood_values))
        print(f"Mood sampling complete. Average mood: {average_mood}")

        self.next_song = self.find_closest_song(average_mood)
        self.next_song_ready.set()

    def prepare_next_song_thread(self):
        """Thread function for preparing the next song"""
        self.next_song_ready.wait()
        print("Preparing next song...")
        next_partitions = self.load_and_partition_song(self.next_song)
        self.playback_queue.put(next_partitions)
        print("Next song prepared and queued")
        self.next_song_ready.clear()

    def play_audio_segment(self, audio_data, sample_rate, blocking=True):
        """Helper function to play audio with proper error handling"""
        try:
            sd.play(audio_data, sample_rate)
            if blocking:
                sd.wait()
                print("Finished playing segment")
        except Exception as e:
            print(f"Error playing audio: {e}")

    def playback_thread(self):
        """Thread function for continuous audio playback"""
        while self.is_playing:
            if self.current_song is None:
                self.current_song = random.choice(list(self.songs.keys()))
                print(f"Selected initial song: {self.current_song}")

            current_partitions = self.load_and_partition_song(self.current_song)
            if current_partitions is None:
                print(f"Error loading {self.current_song}, skipping...")
                continue

            # Start mood sampling thread
            sample_duration = len(current_partitions['sample']) / self.SAMPLE_RATE
            mood_thread = threading.Thread(
                target=self.sample_mood_thread,
                args=(sample_duration,)
            )
            prepare_thread = threading.Thread(
                target=self.prepare_next_song_thread
            )

            # Play pre-transition
            print("Playing pre-transition")
            self.play_audio_segment(current_partitions['pre_transition'], self.SAMPLE_RATE)

            # Play sample portion and start analysis
            print("Playing sample portion and starting analysis")
            mood_thread.start()
            prepare_thread.start()
            self.play_audio_segment(current_partitions['sample'], self.SAMPLE_RATE)

            # Wait for next song preparation
            print("Waiting for mood analysis and next song preparation")
            mood_thread.join()
            prepare_thread.join()

            # Get next song partitions
            next_partitions = self.playback_queue.get()
            if next_partitions is None:
                print("Error getting next song partitions")
                continue

            # Create and play transition
            print("Creating transition")
            transition = self.create_simple_crossfade(
                current_partitions['post_transition'][:self.SAMPLE_RATE * 2],  # Use 2 seconds
                next_partitions['pre_transition'][:self.SAMPLE_RATE * 2]
            )

            print(f"Playing transition from {self.current_song} to {self.next_song}")
            self.play_audio_segment(transition, self.SAMPLE_RATE)

            # Update current song
            self.current_song = self.next_song
            print(f"Now playing: {self.current_song}")

    def run(self):
        """Main method to start the player"""
        self.is_playing = True
        print("Starting music playback system")

        playback_thread = threading.Thread(target=self.playback_thread)
        playback_thread.start()

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Stopping playback...")
            self.is_playing = False
            playback_thread.join()


if __name__ == "__main__":
    player = MoodBasedMusicPlayer()
    player.songs = {
            "gym.mp3": 0.2,
            "lana.mp3": 0.4,
            "lmfao.mp3": 0.6,
        }
    player.run()