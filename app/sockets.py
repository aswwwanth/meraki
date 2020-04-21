from app import app, db, socketio
from app.models import *
from flask_socketio import SocketIO, send, emit, join_room
from flask_login import current_user
import datetime

@socketio.on('message')
def connect(msg):
    print("Recieved: " + msg)
    emit('general', "Connected")

@socketio.on('join_team_channel')
def on_join(data):
    # print("Room = ", data)
    team = Team.query.get(data['room'])
    join_room(team.tcode)
    emit('general', "Joined room")

@socketio.on('team_message')
def send_team_message(data):
    print("Team message = ", data);
    team = Team.query.get(data['room'])
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M:%p")
    print("Current Time =", current_time)
    payLoad = {
        'username': current_user.username, 
        'message': data['message'],
        'time': current_time
    }
    emit('team_message', payLoad, room=team.tcode)