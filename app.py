import os
import uuid
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)

# ডাউনলোড ফোল্ডার ঠিক করা
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
        return jsonify({'success': False, 'message': 'লিংক দিন!'})

    try:
        # ইউনিক নাম জেনারেট করা যাতে এক ফাইলের সাথে আরেকটা না মিলে যায়
        video_id = str(uuid.uuid4())
        output_filename = f"{DOWNLOAD_FOLDER}/{video_id}.%(ext)s"

        ydl_opts = {
            'outtmpl': output_filename,  # ফাইল কোথায় সেভ হবে
            'format': 'best',
            'noplaylist': True,
            'quiet': True,
        }

        # ভিডিও ডাউনলোড করা হচ্ছে সার্ভারে
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True) # download=True দিলাম
            filename = ydl.prepare_filename(info)
            
            # ফাইলের আসল নামটা বের করে আনা (কারণ এক্সটেনশন mp4/mkv হতে পারে)
            final_filename = os.path.basename(filename)

            return jsonify({
                'success': True,
                'title': info.get('title', 'TikTok Video'),
                'thumbnail': info.get('thumbnail'),
                'download_url': f"/download/{final_filename}" # লোকাল ডাউনলোড লিংক
            })

    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'message': 'ডাউনলোড করা যাচ্ছে না। লিংকটি চেক করুন।'})

# এই রুট ফাইলটি সার্ভার থেকে ইউজারের কাছে পাঠাবে
@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"File not found: {e}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)