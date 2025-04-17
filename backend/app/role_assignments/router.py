from fastapi import APIRouter

from .data_product.router import router as data_product_router
from .dataset.router import router as dataset_router
from .global_.router import router as global_router

router = APIRouter(prefix="/role_assignments", tags=["role_assignments"])
router.include_router(global_router)
router.include_router(data_product_router)
router.include_router(dataset_router)
