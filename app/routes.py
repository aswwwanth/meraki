from app import app

@app.route('/')
def hello_world():
    print("TESTING")
    return 'Hello, World!'

@app.route('/test')
def test():
    print("BLAH")
    return "TESTING"