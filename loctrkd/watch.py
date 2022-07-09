""" Watch for locevt and print them """

from configparser import ConfigParser
from datetime import datetime, timezone
from importlib import import_module
from logging import getLogger
from typing import Any, cast, List
import zmq

from . import common
from .zmsg import Bcast

log = getLogger("loctrkd/watch")


class ProtoModule:
    PROTO_PREFIX: str

    @staticmethod
    def parse_message(packet: bytes, is_incoming: bool = True) -> Any:
        ...


pmods: List[ProtoModule] = []


def runserver(conf: ConfigParser) -> None:
    global pmods
    pmods = [
        cast(ProtoModule, import_module("." + modnm, __package__))
        for modnm in conf.get("collector", "protocols").split(",")
    ]
    # Is this https://github.com/zeromq/pyzmq/issues/1627 still not fixed?!
    zctx = zmq.Context()  # type: ignore
    zsub = zctx.socket(zmq.SUB)  # type: ignore
    zsub.connect(conf.get("collector", "publishurl"))
    zsub.setsockopt(zmq.SUBSCRIBE, b"")

    try:
        while True:
            zmsg = Bcast(zsub.recv())
            print("Bcast:", zmsg)
            for pmod in pmods:
                if zmsg.proto.startswith(pmod.PROTO_PREFIX):
                    msg = pmod.parse_message(zmsg.packet, zmsg.is_incoming)
                    print("I" if zmsg.is_incoming else "O", zmsg.imei, msg)
    except KeyboardInterrupt:
        pass


if __name__.endswith("__main__"):
    runserver(common.init(log))
