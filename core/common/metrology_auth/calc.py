"""
calc.py
"""

import ctypes

from common.metrology_auth.base import BaseClass


class Metrology(BaseClass):

    def __init__(self, ctype_filename):
        self.lib = self.get_lib(ctype_filename)

        class CalcReturnType(ctypes.Structure):
            _fields_ = [("r0", ctypes.c_int), ("r1", ctypes.c_char_p)]

        self.CalcReturnType = CalcReturnType

        self.lib.Calc.restype = self.CalcReturnType

        self.lib.Calc.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_longlong,
        ]

        self.lib.Calc_Init.restype = ctypes.c_char_p
        self.lib.Calc_Init.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
        ]

        self.lib.Calc_Fini.restype = None
        self.lib.Calc_Fini.argtypes = []

        self.calc_inited = False

    def calc_init(self, url, pro, gro, service, version, mode, sname):
        url = url.encode()
        pro = pro.encode()
        gro = gro.encode()
        service = service.encode()
        version = version.encode()
        sname = sname.encode()
        result = self.lib.Calc_Init(url, pro, gro, service, version, mode, sname)
        if not result:
            self.calc_inited = True
            return None
        else:
            return result.decode()

    def calc(self, appid, channel, funcs, c):
        appid = appid.encode()
        channel = channel.encode()
        funcs = funcs.encode()
        calc_result = self.lib.Calc(appid, channel, funcs, c)
        return calc_result.r0, calc_result.r1.decode() if calc_result.r1 else None

    def calc_fini(self):
        self.lib.Calc_Fini()
