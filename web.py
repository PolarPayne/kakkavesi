from flask import Flask, send_file

from plot_pump_averages import make_plot
import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return "Kakkavettä!"

@app.route("/avg/<code>")
def avg(code="1078"):
    filename = "JVP" + code
    p = make_plot(filename, datetime.datetime(2015, 1, 1), datetime.datetime(2015, 12, 31))
    p.savefig(filename + ".png")
    return send_file(filename + ".png", mimetype='image/png')

if __name__ == "__main__":
    app.run()