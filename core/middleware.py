class ActivityLogMiddleware:
    """
    Lightweight middleware placeholder for future request-level activity
    tracking (e.g. rate limiting, audit trails). Currently a pass-through;
    explicit activity logs are written directly from views via
    core.utils.log_activity() to keep the log meaningful and low-noise.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
