"""应用异常定义。"""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """统一的 API 错误响应结构。"""

    code: str
    message: str
    request_id: str | None = None


class AetherLabError(Exception):
    """AetherLab 应用异常基类。"""


class ResourceNotFoundError(AetherLabError):
    """请求的资源不存在时抛出的异常。"""
