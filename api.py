from flask import Flask, jsonify
import cv  # Import the mood_updater module

app = Flask(__name__)

@app.route('/get_mood', methods=['GET'])
def get_mood():
    return jsonify({"current_mood": cv.normalized_movement})

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(host="0.0.0.0", port=5001, debug=True)
