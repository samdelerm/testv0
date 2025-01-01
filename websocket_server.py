from flask import Flask, render_template, request, jsonify, Response
import requests

app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Redirige la requête vers le simulateur à l'adresse http://127.0.0.1:7070
        target_url = "http://127.0.0.1:7070"
        response = requests.get(target_url, stream=True)
        return Response(response.iter_content(), status=response.status_code, content_type=response.headers['Content-Type'])
    except requests.ConnectionError:
        return jsonify({"error": "Unable to connect to simulator"}), 500

@app.route('/proxy/<path:url>')
def proxy(url):
    try:
        # Redirige la requête vers le simulateur à l'adresse http://127.0.0.1:7070
        target_url = f"http://127.0.0.1:7070/{url}"
        response = requests.get(target_url, stream=True)
        return Response(response.iter_content(), status=response.status_code, content_type=response.headers['Content-Type'])
    except requests.ConnectionError:
        return jsonify({"error": "Unable to connect to simulator"}), 500

@app.route('/static/<path:filename>')
def static_proxy(filename):
    try:
        # Redirige la requête vers le simulateur pour les fichiers statiques
        target_url = f"http://127.0.0.1:7070/static/{filename}"
        response = requests.get(target_url, stream=True)
        return Response(response.iter_content(), status=response.status_code, content_type=response.headers.get('Content-Type', 'application/octet-stream'))
    except requests.ConnectionError:
        return jsonify({"error": "Unable to connect to simulator"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
