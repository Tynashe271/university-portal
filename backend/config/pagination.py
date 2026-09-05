from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Default pagination for every list endpoint.

    The frontend already asks for larger pages on dashboard panels that
    want everything in one request (e.g. `?page_size=500` for beds, staff
    profiles, fee accounts) rather than paging through results — and
    settings.py already declares PAGE_SIZE/MAX_PAGE_SIZE with that in
    mind. But the stock PageNumberPagination ignores a `page_size` query
    param unless page_size_query_param is explicitly set, so every one of
    those requests was silently capped at 20 results regardless of what
    was asked for — anything past the first 20 rows (the 21st book, the
    21st fee account, ...) never reached the page. This wires the param
    up for real, with the same ceiling settings.py already declares.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
