from collections import OrderedDict, namedtuple

from rest_framework import (
    pagination
)


class CustomPagination(pagination.PageNumberPagination):
    page_size = 25
    max_page_size = 10000
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):

        count = self.page.paginator.count
        total_pages = count // self.page_size
        return OrderedDict([
            ('count', count),
            ('total_pages', total_pages),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])


def paginate(*, serializer, query_set, request):
    '''Paginate Queries'''
    paginator = CustomPagination()
    paginator_results = paginator.paginate_queryset(query_set, request)

    serialized_data = serializer(paginator_results, many=True).data
    return paginator.get_paginated_response(serialized_data)
