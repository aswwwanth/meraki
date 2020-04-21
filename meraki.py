from app import app
from app import socketio
if __name__ == "__main__":
	# app.run(debug=True)
	socketio.run(app, debug=True, host='0.0.0.0')