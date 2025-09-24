"""
__init__.py
"""

import json
import os
import platform
import socket
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import toml

from common.metrology_auth.calc import Metrology
from common.metrology_auth.conc import Concurrent
from common.metrology_auth.errors import ErrorCode, MASDKErrors
from common.metrology_auth.licc import Authorization


@dataclass
class MASDKRequest:
    sid: str
    appid: str
    channel: str
    function: str
    cnt: int
    uid: Optional[str] = None

    def to_dict(self):
        return {
            "sid": self.sid,
            "appid": self.appid,
            "channel": self.channel,
            "function": self.function,
            "cnt": self.cnt,
            "uid": self.uid,
        }


@dataclass
class MASDKResponse:
    code: int
    msg: str
    log: str


class MetrologyAuthorization:
    def __init__(
        self, url, pro, gro, service, version, mode, sname, channel_list, ctype_filename
    ):
        self.metrology = Metrology(ctype_filename)
        self.authorization = Authorization(ctype_filename)
        self.url = url
        self.pro = pro
        self.gro = gro
        self.service = service
        self.version = version
        self.mode = mode
        self.sname = sname
        self.channel_list = channel_list

        _ = self.authorization.check_init(
            self.url,
            self.pro,
            self.gro,
            self.service,
            self.version,
            self.mode,
            self.channel_list,
            self.sname,
        )
        # print(f"Check_Init result: {check_init_result}")

        _ = self.metrology.calc_init(
            self.url,
            self.pro,
            self.gro,
            self.service,
            self.version,
            self.mode,
            self.sname,
        )
        # print(f"Calc_Init result: {result}")

    def excute(self, masdk_request: MASDKRequest):
        now = datetime.now()
        tag = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        r0, r1, r2 = self.authorization.check(
            masdk_request.appid,
            masdk_request.uid,
            masdk_request.channel,
            [masdk_request.function],
            tag,
        )

        if r0 != "null":
            logInfo = {
                "request": masdk_request.to_dict(),
                "response": {
                    "r0": r0,
                    "r1": r1,
                    "r2": r2,
                },
            }
            return MASDKResponse(
                code=MASDKErrors.get_error(ErrorCode.AuthorizationCheckError).c,
                msg=MASDKErrors.get_error(ErrorCode.AuthorizationCheckError).m,
                log=json.dumps(logInfo, ensure_ascii=False),
            )

        r0, r1 = self.metrology.calc(
            masdk_request.appid,
            masdk_request.channel,
            masdk_request.function,
            masdk_request.cnt,
        )

        return MASDKResponse(
            code=MASDKErrors.get_error(ErrorCode.Successes).c,
            msg=MASDKErrors.get_error(ErrorCode.Successes).m,
            log="",
        )


