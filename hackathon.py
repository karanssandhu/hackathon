from flask import Flask, render_template, request, send_file
from PIL import Image, ImageOps
import io
import base64

app = Flask(__name__)

def process_image(input_image, remove_metadata=True, encrypt=False):
    try:
        metadata = None
        image = Image.open(input_image)

        if 'A' in image.getbands():
            image = image.convert('RGB')

        if 'exif' in image.info:
            metadata_bytes = image.info['exif']
            if remove_metadata:
                image = ImageOps.exif_transpose(image)
        else:
            metadata_bytes = None

        if metadata_bytes:
            metadata_hex = metadata_bytes.hex()
        else:
            metadata_hex = None

        if encrypt:
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="JPEG")
            image_data = image_bytes.getvalue()

            encrypted_image = base64.b64encode(image_data).decode()
            return encrypted_image, metadata_hex

        processed_image_io = io.BytesIO()
        image.save(processed_image_io, format="JPEG")

        processed_image_base64 = base64.b64encode(processed_image_io.getvalue()).decode()
        return processed_image_base64, metadata_hex
    except Exception as e:
        return str(e), None

def decrypt_image(encrypted_image):
    try:
        decrypted_data = base64.b64decode(encrypted_image.encode())
        decrypted_image_io = io.BytesIO(decrypted_data)
        return decrypted_image_io
    except Exception as e:
        return str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No image uploaded."

        image_file = request.files['image']

        if image_file.filename == '':
            return "No image selected."

        remove_metadata = request.form.get('remove_metadata', False)
        encrypt = request.form.get('encrypt', False)

        if encrypt:
            processed_image, metadata = process_image(image_file, remove_metadata, encrypt)
        else:
            return "Encryption is not selected. Please enable encryption."

        if isinstance(processed_image, str):
            if not processed_image.startswith('/9j/'):
                return f"Error processing image: {processed_image}"

        if encrypt:
            encrypted_image_filename = 'encrypted_image.jpg'
            with open(encrypted_image_filename, 'wb') as encrypted_file:
                encrypted_file.write(base64.b64decode(processed_image.encode()))

            decrypted_image_io = decrypt_image(processed_image)

            return send_file(
                decrypted_image_io,
                as_attachment=True,
                download_name='decrypted_image.jpg',
                mimetype='image/jpeg'
            )
        return render_template('index.html', image=processed_image, metadata=metadata)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
