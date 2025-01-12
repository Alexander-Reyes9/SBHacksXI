# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials

# class SpotifyAPIError(Exception):
#     """
#     Custom exception for Spotify API errors.
#     """
#     pass

# def get_playlist_tracks(playlist_url, client_id, client_secret):
#     """
#     Given a Spotify playlist URL, returns a list of tuples with
#     (track_name, track_artists, danceability, energy).
#     """
#     # Initialize Spotipy with your credentials
#     auth_manager = SpotifyClientCredentials(
#         client_id=client_id,
#         client_secret=client_secret
#     )

#     # Handle token deprecation warning
#     try:
#         token = auth_manager.get_access_token(as_dict=False)
#     except Exception as e:
#         raise SpotifyAPIError(f"Failed to get access token: {e}")

#     sp = spotipy.Spotify(auth=token)

#     # Extract playlist ID from the URL
#     try:
#         playlist_id = playlist_url.split("playlist/")[1].split("?")[0]
#     except IndexError:
#         raise ValueError("Invalid playlist URL format.")

#     # Retrieve playlist items
#     try:
#         results = sp.playlist_items(playlist_id)
#     except spotipy.exceptions.SpotifyException as e:
#         raise SpotifyAPIError(f"Failed to fetch playlist items: {e}")

#     tracks_info = []

#     for item in results['items']:
#         track = item['track']
#         if track is None:
#             continue

#         track_id = track['id']
#         track_name = track['name']
#         artists = [artist['name'] for artist in track['artists']]

#         # Retrieve audio features like danceability and energy
#         if track_id:
#             try:
#                 features = sp.audio_features(track_id)[0]
#                 if features:
#                     danceability = features.get('danceability', 0)
#                     energy = features.get('energy', 0)
#                 else:
#                     danceability = 0
#                     energy = 0

#                 tracks_info.append((track_name, artists, danceability, energy))

#             except spotipy.exceptions.SpotifyException as e:
#                 print(f"Error fetching audio features for track '{track_name}': {e}")

#     return tracks_info

# if __name__ == "__main__":
#     CLIENT_ID = "19fc7beb79d74265a06c14557fe4c926"  # Replace with your Spotify Client ID
#     CLIENT_SECRET = "0a4aa5e0b4494361bbb99f670b567f30"  # Replace with your Spotify Client Secret

#     playlist_link = input("Enter the Spotify playlist link: ")

#     try:
#         track_data = get_playlist_tracks(playlist_link, CLIENT_ID, CLIENT_SECRET)

#         if not track_data:
#             print("No tracks found or unable to retrieve track information.")
#         else:
#             for track_name, artists, danceability, energy in track_data:
#                 print(f"{track_name} - {', '.join(artists)} - "
#                       f"Danceability: {danceability:.2f} - Energy: {energy:.2f}")

#     except SpotifyAPIError as e:
#         print(f"An error occurred: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
