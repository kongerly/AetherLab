"""健康检查路由。"""

from fastapi import APIRouter

health_router = APIRouter(prefix="/health", tags=["Health"])


@health_router.get("")
async def health() -> dict[str, str]:
    """返回后端服务当前的健康状态。"""
    return {
        "status": "ok",
        "service": "aetherlab",
    }
