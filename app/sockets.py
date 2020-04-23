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
    team = Team.query.filter_by(tcode=data['room']).first()
    join_room(team.chatroom)
    emit('general', "Joined room")

@socketio.on('team_message')
def send_team_message(data):
    team = Team.query.filter_by(tcode=data['room']).first()
    now = datetime.datetime.now()
    db_team_chat = TeamChat(
        sender_username=current_user.username,
        team_code=data['room'],
        message=data['message'],
        time=now
    )
    db.session.add(db_team_chat)
    db.session.commit()
    payLoad = {
        'username': current_user.username, 
        'message': data['message'],
        'time': now.strftime("%I:%M:%p")
    }
    emit('team_message', payLoad, room=team.chatroom)