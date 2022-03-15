from logging import getLogger
from sqlite3 import connect

__all__ = ("initdb", "stow")

log = getLogger("gps303")

DB = None

SCHEMA = """create table if not exists events (
    timestamp real not null,
    imei text,
    clntaddr text not null,
    proto int not null,
    payload blob
)"""


def initdb(dbname):
    global DB
    DB = connect(dbname)
    DB.execute(SCHEMA)


def stow(clntaddr, timestamp, imei, proto, payload):
    assert DB is not None
    parms = dict(
        zip(
            ("clntaddr", "timestamp", "imei", "proto", "payload"),
            (str(clntaddr), timestamp, imei, proto, payload),
        )
    )
    log.debug("inserting %s", parms)
    DB.execute(
        """insert or ignore into events
                (timestamp, imei, clntaddr, proto, payload)
                values (:timestamp, :imei, :clntaddr, :proto, :payload)""",
        parms,
    )
    DB.commit()
