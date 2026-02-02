from fastapi import Request

from fpts.query.service import QueryService


def get_query_service(request: Request) -> QueryService:
    return request.app.state.query_service
