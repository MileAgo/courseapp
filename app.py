import os

from flask import Flask

app = Flask(__name__)

# Port is configurable so the app can listen on any port (default: 8000)
PORT = int(os.environ.get("PORT", 8000))


@app.route("/")
def index():
    message = "Hello from Benny's containerized app!"
    print(message)
    return f"<h1>{message}</h1><p>Listening on port {PORT}</p>"


if __name__ == "__main__":
    print(f"Starting Benny's server on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT)
