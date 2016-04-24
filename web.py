from flask import Flask, send_file, abort

from plot_pump_averages import make_plot
import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return "Kakkavettä!"

@app.route("/avg/<code>/<start_date>/<end_date>")
def avg(code, start_date, end_date):
    filename = code + "_" + start_date + "_" + end_date + ".png"
    from os import path
    if not path.exists("tmp/" + filename):
        try:
            p = make_plot(code, datetime.datetime.strptime(start_date, "%Y-%m-%d"), datetime.datetime.strptime(end_date, "%Y-%m-%d"))
            p.savefig("tmp/" + filename)
        except:
            print("abort", code, start_date, end_date)
            abort(404)
    return send_file("tmp/" + filename, mimetype='image/png')

if __name__ == "__main__":
    app.run()