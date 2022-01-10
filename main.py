import multiprocessing
import pychromecast
import time
import json
from flask import Flask, request, render_template, url_for

app = Flask(__name__)

# services, browser = pychromecast.discovery.discover_chromecasts()
# time.sleep(3)
# pychromecast.discovery.stop_discovery(browser)
# print(services,browser)
# print(cast.media_controller.status)


@app.route("/set_state")
def toggle():
    outfile = open("config.json", "r")
    #stringfile = str(outfile.read())
    state = request.args.get("state")
    if state.lower() in ['true', '1']:
        state = True
    else:
        state = False
    dict = json.load(outfile)
    dict["castOn"] = state
    strout = json.dumps(dict)
    outfile.close()

    outfile = open("config.json", "w")
    outfile.write(strout)
    outfile.close()

    is_on = 'on' if dict["castOn"] else 'off'
    return f"{is_on}"


@app.route("/get_state")
def state():
    outfile = open("config.json", "r")
    #stringfile = str(outfile.read())
    dict = json.load(outfile)
    dict["castOn"] = dict["castOn"]
    outfile.close()

    is_on = 'on' if dict["castOn"] else 'off'
    return f"{is_on}"


@app.route("/set_max_volume")
def set_max_volume():
    volume = int(request.args.get("volume"))
    if volume > 100:
        volume = 100
    elif volume < 0:
        volume = 0
    outfile = open("config.json", "r")
    #stringfile = str(outfile.read())
    dict = json.load(outfile)
    dict["maxVolume"] = volume
    strout = json.dumps(dict)
    outfile.close()

    outfile = open("config.json", "w")
    outfile.write(strout)
    outfile.close()

    return f"{volume}"


@app.route("/get_max_volume")
def get_max_volume():
    outfile = open("config.json", "r")
    #stringfile = str(outfile.read())
    dict = json.load(outfile)
    volume = dict["maxVolume"]
    outfile.close()

    return f"{volume}"


@app.route("/")
def index():
    outfile = open("config.json", "r")
    dict = json.load(outfile)
    outfile.close()
    return render_template('index.html', data=dict)


def main_cast():
    print('in loop')
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[
                                                               "Home Mini"])
    cast = chromecasts[0]
    cast.wait()
    time.sleep(1)
    f = open('config.json')
    cast_on = json.load(f)["castOn"]
    f.close()
    while True:
        if cast.media_controller.status.player_state == 'PLAYING':
            f = open('config.json', 'r')
            dict = json.load(f)
            cast_on = dict["castOn"]
            max_volume = dict["maxVolume"]
            f.close()
            if cast_on:
                volume = int(round(cast.status.volume_level, 2)*100)
                if volume > max_volume:
                    cast.set_volume(max_volume/100)
                    print(volume)
        time.sleep(5)
    print('done')
    pychromecast.discovery.stop_discovery(browser)


def run():
    app.run()


if __name__ == '__main__':
    p2 = multiprocessing.Process(target=run, args=())
    p = multiprocessing.Process(target=main_cast, args=())
    p2.start()
    p.start()
