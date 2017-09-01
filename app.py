from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/server')
def server():
    return render_template("server.html")

@app.route('/keepass')
def keepass():
    return render_template("keepass.html")
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