class ConcurrentAuthorization:
    def __init__(
        self, url, pro, gro, service, version, mode, sname, channel_list, ctype_filename
    ):
        self.concurrent = Concurrent(ctype_filename)
        self.authorization = Authorization(ctype_filename)
        self.url = url
        self.pro = pro
        self.gro = gro
        self.service = service
        self.version = version
        self.mode = mode
        self.sname = sname
        self.channel_list = channel_list

        _ = self.authorization.check_init(
            self.url,
            self.pro,
            self.gro,
            self.service,
            self.version,
            self.mode,
            self.channel_list,
            self.sname,
        )

        _ = self.concurrent.conc_init(
            self.url,
            self.pro,
            self.gro,
            self.service,
            self.version,
            self.mode,
            get_local_ip(),
            self.sname,
        )

    def acquire(self, masdk_request: MASDKRequest):
        now = datetime.now()
        tag = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        r0, r1, r2 = self.authorization.checkV2(
            masdk_request.appid,
            masdk_request.uid,
            masdk_request.channel,
            [masdk_request.function],
            tag,
        )

        if r0 != "null":
            logInfo = {
                "request": masdk_request.to_dict(),
                "response": {
                    "r0": r0,
                    "r1": r1,
                    "r2": r2,
                },
            }
            return MASDKResponse(
                code=MASDKErrors.get_error(ErrorCode.AuthorizationCheckV2Error).c,
                msg=MASDKErrors.get_error(ErrorCode.AuthorizationCheckV2Error).m,
                log=json.dumps(logInfo, ensure_ascii=False),
            )
        for i in range(masdk_request.cnt):
            r0, r1, r2, r3 = self.concurrent.acquire_conc(
                masdk_request.sid,
                masdk_request.appid,
                masdk_request.channel,
                masdk_request.function,
            )

            if r0 != 1:
                logInfo = {
                    "request": masdk_request.to_dict(),
                    "response": {
                        "r0": r0,
                        "r1": r1,
                        "r2": r2,
                        "r3": r3,
                    },
                }
                return MASDKResponse(
                    code=MASDKErrors.get_error(ErrorCode.ConcurrentAcquireConcError).c,
                    msg=MASDKErrors.get_error(ErrorCode.ConcurrentAcquireConcError).m,
                    log=json.dumps(logInfo, ensure_ascii=False),
                )
        return MASDKResponse(
            code=MASDKErrors.get_error(ErrorCode.Successes).c,
            msg=MASDKErrors.get_error(ErrorCode.Successes).m,
            log="",
        )

    def release(self, masdk_request: MASDKRequest):
        for i in range(masdk_request.cnt):
            result = self.concurrent.release_conc(
                masdk_request.sid,
                masdk_request.appid,
                masdk_request.channel,
                masdk_request.function,
            )
            if result != "":
                logInfo = {
                    "request": masdk_request.to_dict(),
                    "response": {
                        "result": result,
                    },
                }
                return MASDKResponse(
                    code=MASDKErrors.get_error(ErrorCode.ConcurrentReleaseConcError).c,
                    msg=MASDKErrors.get_error(ErrorCode.ConcurrentReleaseConcError).m,
                    log=json.dumps(logInfo, ensure_ascii=False),
                )
        return MASDKResponse(
            code=MASDKErrors.get_error(ErrorCode.Successes).c,
            msg=MASDKErrors.get_error(ErrorCode.Successes).m,
            log="",
        )

    @contextmanager
    def excute(self, masdk_request: MASDKRequest):
        if not os.getenv("MASDK_SWITCH", 0):
            logInfo = {
                "request": masdk_request.to_dict(),
                "response": f"MASDK_SWITCH is {os.getenv('MASDK_SWITCH')}",
            }
            self.masdk_response = MASDKResponse(
                code=MASDKErrors.get_error(ErrorCode.MASDKClosedError).c,
                msg=MASDKErrors.get_error(ErrorCode.MASDKClosedError).m,
                log=json.dumps(logInfo, ensure_ascii=False),
            )
            yield self
            return
        self.masdk_response = MASDKResponse(
            code=MASDKErrors.get_error(ErrorCode.Successes).c,
            msg=MASDKErrors.get_error(ErrorCode.Successes).m,
            log="",
        )
        now = datetime.now()
        tag = now.strftime("%Y-%m-%d %H:%M:%S.%f")
        r0, r1, r2 = self.authorization.checkV2(
            masdk_request.appid,
            masdk_request.uid,
            masdk_request.channel,
            [masdk_request.function],
            tag,
        )
        if r0 != "null":
            logInfo = {
                "request": masdk_request.to_dict(),
                "response": {
                    "r0": r0,
                    "r1": r1,
                    "r2": r2,
                },
            }
            self.masdk_response = MASDKResponse(
                code=MASDKErrors.get_error(ErrorCode.AuthorizationCheckV2Error).c,
                msg=MASDKErrors.get_error(ErrorCode.AuthorizationCheckV2Error).m,
                log=json.dumps(logInfo, ensure_ascii=False),
            )
        else:
            for i in range(masdk_request.cnt):
                r0, r1, r2, r3 = self.concurrent.acquire_conc(
                    masdk_request.sid,
                    masdk_request.appid,
                    masdk_request.channel,
                    masdk_request.function,
                )
                if r0 != 1:
                    logInfo = {
                        "request": masdk_request.to_dict(),
                        "response": {
                            "r0": r0,
                            "r1": r1,
                            "r2": r2,
                            "r3": r3,
                        },
                    }
                    self.masdk_response = MASDKResponse(
                        code=MASDKErrors.get_error(
                            ErrorCode.ConcurrentAcquireConcError
                        ).c,
                        msg=MASDKErrors.get_error(
                            ErrorCode.ConcurrentAcquireConcError
                        ).m,
                        log=json.dumps(logInfo, ensure_ascii=False),
                    )
        try:
            yield self
        finally:
            for i in range(masdk_request.cnt):
                result = self.concurrent.release_conc(
                    masdk_request.sid,
                    masdk_request.appid,
                    masdk_request.channel,
                    masdk_request.function,
                )
                if result != "":
                    logInfo = {
                        "request": masdk_request.to_dict(),
                        "response": {
                            "result": result,
                        },
                    }
                    self.masdk_response = MASDKResponse(
                        code=MASDKErrors.get_error(
                            ErrorCode.ConcurrentReleaseConcError
                        ).c,
                        msg=MASDKErrors.get_error(
                            ErrorCode.ConcurrentReleaseConcError
                        ).m,
                        log=json.dumps(logInfo, ensure_ascii=False),
                    )


