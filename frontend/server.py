from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from flask import abort
from flask import render_template
from flask import send_from_directory

app = Flask(__name__, static_url_path='')

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('js', path)

@app.route('/metric/', methods=['PATCH'])
def metric():
	if not request.is_json:
		abort(400)

	data = request.json
	print(data)

	return jsonify(data)

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

app.run(host='netx.ru', port=8080)
