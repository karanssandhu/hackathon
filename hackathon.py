from flask import Flask, render_template, request
from PIL import Image, ExifTags
import os

app = Flask(__name__)

# Directory to store uploaded images
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to extract metadata from an image
def extract_metadata(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        metadata = {}

        if exif_data:
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                metadata[tag_name] = value

        return metadata
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if an image was uploaded
        if 'image' not in request.files:
            return "No image uploaded."

        image_file = request.files['image']

        # Check if the file is empty
        if image_file.filename == '':
            return "No image selected."

        # Save the uploaded image
        image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(image_path)

        # Extract metadata from the image
        metadata = extract_metadata(image_path)

        # Provide metadata information to the user
        return render_template('metadata.html', metadata=metadata)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
