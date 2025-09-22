"""
conc.py
"""

import ctypes

from common.metrology_auth.base import BaseClass


class Concurrent(BaseClass):

    def __init__(self, ctype_filename):
        self.lib = self.get_lib(ctype_filename)

        class ResultType(ctypes.Structure):
            _fields_ = [
                ("_pass", ctypes.c_int),
                ("addr", ctypes.c_char_p),
                ("currentUsed", ctypes.c_char_p),
                ("err", ctypes.c_char_p),
            ]

        self.ResultType = ResultType

        self.lib.Conc_Init.restype = ctypes.c_char_p
        self.lib.Conc_Init.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        self.lib.AcquireConc.restype = ResultType
        self.lib.AcquireConc.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        self.lib.ReleaseConc.restype = ctypes.c_char_p
        self.lib.ReleaseConc.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        self.conc_inited = False

    def conc_init(self, url, pro, gro, service, version, mode, addr, sname):
        url = url.encode()
        pro = pro.encode()
        gro = gro.encode()
        service = service.encode()
        version = version.encode()
        addr = addr.encode()
        sname = sname.encode()
        result = self.lib.Conc_Init(url, pro, gro, service, version, mode, addr, sname)
        if not result:
            self.conc_inited = True
            return None
        else:
            return result.decode()

    def acquire_conc(self, sid, appid, channel, function):
        sid = sid.encode()
        appid = appid.encode()
        channel = channel.encode()
        function = function.encode()
        conc_result = self.lib.AcquireConc(sid, appid, channel, function)
        return (
            conc_result._pass,
            conc_result.addr.decode() if conc_result.addr else "",
            conc_result.currentUsed.decode() if conc_result.currentUsed else "",
            conc_result.err.decode() if conc_result.err else "",
        )

    def release_conc(self, sid, appid, channel, function):
        sid = sid.encode()
        appid = appid.encode()
        channel = channel.encode()
        function = function.encode()
        conc_result = self.lib.ReleaseConc(sid, appid, channel, function)
        return conc_result.decode() if conc_result else ""
