from pydantic import BaseModel

from plugin.aitools.service.ase_sdk.__base.entities.req_data import BaseReqSourceData
from plugin.aitools.service.ase_sdk.ability.common.entities.req_data import Credentials


class Payload(BaseModel):
    # 数据体，图片二进制数据
    data: bytes


class Body(BaseModel):
    payload: Payload


class OcrLLMReqSourceData(BaseReqSourceData):
    credentials: Credentials
    body: Body
