from functools import lru_cache

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.utils.decorators import sync_and_async_middleware
from django.utils.functional import SimpleLazyObject

from .utils import get_user_agent


@sync_and_async_middleware
class UserAgentMiddleware(object):
    """
    Middleware that adds a ``user_agent`` and ``user_agent_parsed`` object to
    the request object.

    Uses an in-memory LRU cache for performance.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request):
        # Add user agent data to the request
        request.user_agent = SimpleLazyObject(lambda: get_user_agent(request))

        response = await self.get_response(request)
        return response

    def __call__(self, request):
        # Add user agent data to the request
        request.user_agent = SimpleLazyObject(lambda: get_user_agent(request))

        response = self.get_response(request)
        return response

    def _set_user_agent(self, request):
        if not hasattr(request, 'user_agent'):
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            user_agent_parsed = self._parse_user_agent(user_agent)
            request.user_agent = user_agent
            request.user_agent_parsed = user_agent_parsed

