import os
import spotipy
import spotipy.oauth2 as oauth2
import yt_dlp
from youtube_search import YoutubeSearch
import multiprocessing
import urllib.request
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error


def write_tracks(text_file: str, tracks: dict):
    # This includes the name, artist, and Spotify URL. Each is delimited by a comma.
    with open(text_file, 'w+', encoding='utf-8') as file_out:
        while True:
            for item in tracks['items']:
                if 'track' in item:
                    track = item['track']
                else:
                    track = item
                try:
                    track_url = track['external_urls']['spotify']
                    track_name = track['name']
                    track_artist = track['artists'][0]['name']
                    album_art_url = track['album']['images'][0]['url']  # still fetching, but not used
                    csv_line = track_name + "," + track_artist + "," + track_url + "," + album_art_url + "\n"
                    try:
                        file_out.write(csv_line)
                    except UnicodeEncodeError:  # Most likely caused by non-English song names
                        print("Track named {} failed due to an encoding error. This is most likely due to this song having a non-English name.".format(track_name))
                except KeyError:
                    print(u'Skipping track {0} by {1} (local only?)'.format(track['name'], track['artists'][0]['name']))
            # 1 page = 50 results, check if there are more pages
            if tracks['next']:
                tracks = spotify.next(tracks)
            else:
                break


def write_playlist(username: str, playlist_id: str):
    results = spotify.user_playlist(username, playlist_id, fields='tracks,next,name')
    playlist_name = results['name']
    text_file = u'{0}.txt'.format(playlist_name)  # Create text file for the playlist
    print(u'Writing {0} tracks to {1}.'.format(results['tracks']['total'], text_file))
    tracks = results['tracks']
    write_tracks(text_file, tracks)

    return playlist_name


def find_and_download_songs(reference_file: str):
    TOTAL_ATTEMPTS = 10
    with open(reference_file, "r", encoding='utf-8') as file:
        for line in file:
            temp = line.split(",")
            name, artist = temp[0], temp[1]
            text_to_search = artist + " - " + name
            best_url = None
            attempts_left = TOTAL_ATTEMPTS
            while attempts_left > 0:
                try:
                    results_list = YoutubeSearch(text_to_search, max_results=1).to_dict()
                    best_url = "https://www.youtube.com{}".format(results_list[0]['url_suffix'])
                    break
                except IndexError:
                    attempts_left -= 1
                    print("No valid URLs found for {}, trying again ({} attempts left).".format(text_to_search, attempts_left))
            if best_url is None:
                print("No valid URLs found for {}, skipping track.".format(text_to_search))
                continue

            print("Initiating download for {}.".format(text_to_search))
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s.mp3',  # Save as mp3
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }, {
                    'key': 'FFmpegMetadata',
                }]
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info([best_url][0], download=True)

                # Extract the name of the downloaded file from the info_dict
            filename = ydl.prepare_filename(info_dict)
            print(f"The downloaded file name is: {filename}.mp3")

            # Add cover image to the mp3 file (optional)
            print('Adding cover image (if any)...')
            audio = MP3(f'{filename}.mp3', ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass

            # Optional: Add cover art to the mp3 file (if desired)
            try:
                # Cover art is optional, commented out here
                # audio.tags.add(
                #     APIC(
                #         encoding=3,  # 3 is for utf-8
                #         mime="image/jpeg",  # can be image/jpeg or image/png
                #         type=3,  # 3 is for the cover image
                #         desc='Cover',
                #         data=open("{}.jpg".format(name), mode='rb').read()
                #     )
                # )
                audio.save()
            except Exception as e:
                print(f"Error adding cover art: {e}")

            # Cleanup: no need for image files anymore
            # os.remove("{}.jpg".format(name))  # No image files are downloaded or kept


# Multiprocessed implementation of find_and_download_songs
def multicore_find_and_download_songs(reference_file: str, cpu_count: int):
    lines = []
    with open(reference_file, "r", encoding='utf-8') as file:
        for line in file:
            lines.append(line)

    # Process allocation of songs per cpu
    number_of_songs = len(lines)
    songs_per_cpu = number_of_songs // cpu_count

    # Calculates number of songs that don't evenly fit into the cpu list
    extra_songs = number_of_songs - (cpu_count * songs_per_cpu)

    cpu_count_list = []
    for cpu in range(cpu_count):
        songs = songs_per_cpu
        if cpu < extra_songs:
            songs = songs + 1
        cpu_count_list.append(songs)

    # Split the songs among the available CPUs
    index = 0
    file_segments = []
    for cpu in cpu_count_list:
        right = cpu + index
        segment = lines[index:right]
        index = index + cpu
        file_segments.append(segment)

    # Prepares processes before starting them
    processes = []
    segment_index = 0
    for segment in file_segments:
        p = multiprocessing.Process(target=multicore_handler, args=(segment, segment_index))
        processes.append(p)
        segment_index += 1

    # Start and wait for all processes to complete
    for p in processes:
        p.start()

    for p in processes:
        p.join()


def multicore_handler(reference_list: list, segment_index: int):
    # Write the reference_list to a new "reference_file" for compatibility
    reference_filename = "{}.txt".format(segment_index)
    with open(reference_filename, 'w+', encoding='utf-8') as file_out:
        for line in reference_list:
            file_out.write(line)

    # Call the original find_and_download method
    find_and_download_songs(reference_filename)

    # Cleanup
    if os.path.exists(reference_filename):
        os.remove(reference_filename)


def enable_multicore(autoenable=False, maxcores=None, buffercores=1):
    native_cpu_count = multiprocessing.cpu_count() - buffercores
    if autoenable:
        if maxcores:
            if maxcores <= native_cpu_count:
                return maxcores
            else:
                print("Too many cores requested, single core operation fallback")
                return 1
        return native_cpu_count
    multicore_query = "Y"
    if multicore_query not in ["Y", "y", "Yes", "YES", "YEs", 'yes']:
        return 1
    core_count_query = 0
    if core_count_query == 0:
        return native_cpu_count
    else:
        return core_count_query if core_count_query <= native_cpu_count else 1


if __name__ == "__main__":
    # Parameters
    print("Please read README.md for use instructions.")
    if os.path.isfile('config.ini'):
        import configparser
        config = configparser.ConfigParser()
        config.read("config.ini")
        client_id = config["Settings"]["client_id"]
        client_secret = config["Settings"]["client_secret"]
        username = config["Settings"]["username"]
    else:
        client_id = input("Client ID: ")
        client_secret = input("Client secret: ")
        username = input("Spotify username: ")

    playlist_uri = input("Playlist link: ")
    multicore_support = enable_multicore(autoenable=False, maxcores=None, buffercores=1)
    auth_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    playlist_name = write_playlist(username, playlist_uri)
    reference_file = "{}.txt".format(playlist_name)

    # Create the playlist folder with a fixed name "playlist"
    playlist_folder = "playlist"
    if not os.path.exists(playlist_folder):
        os.makedirs(playlist_folder)

    os.rename(reference_file, os.path.join(playlist_folder, reference_file))
    os.chdir(playlist_folder)

    # Enable multicore support if needed
    if multicore_support > 1:
        multicore_find_and_download_songs(reference_file, multicore_support)
    else:
        find_and_download_songs(reference_file)

    os.remove(f'{reference_file}')
    print("Operation complete.")
