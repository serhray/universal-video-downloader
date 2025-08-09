from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)  # Permitir requests do Vercel

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "Video Downloader API"})

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return {"error": "URL não fornecida"}, 400

    # Nome de arquivo único para evitar conflitos
    filename = f"{uuid.uuid4()}.mp4"
    filepath = f"/tmp/{filename}"

    ydl_opts = {
        'outtmpl': filepath,
        'format': 'best',
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(filepath, as_attachment=True)

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        # Limpa o arquivo temporário
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
