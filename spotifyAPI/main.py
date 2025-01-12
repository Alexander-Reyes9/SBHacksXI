# Code snippet that Christopher copies and pastes
from partyscore import append_song_scores_to_dict

# Initialize an empty dictionary for storing results
party_scores = {}

# Define the folder containing the MP3 files
playlist_folder = "./playlist"

# Call the function
append_song_scores_to_dict(playlist_folder, party_scores)

# Print the results
if party_scores:
    print("\nParty Scores Dictionary:")
    for song, score in sorted(party_scores.items(), key=lambda x: x[1]):
        print(f"{song}: {score:.2f}")
else:
    print("No scores were calculated.")
