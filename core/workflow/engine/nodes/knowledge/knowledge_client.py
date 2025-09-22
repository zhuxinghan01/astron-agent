import json
from typing import Any

from workflow.exception.e import CustomException
from workflow.exception.errors.err_code import CodeEnum
from workflow.extensions.otlp.trace.span import Span


class KnowledgeConfig:
    """
    Configuration class for knowledge base operations.

    This class holds all the necessary parameters for making requests to the knowledge base API.
    Documentation: http://10.1.87.65:3000/project/427/interface/api/17187
    """

    # TODO: Move knowledge base URL to configuration file

    def __init__(
        self,
        top_n: str,
        rag_type: str,
        repo_id: list,
        url: str,
        query: str,
        flow_id: str = "",
        doc_ids: list = [],
        threshold: float = 0.1,
    ):
        """
        Initialize knowledge configuration parameters.

        :param top_n: Number of top results to retrieve from knowledge base
        :param rag_type: Type of RAG (Retrieval-Augmented Generation) to use
        :param repo_id: List of repository IDs to search in
        :param url: Knowledge base API endpoint URL
        :param query: Search query string
        :param flow_id: Optional flow ID for context
        :param doc_ids: Optional list of specific document IDs to search
        :param threshold: Minimum similarity threshold for results (default: 0.1)
        """
        self.top_n = top_n
        self.rag_type = rag_type
        self.repo_id = repo_id
        self.url = url
        self.query = query
        self.flow_id = flow_id
        self.doc_ids = doc_ids
        self.threshold = threshold


"""
{
    "code": 0,
    "data": {
        "summary": "",
        "metadata": [
            "中国移动物联网-生态渠道运营部：和对讲CM13外观是怎样的呢？\n和对讲CM13按键怎么操作呢？\n您好，操作指示如下：  \n电源键：短按锁屏、解锁；长按 3 秒可开关机；\n通话键（PTT）：按下“通话键（PTT）”可发起对讲，松开可结束对讲；\n左右功能键：“左右功能键”对应屏幕下方显示的功能，短按“左右功能键”执行相应功能；\n上下功能键：短按或长按“上下功能键”可上下移动光标，在对讲页时可快捷切换频道； \n和对讲CM13刚开机时按键不能用如何解决呢？\n和对讲CM13主界面如何操作呢？\n和对讲CM13怎样新建或者加入群组呢？",
            "和对讲 CM13 使用简介： 菜单页面功能： 功能页面功能：2\n![Alt文本](https://oss-beijing-m8.openstorage.cn/SparkBotDev/repoRef/9c81308cce8d4574923db2a13d55ab66/unused1.jpg)\n1.CM13终端简介\n和对讲CM13是中国移动和对讲首批深度定制产品。\n聚焦基础对讲体验，外观小巧\n精致，音质完美。提供高质量的\n公网对讲体验，产品品质有保障。\n3\n![Alt文本](https://oss-beijing-m8.openstorage.cn/SparkBotDev/repoRef/9c81308cce8d4574923db2a13d55ab66/unused2.jpg)\n2.CM13按键说明\n 电源键：短按锁屏、解锁；长按 3 秒可开关机。\n 通话键（PTT）：按下“通话键（PTT）”可发起对讲，松开可结束对讲。\n 左右功能键：“左右功能键”对应屏幕下方显示的功能，短按“左右功能键”执行相应功能。"
        ]
    },
    "message": "success",
    "sid": "retrieval-summary00110001@sh18f55fae063000f202"
}

"""


class KnowledgeClient:
    """
    Client for interacting with the knowledge base API.

    This class handles HTTP requests to retrieve relevant information from the knowledge base
    using the provided configuration parameters.
    """

    headers = {"Content-Type": "application/json"}

    def __init__(self, *, config: KnowledgeConfig):
        """
        Initialize the knowledge client with configuration.

        :param config: KnowledgeConfig instance containing API parameters
        """
        self.config = config

    async def top_k(self, request_span: Span, **kwargs: Any) -> str:
        """
        Retrieve top-k results from the knowledge base.

        Makes an asynchronous HTTP POST request to the knowledge base API and returns
        the top-k most relevant results based on the configured parameters.

        :param request_span: Span object for tracing and logging
        :param kwargs: Additional keyword arguments including event_log_node_trace
        :return: JSON string containing the retrieved knowledge base results
        :raises CustomException: If the API request fails or returns an error code
        """
        url = self.config.url
        payload = self.payload()
        request_span.add_info_events({"url": url})
        request_span.add_info_events({"request_data": payload})
        try:
            event_log_node_trace = kwargs.get("event_log_node_trace")
            if event_log_node_trace:
                event_log_node_trace.append_config_data(
                    {"url": url, "req_headers": self.headers, "req_body": payload}
                )
            from aiohttp import ClientSession

            async with ClientSession() as session:
                async with session.post(
                    url, headers=self.headers, json=json.loads(payload)
                ) as resp:
                    background_json = json.loads(await resp.text())
                    # background_json = requests.request("POST", url, headers=self.headers, data=payload).json()
                    if background_json.get("code") != 0:
                        msg = (
                            f"err code {background_json.get('code')}, "
                            f"reason {background_json.get('message')}, sid {background_json.get('sid')}"
                        )
                        request_span.add_error_event(msg)
                        raise CustomException(
                            err_code=CodeEnum.KnowledgeRequestError,
                            err_msg=f"{msg}",
                            cause_error=f"{msg}",
                        )
                    request_span.add_info_events(
                        {"response": json.dumps(background_json, ensure_ascii=False)}
                    )
                    recall_contents = background_json.get("data", {})
                    recalls = json.dumps(recall_contents, ensure_ascii=False)
                    return recalls
        except Exception as e:
            err = str(e)
            request_span.add_error_event(err)
            raise CustomException(
                err_code=CodeEnum.KnowledgeRequestError,
                err_msg=f"Knowledge base POST request error: {err}",
                cause_error=f"Knowledge base POST request error: {err}",
            ) from e

    def payload(self) -> str:
        """
        Construct the request payload for knowledge base top-k retrieval.

        Creates a JSON payload containing all the necessary parameters for the
        knowledge base API request including query, topN, ragType, and match criteria.

        :return: JSON string containing the request payload
        """
        _payload = json.dumps(
            {
                "query": self.config.query,
                "topN": self.config.top_n,
                "ragType": self.config.rag_type,
                "match": {
                    "repoId": self.config.repo_id,
                    "docIds": self.config.doc_ids,
                    "flowId": self.config.flow_id,
                    "threshold": self.config.threshold,
                },
            },
            ensure_ascii=True,
        )

        return _payload
