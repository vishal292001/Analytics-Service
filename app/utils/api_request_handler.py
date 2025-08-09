import asyncio
import inspect
import json
import logging
import traceback
from typing import Any

import jwt
from fastapi import HTTPException, status, Request
from jose.exceptions import JWTError
from pydantic.v1 import ValidationError
from sqlalchemy.orm import Session


# Initialize logger
logger = logging.getLogger('fastapi')

async def handle_api_request(
        request: Request,
        db: Session ,  # Add db as a parameter
        schema=None,
        query_schema=None,  # Schema for validating query parameters
        helper_function=None,
        *helper_args: Any,  # Arguments for the helper function
        **helper_kwargs: Any  # Keyword arguments for the helper function
):
    """
    Handles API requests, including validation, and delegates the logic to a helper function.

    Args:
        request: The incoming FastAPI request object.
        db: The database session for the request.
        schema: Pydantic model for validating request body (for POST/PUT).
        query_schema: Pydantic model for validating query params (for GET).
        helper_function: Function to process the validated data.

    Returns:
        JSONResponse: The API response based on the processed data or errors.
    """
    parsed_body = query_params = status_code = e = None
    try:
        logger.info(f"Processing {request.method} request to {request.url}")
        content_type = request.headers.get("content-type")
        # Handle GET request with optional query params validation

        if request.method == "GET":
            query_params = request.query_params
            if query_schema:
                logger.debug("Validating query parameters using schema.")

                query_model_instance = query_schema(**dict(query_params))  # Validate query params
                response = helper_function(db, query_model_instance, *helper_args,
                                                 **helper_kwargs)
            else:
                logger.debug(f"Calling helper function with query params: {query_params}")
                if query_params:
                    response = helper_function(db, dict(query_params), *helper_args, **helper_kwargs)
                else:
                    response = helper_function(db, *helper_args, **helper_kwargs)

        # Handle POST/PUT requests with optional body validation
        elif request.method in ["POST", "PUT", "DELETE"]:
            # Handle POST and PUT requests with JSON body
            parsed_body = await parse_request_body(request, content_type)

            if schema:
                logger.debug("Validating request body using schema.")
                model_instance = schema(**parsed_body)
                signature = inspect.signature(helper_function)
                if 'file' in signature.parameters:
                    response = helper_function(db, model_instance, *helper_args,
                                                     **helper_kwargs, file=parsed_body.get('file'))
                else:
                    response = await helper_function(db, model_instance, *helper_args,
                                                     **helper_kwargs)
            else:
                response = await helper_function(db, parsed_body, *helper_args,
                                                 **helper_kwargs)

        else:
            logger.error(f"Method {request.method} not allowed.")
            status_code = status.HTTP_405_METHOD_NOT_ALLOWED
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                detail="Method not allowed")

        return response


    except ValidationError as ex:
        e = ex
        logger.error(f"Validation error: {ex}")
        status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status_code":status_code,
            "error": str(e)
            }


    except Exception as ex:
        e = ex
        logger.exception(f"Unexpected error occurred: {ex}")
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status_code":status_code,
            "error": str(e)
            }


# Utility function to parse the request body based on content type
# async def parse_request_body(request: Request, content_type: str):
#     if request.query_params:
#         return dict(request.query_params)
#     elif content_type == "application/json":
#         raw_body = await request.body()
#         # raw_body = request.body()
#         return json.loads(raw_body) if raw_body else {}
#     elif (content_type.startswith("multipart/form-data") or
#           content_type =='application/x-www-form-urlencoded'):
#         raw_body = await request.form()
#         return dict(raw_body)
#     return {}


async def parse_request_body(request: Request, content_type: str):
    if request.query_params:
        return dict(request.query_params)
    elif content_type == "application/json":
        raw_body = await request.body()
        return json.loads(raw_body) if raw_body else {}
    elif content_type.startswith("multipart/form-data"):
        form = await request.form()
        file = form.get("file")  # "file" should match the name used in your upload form/Postman
        return file
        # return form  # Don't convert to dict — this preserves UploadFile object
    return {}


