"""
Module for custom exception classes.
"""

from typing import Optional


class BaseAPIException(Exception):
    """Base exception for API errors."""

    # Status code to return if this exception is raised
    status_code: int

    # Generic detail of the exception (That may be returned in a response)
    response_detail: str

    detail: str

    def __init__(self, detail: str, response_detail: Optional[str] = None):
        """
        Initialise the exception.

        :param detail: Specific detail of the exception (just like Exception would take - this will only be logged
                       and not returned in a response).
        :param response_detail: Generic detail of the exception that will be returned in a response.
        """
        super().__init__(detail)

        self.detail = detail

        if response_detail is not None:
            self.response_detail = response_detail
