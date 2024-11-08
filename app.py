from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pytubefix as pytube
from urllib.parse import quote_plus
import io
import re

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_audio_route():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL do vídeo não fornecida."}), 400

    try:
        yt = pytube.YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()

        if not stream:
            return jsonify({"error": "Nenhum stream de áudio encontrado."}), 404

        audio_stream = io.BytesIO()
        stream.stream_to_buffer(audio_stream)
        audio_stream.seek(0)

        filename = re.sub(r'[^\w\s-]', '', yt.title).strip()
        filename = filename.replace(" ", "_") + ".mp4"


        filename = quote_plus(filename)

        response = Response(
            audio_stream,
            mimetype="audio/mp4",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Expose-Headers": "Content-Disposition"  
            }
        )

        return response

    except pytube.exceptions.PytubeError as e:
        return jsonify({"error": f"Erro ao acessar o conteúdo: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Erro ao baixar o conteúdo: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3000)
