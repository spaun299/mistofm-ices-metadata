from flask import Flask, abort, request
import config
import json
import datetime
import pytz
import logging

app = Flask(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)


class Metadata:
    def __init__(self):
        self.max_songs = config.MAX_SONGS
        self.stations = {}
        self.tz = pytz.timezone('Europe/Uzhgorod')

    def add_song(self, station_name, song_name, played_to):
        if not self.stations.get(station_name):
            self.stations[station_name] = []
        if len(self.stations[station_name]) == self.max_songs:
            del self.stations[station_name][0]
        self.stations[station_name].append(
            {'name': song_name,
             'played_to': played_to or '%s:%s' % (
                 datetime.datetime.now(self.tz).hour, datetime.datetime.now(self.tz).minute)})

    def get_songs(self, station_name):
        return self.stations.get(station_name, {})

metadata = Metadata()


@app.route('/metadata/add/<string:station_name>/<string:song_name>', methods=['POST', 'GET'])
def metadata_add(station_name, song_name):
    if request.args.get('username', '') != config.USER_NAME \
            or request.args.get('password', '') != config.USER_PASSWORD:
        abort(403)
    metadata.add_song(station_name, song_name, request.args.get('play_to', None))
    return 'OK'


@app.route('/metadata/get/<string:station_name>')
def metadata_get(station_name):
    meta = metadata.get_songs(station_name)
    return json.dumps(meta)

if __name__ == '__main__':
    app.run('0.0.0.0', config.PORT)
