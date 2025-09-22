import ctypes

from common.metrology_auth.base import BaseClass


class Report(BaseClass):

    def __init__(self, ctype_filename):
        self.lib = self.get_lib(ctype_filename)

        self.lib.Report_Init.restype = ctypes.c_char_p
        self.lib.Report_Init.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        self.lib.Report.restype = ctypes.c_char_p
        self.lib.Report.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_uint),
        ]

        self.lib.Report_Fini.restype = None
        self.lib.Report_Fini.argtypes = []

        self.report_inited = False

    def report_init(self, url, pro, gro, service, version, mode, addr, sname):
        """
        初始化上报
        """
        url = url.encode()
        pro = pro.encode()
        gro = gro.encode()
        service = service.encode()
        version = version.encode()
        addr = addr.encode()
        sname = sname.encode()
        result = self.lib.Report_Init(
            url, pro, gro, service, version, mode, addr, sname
        )
        if not result:
            self.report_inited = True
            return None
        else:
            return result.decode()

    def report(self, channel, conc_info_keys, conc_info_values):
        channel = channel.encode()
        conc_info_keys_array = (ctypes.c_char_p * len(conc_info_keys))(
            *[k.encode() for k in conc_info_keys]
        )
        conc_info_values_array = (ctypes.c_uint * len(conc_info_values))(
            *conc_info_values
        )
        result = self.lib.Report(
            channel, conc_info_keys_array, len(conc_info_keys), conc_info_values_array
        )
        return result.decode() if result else None

    def report_fini(self):
        self.lib.Report_Fini()
