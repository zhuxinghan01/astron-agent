import ctypes

from common.metrology_auth.base import BaseClass


class Authorization(BaseClass):

    def __init__(self, ctype_filename):
        self.lib = self.get_lib(ctype_filename)

        class CheckReturnType(ctypes.Structure):
            _fields_ = [
                ("r0", ctypes.c_char_p),
                ("r1", ctypes.c_char_p),
                ("r2", ctypes.c_char_p),
            ]

        class CheckV2ReturnType(ctypes.Structure):
            _fields_ = [
                ("r0", ctypes.c_char_p),
                ("r1", ctypes.c_char_p),
                ("r2", ctypes.c_char_p),
            ]

        self.CheckReturnType = CheckReturnType
        self.CheckV2ReturnType = CheckV2ReturnType

        self.lib.Check.restype = self.CheckReturnType
        self.lib.Check.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_int,
            ctypes.c_char_p,
        ]

        self.lib.CheckV2.restype = self.CheckV2ReturnType
        self.lib.CheckV2.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_int,
            ctypes.c_char_p,
        ]

        self.lib.Check_Init.restype = ctypes.c_char_p
        self.lib.Check_Init.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_int,
            ctypes.c_char_p,
        ]

        self.lib.Check_Fini.restype = None
        self.lib.Check_Fini.argtypes = []

        self.check_inited = False

    def check_init(self, url, pro, gro, service, version, mode, channel_list, sname):
        url = url.encode()
        pro = pro.encode()
        gro = gro.encode()
        service = service.encode()
        version = version.encode()
        sname = sname.encode()
        channel_array = (ctypes.c_char_p * len(channel_list))(
            *[c.encode("utf-8") for c in channel_list]
        )
        result = self.lib.Check_Init(
            url,
            pro,
            gro,
            service,
            version,
            mode,
            channel_array,
            len(channel_list),
            sname,
        )
        if not result:
            self.check_inited = True
            return None
        else:
            return result.decode()

    def check(self, appid, uid, channel, func_list, tag):
        # if self.check_inited is False:
        #     raise Exception("check not inited")
        appid = appid.encode()
        uid = uid.encode()
        channel = channel.encode()
        func_array = (ctypes.c_char_p * len(func_list))(
            *[f.encode() for f in func_list]
        )
        tag = tag.encode()
        check_result = self.lib.Check(
            appid, uid, channel, func_array, len(func_list), tag
        )
        return (
            check_result.r0.decode() if check_result.r0 else None,
            check_result.r1.decode() if check_result.r1 else None,
            check_result.r2.decode() if check_result.r2 else None,
        )

    def checkV2(self, appid, uid, channel, func_list, tag):
        # if self.check_inited is False:
        #     raise Exception("check not inited")
        appid = appid.encode()
        uid = uid.encode()
        channel = channel.encode()
        func_array = (ctypes.c_char_p * len(func_list))(
            *[f.encode() for f in func_list]
        )
        tag = tag.encode()
        check_result = self.lib.CheckV2(
            appid, uid, channel, func_array, len(func_list), tag
        )
        return (
            check_result.r0.decode() if check_result.r0 else None,
            check_result.r1.decode() if check_result.r1 else None,
            check_result.r2.decode() if check_result.r2 else None,
        )

    def check_fini(self):
        self.lib.Check_Fini()
