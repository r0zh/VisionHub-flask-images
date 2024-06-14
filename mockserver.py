from flask import Flask, send_from_directory, request
import os
import random

# Initialize the Flask application
app = Flask(__name__)

# Directory where the photos are stored
PHOTOS_DIR = './photos'

@app.route('/get_image', methods=['POST'])
def get_photo():
    print(request.get_json())
    ratio = request.get_json()['ratio']
    photos_directory = PHOTOS_DIR + '/' + ratio
    # get a random photo from the folder and return it
    photo = ""

    # get random photo from folder with ratio name
    def get_random_photo(photos_directory):
        photos = os.listdir(photos_directory)
        photo = random.choice(photos)
        return photo

    photo = get_random_photo(photos_directory)

    return send_from_directory(photos_directory, photo)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)