def copy_toml(source_file, target_file):
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            data = toml.load(f)
        with open(target_file, "w", encoding="utf-8") as f:
            toml.dump(data, f)
    except Exception:
        return MASDKErrors.get_error(ErrorCode.InitParamInvalidError)
    return


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    finally:
        s.close()
    return ip_address


class MASDK:

    def get_ctype_file_for_platform(self):
        current_file_path = os.path.abspath(__file__)
        operate_system = platform.system()
        if operate_system == "Windows":
            ctype_filename = os.path.dirname(current_file_path) + "/ma_sdk_windows.so"
        elif operate_system == "Linux":
            ctype_filename = os.path.dirname(current_file_path) + "/ma_sdk_linux_x64.so"
        elif operate_system == "Darwin":
            ctype_filename = (
                os.path.dirname(current_file_path) + "/ma_sdk_macos_arm64.so"
            )
        else:
            raise (MASDKErrors.get_error(ErrorCode.InitParamInvalidError))
        return ctype_filename

    def get_polaris_flag(self):
        polaris_flag = False
        if (
            self._polaris_url != ""
            and self._polaris_project != ""
            and self._polaris_group != ""
            and self._polaris_service != ""
            and self._polaris_version != ""
        ):
            polaris_flag = True
        return polaris_flag

    def get_mode(self):
        if self._rpc_config_file is not None:
            err = copy_toml(self._rpc_config_file, "./ma-sdk.toml")
            if err:
                raise (err)
            else:
                mode = 0
        elif self._polaris_flag is True:
            mode = 1
        else:
            err = copy_toml(
                os.path.dirname(self._current_file_path) + "/ma-sdk-default.toml",
                "./ma-sdk.toml",
            )
            if err:
                raise (err)
            else:
                mode = 0
        return mode

    def __init__(
        self,
        channel_list,
        strategy_type,
        polaris_url="",
        polaris_project="",
        polaris_group="",
        polaris_service="",
        polaris_version="",
        rpc_config_file=None,
        metrics_service_name=None,
    ):
        self._current_file_path = os.path.abspath(__file__)
        self._channel_list = channel_list
        self._strategy_type = strategy_type
        self._polaris_url = polaris_url
        self._polaris_project = polaris_project
        self._polaris_group = polaris_group
        self._polaris_service = polaris_service
        self._polaris_version = polaris_version
        self._rpc_config_file = rpc_config_file
        self._metrics_service_name = metrics_service_name

        self._ctype_filename = self.get_ctype_file_for_platform()

        self._polaris_flag = self.get_polaris_flag()
        self._mode = self.get_mode()

        for item in strategy_type:
            if item == "cnt":
                self.create_modular_method()
            if item == "conc":
                self.create_concurrent_method()

    def create_modular_method(self):
        self.modular_method = MetrologyAuthorization(
            self._polaris_url,
            self._polaris_project,
            self._polaris_group,
            self._polaris_service,
            self._polaris_version,
            self._mode,
            self._metrics_service_name,
            self._channel_list,
            self._ctype_filename,
        )

    def create_concurrent_method(self):
        self.concurrent_method = ConcurrentAuthorization(
            self._polaris_url,
            self._polaris_project,
            self._polaris_group,
            self._polaris_service,
            self._polaris_version,
            self._mode,
            self._metrics_service_name,
            self._channel_list,
            self._ctype_filename,
        )

    def metrology_authorization(self, masdk_request: MASDKRequest):
        if not os.getenv("MASDK_SWITCH", 0):
            logInfo = {
                "request": masdk_request.to_dict(),
                "response": f"MASDK_SWITCH is {os.getenv('MASDK_SWITCH')}",
            }
            return MASDKResponse(
                code=MASDKErrors.get_error(ErrorCode.MASDKClosedError).c,
                msg=MASDKErrors.get_error(ErrorCode.MASDKClosedError).m,
                log=json.dumps(logInfo, ensure_ascii=False),
            )
        if not hasattr(self, "modular_method"):
            logInfo = {
                "request": masdk_request.to_dict(),
                "response": "MASDK has no modular_method",
            }
            return MASDKResponse(
                code=MASDKErrors.get_error(ErrorCode.CntInitFailedError).c,
                msg=MASDKErrors.get_error(ErrorCode.CntInitFailedError).m,
                log=json.dumps(logInfo, ensure_ascii=False),
            )
        return self.modular_method.excute(masdk_request)

    def concurrent_authorization(self, masdk_request: MASDKRequest):
        return self.concurrent_method.excute(masdk_request)

    def acquire_concurrent(self, masdk_request: MASDKRequest):
        if not os.getenv("MASDK_SWITCH", 0):
            logInfo = {
                "request": masdk_request.to_dict(),
                "response": f"MASDK_SWITCH is {os.getenv('MASDK_SWITCH')}",
            }
            return MASDKResponse(
                code=MASDKErrors.get_error(ErrorCode.MASDKClosedError).c,
                msg=MASDKErrors.get_error(ErrorCode.MASDKClosedError).m,
                log=json.dumps(logInfo, ensure_ascii=False),
            )
        if not hasattr(self, "concurrent_method"):
            logInfo = {
                "request": masdk_request.to_dict(),
                "response": "MASDK has no concurrent_method",
            }
            return MASDKResponse(
                code=MASDKErrors.get_error(ErrorCode.ConcInitFailError).c,
                msg=MASDKErrors.get_error(ErrorCode.ConcInitFailError).m,
                log=json.dumps(logInfo, ensure_ascii=False),
            )
        return self.concurrent_method.acquire(masdk_request)

    def release_concurrent(self, masdk_request: MASDKRequest):
        if not os.getenv("MASDK_SWITCH", 0):
            logInfo = {
                "request": masdk_request.to_dict(),
                "response": f"MASDK_SWITCH is {os.getenv('MASDK_SWITCH')}",
            }
            return MASDKResponse(
                code=MASDKErrors.get_error(ErrorCode.MASDKClosedError).c,
                msg=MASDKErrors.get_error(ErrorCode.MASDKClosedError).m,
                log=json.dumps(logInfo, ensure_ascii=False),
            )
        if not hasattr(self, "concurrent_method"):
            logInfo = {
                "request": masdk_request.to_dict(),
                "response": "MASDK has no concurrent_method",
            }
            return MASDKResponse(
                code=MASDKErrors.get_error(ErrorCode.ConcInitFailError).c,
                msg=MASDKErrors.get_error(ErrorCode.ConcInitFailError).m,
                log=json.dumps(logInfo, ensure_ascii=False),
            )
        return self.concurrent_method.release(masdk_request)
