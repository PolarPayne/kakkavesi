from flask import Flask, abort
import datetime

from plot_pump_averages import make_plot
import station_network

app = Flask(__name__)

@app.route("/")
def index():
    return "Kakkavettä!"

@app.route("/avg/<code>/<start_date>/<end_date>")
def avg(code, start_date, end_date):
    filename = "JVP" + code + "_" + start_date + "_" + end_date + ".png"
    from os import path
    if not path.exists("static/tmp/" + filename):
        try:
            p = make_plot("JVP" + code, datetime.datetime.strptime(start_date, "%Y-%m-%d"), datetime.datetime.strptime(end_date, "%Y-%m-%d"))
            p.savefig("static/tmp/" + filename, dpi=300)
        except:
            abort(404)
    return "static/tmp/" + filename
    # return send_file("tmp/" + filename, mimetype='image/png')


@app.route("/neighbors/<code>/<int:depth>")
def neighbors(code, depth=1):
    stations = station_network.StationNetwork()
    ls = []
    for i in stations.neighbors(code, depth):
        ls.append(str(i.code))
    return "[" + ",".join(ls) + "]"

if __name__ == "__main__":
    app.run(debug=True)


