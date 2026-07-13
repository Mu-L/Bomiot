from django.contrib.auth import get_user_model
from django.db.models import JSONField
from django_filters import CharFilter, NumberFilter, DateFilter, DateTimeFilter, BooleanFilter, RangeFilter
from django_filters import FilterSet
from bomiot.server.core import models
# Get user model
User = get_user_model()

# define JSONField filter support more lookup_expr
def generate_jsonfield_filter(lookup_expr, filter_class):
    """
    create JSONField filter parameter
    :param lookup_expr: get（exact, icontains...）
    :return: filter parameter
    """
    return {
        JSONField: {
            'filter_class': filter_class,
            'extra': lambda f: {
                'lookup_expr': lookup_expr
            },
        }
    }

JSONFIELD_FILTER_OVERRIDE = {
    # String filters
    **generate_jsonfield_filter('exact', CharFilter),
    **generate_jsonfield_filter('iexact', CharFilter),
    **generate_jsonfield_filter('contains', CharFilter),
    **generate_jsonfield_filter('icontains', CharFilter),
    # Number filters (support integers and floats)
    **generate_jsonfield_filter('exact', NumberFilter),  # exact match for numbers (int/float)
    **generate_jsonfield_filter('lt', NumberFilter),  # less than
    **generate_jsonfield_filter('lte', NumberFilter),  # less than or equal
    **generate_jsonfield_filter('gt', NumberFilter),  # greater than
    **generate_jsonfield_filter('gte', NumberFilter),  # greater than or equal
    # Boolean filters
    **generate_jsonfield_filter('exact', BooleanFilter),  # exact match for boolean values
    # Date filters
    **generate_jsonfield_filter('exact', DateFilter),  # exact match for dates
    **generate_jsonfield_filter('lt', DateFilter),  # less than
    **generate_jsonfield_filter('lte', DateFilter),  # less than or equal
    **generate_jsonfield_filter('gt', DateFilter),  # greater than
    **generate_jsonfield_filter('gte', DateFilter),  # greater than or equal
    # DateTime filters
    **generate_jsonfield_filter('exact', DateTimeFilter),  # exact match for datetime
    **generate_jsonfield_filter('lt', DateTimeFilter),  # less than
    **generate_jsonfield_filter('lte', DateTimeFilter),  # less than or equal
    **generate_jsonfield_filter('gt', DateTimeFilter),  # greater than
    **generate_jsonfield_filter('gte', DateTimeFilter),  # greater than or equal
    # Range filters
    **generate_jsonfield_filter('range', RangeFilter),  # range filter for numbers, dates, etc.
}

class ExampleFilter(FilterSet):
    """
    Example filter
    """
    class Meta:
        model = models.Example
        fields = '__all__'
        filter_overrides = JSONFIELD_FILTER_OVERRIDE
