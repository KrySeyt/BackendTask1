from typing import Any

from fastapi.exceptions import RequestValidationError
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field


class ValidationErrorSchema(BaseModel):
    detail: list[dict[str, Any]] = Field(description="Default detail of validation error", example=[
        {
            "loc": [
                "body",
                "phone_number"
            ],
            "msg": "field required",
            "type": "value_error.missing",
        }
    ])
    body: dict[str, Any] = Field(description="Body of your request", example={
        "phone_operator_code": 900,
        "timezone": "Europe/Amsterdam",
        "id": 0,
        "tag": {
            "text": "Any text"
        }
    })
    params: dict[str, Any] = Field(description="Path and query parameters of your request", example={
        "deprecated_param": 1
    })


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "detail": exc.errors(),
            "body": exc.body,
            "params": {**request.path_params, **request.query_params}
        })
    )
