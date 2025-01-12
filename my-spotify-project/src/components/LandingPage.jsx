import React, { useState } from 'react';
import { Music, ArrowRight } from 'lucide-react';

const LandingPage = () => {
  const [playlistUrl, setPlaylistUrl] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (playlistUrl.includes('spotify.com/playlist/')) {
      setSubmitted(true);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 to-blue-900 flex flex-col items-center justify-center p-4">
      {/* Animated background circles */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute w-64 h-64 rounded-full bg-purple-600/20 blur-xl animate-pulse -top-32 -left-32" />
        <div className="absolute w-64 h-64 rounded-full bg-blue-600/20 blur-xl animate-pulse top-1/2 right-32" />
        <div className="absolute w-64 h-64 rounded-full bg-indigo-600/20 blur-xl animate-pulse bottom-32 -left-32" />
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-2xl w-full text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold text-white">
            Share Your Vibes
          </h1>
          <p className="text-lg text-purple-100">
            Connect with others through the power of music. Add your Spotify playlist and start sharing.
          </p>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 space-y-6">
          {!submitted ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex items-center gap-4 p-3 bg-white/5 rounded-lg border border-white/20">
                <Music className="w-6 h-6 text-purple-300" />
                <input
                  type="text"
                  value={playlistUrl}
                  onChange={(e) => setPlaylistUrl(e.target.value)}
                  placeholder="Paste your Spotify playlist URL"
                  className="flex-1 bg-transparent text-white placeholder-purple-300 outline-none"
                />
              </div>
              <button
                type="submit"
                className="w-full py-3 px-6 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
              >
                Share Playlist
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          ) : (
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto">
                <Music className="w-8 h-8 text-green-400" />
              </div>
              <h3 className="text-xl text-white font-medium">Playlist Added!</h3>
              <p className="text-purple-200">
                Your musical vibes are now part of our community.
              </p>
              <button
                onClick={() => setSubmitted(false)}
                className="text-purple-300 hover:text-purple-100 transition-colors"
              >
                Add another playlist
              </button>
            </div>
          )}
        </div>

        <p className="text-sm text-purple-200">
          Note: Make sure your playlist is set to public on Spotify
        </p>
      </div>
    </div>
  );
};

export default LandingPage;
