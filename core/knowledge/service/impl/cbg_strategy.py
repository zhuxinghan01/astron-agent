"""
CBG-RAG strategy implementation module
Implements RAG (Retrieval-Augmented Generation) functionality based on Spark LLM
"""
import base64
from typing import Any, Dict, List, Optional, TypedDict
from urllib.parse import unquote

from knowledge.domain.entity.rag_do import ChunkInfo, FileInfo
from knowledge.exceptions.exception import ProtocolParamException
from knowledge.infra.xinghuo import xinghuo
from knowledge.service.rag_strategy import RAGStrategy
from knowledge.utils.verification import check_not_empty


class QueryParams(TypedDict):
    """Query parameters type definition"""
    doc_ids: Optional[List[str]]
    repo_ids: Optional[List[str]]
    top_k: Optional[int]
    threshold: Optional[float]
    flow_id: Optional[str]


class SplitParams(TypedDict):
    """Split parameters type definition"""
    length_range: List[int]
    overlap: int
    resource_type: int
    separator: List[str]
    title_split: bool
    cut_off: List[str]


class CBGRAGStrategy(RAGStrategy):
    """CBG-RAG strategy implementation."""

    async def query(
            self,
            query: str,
            doc_ids: Optional[List[str]] = None,
            repo_ids: Optional[List[str]] = None,
            top_k: Optional[int] = None,
            threshold: Optional[float] = 0,
            **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute RAG query

        Args:
            query: Query text
            doc_ids: Document ID list
            repo_ids: Knowledge base ID list
            top_k: Number of results to return
            threshold: Similarity threshold
            **kwargs: Other parameters

        Returns:
            Query result dictionary
        """
        if not check_not_empty(doc_ids):
            raise ProtocolParamException("docIds is not empty")

        query_results = await xinghuo.new_topk_search(
            query=query, doc_ids=doc_ids, top_n=top_k, **kwargs
        )

        results = [dict]
        if check_not_empty(query_results):
            for result in query_results:
                if isinstance(result, dict):
                    if result.get("score", 0) < threshold:
                        continue

                    chunk_context = []
                    chunk_img_reference: Dict[str, Any] = {}  # Added type annotation
                    sorted_objects = []
                    chunk_info = result.get("chunk")

                    # Handle chunk_info as dictionary
                    if check_not_empty(chunk_info) and isinstance(chunk_info, dict):
                        chunk_context.append(chunk_info)

                        # Safely handle imgReference
                        img_ref = chunk_info.get("imgReference")
                        if check_not_empty(img_ref) and isinstance(img_ref, dict):
                            chunk_img_reference.update(img_ref)

                        # Handle overlap chunks
                        overlap_chunks = result.get("overlap", [])
                        if check_not_empty(overlap_chunks):
                            chunk_context.extend(overlap_chunks)
                            sorted_objects = sorted(
                                chunk_context, key=lambda x: x.get("dataIndex", 0)
                            )

                        # Build full context text
                        full_context = "".join(
                            obj.get("content", "") for obj in sorted_objects
                        ) if sorted_objects else chunk_info.get("content", "")

                        # Collect references from all chunks
                        for obj in sorted_objects or chunk_context:
                            obj_img_ref = obj.get("imgReference") if isinstance(obj, dict) else None
                            if check_not_empty(obj_img_ref) and isinstance(obj_img_ref, dict):
                                chunk_img_reference.update(obj_img_ref)

                        # Append processed result
                        results.append(
                            {
                                "score": result.get("score"),
                                "docId": chunk_info.get("fileId", ""),
                                "chunkId": chunk_info.get("id", ""),
                                "fileName": unquote(
                                    str(result.get("fileName", "")), encoding="utf-8"
                                ),
                                "content": chunk_info.get("content", ""),
                                "context": full_context,
                                "references": chunk_img_reference,
                            }
                        )

        return {
            "query": query,
            "count": len(results),
            "results": results,
        }

    async def split(
        self,
        file: str,
        lengthRange: List[int],
        overlap: int,
        resourceType: int,
        separator: List[str],
        titleSplit: bool,
        cutOff: List[str],
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Split file into multiple chunks

        Args:
            file: File content
            lengthRange: Length range
            overlap: Overlap length
            resourceType: Resource type
            separator: Separator list
            **kwargs: Other parameters

        Returns:
            List of split chunks
        """
        data = []
        wiki_split_extends: Dict[str, Any] = {}

        if check_not_empty(separator):
            split_chars = []
            for chars in separator:
                split_chars.append(
                    base64.b64encode(chars.encode("utf-8")).decode(encoding="utf-8")
                )
            wiki_split_extends["chunkSeparators"] = split_chars
        else:
            wiki_split_extends["chunkSeparators"] = ["DQo="]

        if check_not_empty(lengthRange) and len(lengthRange) > 1:
            wiki_split_extends["chunkSize"] = lengthRange[1]
            wiki_split_extends["minChunkSize"] = lengthRange[0]
        else:
            wiki_split_extends["chunkSize"] = 2000
            wiki_split_extends["minChunkSize"] = 256

        doc_upload_response_data = await xinghuo.upload(
            file, wiki_split_extends, resourceType, **kwargs
        )
        fileId = doc_upload_response_data.get("fileId", "")
        doc_chunks_response_data = await xinghuo.get_chunks(file_id=fileId, **kwargs)
        if check_not_empty(doc_chunks_response_data):
            for chunk in doc_chunks_response_data:
                data.append(
                    {
                        "docId": fileId,
                        "dataIndex": str(chunk.get("dataIndex", "")),
                        "title": "",
                        "content": chunk.get("content", ""),
                        "context": chunk.get("content", ""),
                        "references": chunk.get("imgReference", {}),
                    }
                )

        return data

    async def chunks_save(
        self, docId: str, group: str, uid: str, chunks: List[Any], **kwargs: Any
    ) -> Any:
        """
        Save chunks to knowledge base

        Args:
            docId: Document ID
            group: Group name
            uid: User ID
            chunks: Chunk list
            **kwargs: Other parameters

        Returns:
            Save result
        """
        data_chunks = []
        for chunk in chunks:
            data_chunks.append(
                {
                    "fileId": docId,
                    "chunkType": "RAW",
                    "content": chunk.get("content", ""),
                    "dataIndex": chunk.get("dataIndex"),
                    "imgReference": chunk.get("references"),
                }
            )

        return await xinghuo.dataset_addchunk(chunks=data_chunks, **kwargs)

    async def chunks_update(
        self, docId: str, group: str, uid: str, chunks: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        """
        Update chunks

        Args:
            docId: Document ID
            group: Group name
            uid: User ID
            chunks: Chunk list
            **kwargs: Other parameters

        Returns:
            Update result
        """
        for chunk in chunks:
            return await xinghuo.dataset_updchunk(chunk, **kwargs)

    async def chunks_delete(self, docId: str, chunkIds: List[str], **kwargs: Any) -> Any:
        """
        Delete chunks

        Args:
            docId: Document ID
            chunkIds: Chunk ID list
            **kwargs: Other parameters

        Returns:
            Delete result

        Raises:
            ProtocolParamException: When chunkIds is empty
        """
        if not check_not_empty(chunkIds):
            raise ProtocolParamException(msg="chunkIds is not empty")

        return await xinghuo.dataset_delchunk(chunk_ids=chunkIds, **kwargs)

    async def query_doc(self, docId: str, **kwargs: Any) -> List[dict]:
        """
        Query all chunks of a document

        Args:
            docId: Document ID
            **kwargs: Other parameters

        Returns:
            List of chunk information
        """
        result: List[dict] = []
        datas = await xinghuo.get_chunks(file_id=docId, **kwargs)

        for data in datas:
            references = data.get("imgReference", {})
            content_text = data.get("content", "")

            if isinstance(references, dict):
                for key, value in references.items():
                    content_text = content_text.replace(
                        "{" + key + "}", ""
                    )

            result.append(
                ChunkInfo(
                    docId=docId,
                    chunkId=data.get("dataIndex", ""),
                    content=content_text
                ).__dict__
            )
        sorted_by_age = sorted(result, key=lambda x: x["chunkId"])
        return sorted_by_age

    async def query_doc_name(self, docId: str, **kwargs: Any) -> Optional[dict]:
        """
        Query document name information

        Args:
            docId: Document ID
            **kwargs: Other parameters

        Returns:
            File information object
        """
        datas = await xinghuo.get_file_info(file_id=docId, **kwargs)
        file_name = unquote(datas.get("fileName", ""), encoding="utf-8")
        file_name_split = file_name.split("_")[2:]

        if file_name_split:
            file_name = "_".join(file_name_split)

        return FileInfo(
            docId=datas.get("fileId", ""),
            fileName=file_name,
            fileStatus=datas.get("fileStatus", ""),
            fileQuantity=datas.get("quantity", 0),
        ).__dict__
