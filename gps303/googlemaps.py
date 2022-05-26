import googlemaps as gmaps
from sqlite3 import connect

gclient = None


def init(conf):
    global gclient
    with open(conf["googlemaps"]["accesstoken"], encoding="ascii") as fl:
        token = fl.read().rstrip()
    gclient = gmaps.Client(key=token)


def lookup(mcc, mnc, gsm_cells, wifi_aps):
    kwargs = {
        "home_mobile_country_code": mcc,
        "home_mobile_network_code": mnc,
        "radio_type": "gsm",
        "carrier": "O2",
        "consider_ip": False,
        "cell_towers": [
            {
                "locationAreaCode": loc,
                "cellId": cellid,
                "signalStrength": sig,
            }
            for loc, cellid, sig in gsm_cells
        ],
        "wifi_access_points": [
            {"macAddress": mac, "signalStrength": sig} for mac, sig in wifi_aps
        ],
    }
    result = gclient.geolocate(**kwargs)
    if "location" in result:
        return result["location"]["lat"], result["location"]["lng"]
    else:
        raise ValueError("google geolocation: " + str(result))


if __name__.endswith("__main__"):
    from datetime import datetime, timezone
    import sys
    from .gps303proto import *

    db = connect(sys.argv[1])
    c = db.cursor()
    c.execute(
        """select tstamp, packet from events
            where proto in (?, ?)""",
        (WIFI_POSITIONING.PROTO, WIFI_OFFLINE_POSITIONING.PROTO),
    )
    init({"googlemaps": {"accesstoken": sys.argv[2]}})
    count = 0
    for timestamp, packet in c:
        obj = parse_message(packet)
        print(obj)
        avlat, avlon = lookup(obj.mcc, obj.mnc, obj.gsm_cells, obj.wifi_aps)
        print(
            "{} {:+#010.8g},{:+#010.8g}".format(
                datetime.fromtimestamp(timestamp), avlat, avlon
            )
        )
        count += 1
        if count > 10:
            break
