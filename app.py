import os
import uuid
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)

# Setup download folder
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/convert', methods=['POST'])
def convert_video():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({'success': False, 'message': 'Please provide a URL!'})

    try:
        # Generate a unique filename to avoid conflicts
        video_id = str(uuid.uuid4())
        output_filename = f"{DOWNLOAD_FOLDER}/{video_id}.%(ext)s"

        ydl_opts = {
            'outtmpl': output_filename,  # Where the file will be saved
            'format': 'best',
            'noplaylist': True,
            'quiet': True,
        }

        # Downloading video to the server
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Extract actual filename (since extension can be mp4, mkv, etc.)
            final_filename = os.path.basename(filename)

            return jsonify({
                'success': True,
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail'),
                'download_url': f"/download/{final_filename}" # Local download link
            })

    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'message': 'Download failed. Please check the link.'})

# This route sends the file from the server to the user
@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"File not found: {e}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
