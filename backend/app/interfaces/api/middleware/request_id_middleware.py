"""Request ID Middleware.

Generates a unique X-Request-ID for every incoming request and propagates
it in the response headers. Useful for distributed tracing and logging.
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that injects an X-Request-ID header."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Check if the client provided one, otherwise generate a new UUID4
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Attach to request state for access in routes/services
        request.state.request_id = request_id
        
        # Process the request
        response = await call_next(request)
        
        # Inject the ID into the response headers
        response.headers["X-Request-ID"] = request_id
        return response
