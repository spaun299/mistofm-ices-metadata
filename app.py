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

    def add_song(self, station_id, song_name, play_from):
        if not self.stations.get(station_id):
            self.stations[station_id] = []
        if len(self.stations[station_id]) == self.max_songs:
            del self.stations[station_id][0]
        self.stations[station_id].append(
            {'name': song_name,
             'play_from': play_from or '%s:%s' % (
                 datetime.datetime.now(self.tz).hour, datetime.datetime.now(self.tz).minute)})

    def get_songs(self, station_id):
        return self.stations.get(station_id, {})

metadata = Metadata()


@app.route('/metadata/add/<string:station_id>/<string:song_name>', methods=['POST', 'GET'])
def metadata_add(station_id, song_name):
    if request.args.get('username', '') != config.USER_NAME \
            or request.args.get('password', '') != config.USER_PASSWORD:
        abort(403)
    metadata.add_song(station_id, song_name, request.args.get('play_from', None))
    return 'OK'


@app.route('/metadata/get/<string:station_id>')
def metadata_get(station_id):
    meta = metadata.get_songs(station_id)
    return json.dumps(meta)

if __name__ == '__main__':
    app.run('0.0.0.0', config.PORT)
