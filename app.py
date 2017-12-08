from flask import Flask, abort, request
import config
import json
import datetime
import pytz
import logging

app = Flask(__name__)
# logging.getLogger('werkzeug').setLevel(logging.INFO)


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
             'play_from': play_from or datetime.datetime.strftime(
                 datetime.datetime.now(self.tz), "%H:%M")})

    def get_songs(self, station_id, amount=5):
        songs = self.stations.get(station_id, [])
        if len(songs) <= amount:
            return songs
        return songs[-amount:]

    def get_current_song_name(self, station_id):
        songs = self.stations.get(station_id, [])
        if songs:
            return songs[-1]['name']
        return ''

metadata = Metadata()


@app.route('/metadata/add/<int:station_id>/', methods=['POST'])
def metadata_add(station_id):
    if request.form.get('username', '') != config.USER_NAME \
            or request.form.get('password', '') != config.USER_PASSWORD:
        abort(403)
    song_name = request.form.get('song_name')
    if not song_name:
        abort(400)
    metadata.add_song(station_id, song_name, request.form.get('play_from', None))
    return 'OK'


@app.route('/metadata/get/<int:station_id>')
def metadata_get(station_id):
    amount = request.args.get('amount', '')
    if (not amount.isdigit()) or int(amount) < 0:
        amount = 5
    meta = metadata.get_songs(station_id, amount=int(amount))
    return json.dumps(meta)


@app.route('/metadata/get/<int:station_id>/current_song')
def get_current_song_name(station_id):
    return json.dumps({"name": metadata.get_current_song_name(station_id)})


if __name__ == '__main__':
    app.run('0.0.0.0', config.PORT)
