""" sqlite event store """

from sqlite3 import connect

__all__ = "initdb", "stow"

DB = None

SCHEMA = """create table if not exists events (
    tstamp real not null,
    imei text,
    peeraddr text not null,
    proto int not null,
    packet blob
)"""


def initdb(dbname):
    global DB
    DB = connect(dbname)
    DB.execute(SCHEMA)


def stow(**kwargs):
    assert DB is not None
    parms = {
        k: kwargs[k] if k in kwargs else v
        for k, v in (
            ("peeraddr", None),
            ("when", 0.0),
            ("imei", None),
            ("proto", -1),
            ("packet", b""),
        )
    }
    assert len(kwargs) <= len(parms)
    DB.execute(
        """insert or ignore into events
                (tstamp, imei, peeraddr, proto, packet)
                values
                (:when, :imei, :peeraddr, :proto, :packet)
        """,
        parms,
    )
    DB.commit()
