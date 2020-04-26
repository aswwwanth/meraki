from app import app, db, socketio
from app.models import *
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_login import current_user
import datetime

@socketio.on('message')
def connect(msg):
    print("Recieved: " + msg)
    emit('general', "Connected")

@socketio.on('join_team_channel')
def on_team_join(data):
    team = Team.query.filter_by(tcode=data['room']).first()
    join_room(team.chatroom)
    emit('general', "Joined room")

def get_private_room(a, b):
    if a > b:
        a, b = b, a
    return a + b

@socketio.on('join_new_messages_room')
def on_join_new_messages_room():
    print("Joining new messages room")
    join_room(current_user.chatroom)
    emit('general', 'Joined new messages', room=current_user.chatroom)

@socketio.on('join_private_room')
def on_private_join(data):
    print("Joining private room")
    print("Room = ", data['room'])
    if data['room'] != '':
        user = User.query.filter_by(username=data['room']).first()
        if user is not None:
            room = get_private_room(user.chatroom, current_user.chatroom)
            print("New room = ", room)
            join_room(room)
            print("Joined room")
            emit('general', "Joined room " + room)

@socketio.on('leave_private_room')
def on_private_leave(data):
    print("Leaving private room")
    print("Room = ", data['room'])
    if data['room'] != '':
        user = User.query.filter_by(username=data['room']).first()
        if user is not None:
            room = get_private_room(user.chatroom, current_user.chatroom)
            leave_room(room)
            print("Left room")
            emit('general', "Left room" + room)

@socketio.on('private_message')
def send_private_message(data):
    user = User.query.filter_by(username=data['room']).first()
    now = datetime.datetime.now()
    db_private_chat = PrivateChat(
        sender_username=current_user.username,
        recipient_username=data['room'],
        message=data['message'],
        time=now
    )
    db.session.add(db_private_chat)
    db.session.commit()
    payLoad = {
        'username': current_user.username, 
        'message': data['message'],
        'time': now.strftime("%I:%M %p")
    }
    room = get_private_room(user.chatroom, current_user.chatroom)
    emit('private_message', payLoad, room=room)
    print("sending new private message")
    print(payLoad)
    emit('new_private_message', payLoad, room=user.chatroom)

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
        'time': now.strftime("%I:%M %p")
    }
    emit('team_message', payLoad, room=team.chatroom)