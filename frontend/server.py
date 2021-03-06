from os import environ

from flask import Flask
from flask import jsonify
from flask import request
from flask import abort
from flask import render_template
from flask import send_from_directory

app = Flask(__name__, static_url_path='')

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


readingTime = 0


@app.route('/metric', methods=['GET'])
def get_metric():
    global readingTime

    return jsonify({
        'reading_time': readingTime,
        'sdf': False
    })


@app.route('/metric', methods=['POST'])
def post_metric():
    if not request.is_json:
        abort(400)

    data = request.json
    print(data)

    global readingTime
    readingTime += int(data['reading_time'])

    return jsonify(data)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


def main():
    host = str(environ.get("APPLICATION_HOST", "netx.ru"))
    port = int(environ.get("APPLICATION_PORT", 8080))

    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
