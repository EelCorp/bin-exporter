from flask import Flask
from prometheus_client import Gauge, start_http_server

app = Flask(__name__)

g = Gauge("bins_time_last_out", "time the bins last went out")
g.set_to_current_time()


@app.get("/")
def index() -> None:
    g.set_to_current_time()
    return "ew bins"

if __name__ == "__main__":
    start_http_server(4446)
    app.run(host="0.0.0.0", port=4445)