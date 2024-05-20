from flask import Flask, send_from_directory
import os
import random

# Initialize the Flask application
app = Flask(__name__)

# Directory where the photos are stored
PHOTOS_DIR = './photos'

@app.route('/get_image')
def get_photo():
    # get a random photo from the folder and return it
    photo = ""
    def get_random_photo():
        photos = os.listdir(PHOTOS_DIR)
        photo = random.choice(photos)
        return photo

    photo = get_random_photo()
    print(photo)

    return send_from_directory(PHOTOS_DIR, photo)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)