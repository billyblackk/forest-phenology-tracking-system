from fastapi import Request

from fpts.query.service import QueryService
from fpts.processing.raster_service import RasterService


def get_query_service(request: Request) -> QueryService:
    return request.app.state.query_service


def get_raster_service(request: Request) -> RasterService:
    return request.app.state.raster_service
