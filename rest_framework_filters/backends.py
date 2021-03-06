from contextlib import contextmanager

from django_filters.rest_framework import backends

from .filterset import FilterSet


@contextmanager
def noop(self):
    yield


class DjangoFilterBackend(backends.DjangoFilterBackend):
    default_filter_set = FilterSet

    @contextmanager
    def patch_for_rendering(self, request):
        """
        Patch `get_filter_class()` so the resulting filterset does not perform
        filter expansion during form rendering.
        """
        original = self.get_filter_class

        def get_filter_class(view, queryset=None):
            filter_class = original(view, queryset)
            filter_class.requested_filters = noop

            return filter_class

        self.get_filter_class = get_filter_class
        yield
        self.get_filter_class = original

    def to_html(self, request, queryset, view):
        # patching the behavior of `get_filter_class()` in this method allows
        # us to avoid maintenance issues with code duplication.
        with self.patch_for_rendering(request):
            return super(DjangoFilterBackend, self).to_html(request, queryset, view)
