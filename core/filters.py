import django_filters
from .models import *

def apply_icontains_filter(filter_set):
    for field_name, filter_obj in filter_set.filters.items():
        if isinstance(filter_obj, django_filters.CharFilter):
            filter_obj.lookup_expr = 'icontains'
            filter_obj.label = f'{filter_obj.label} (similarity)'

#-----------------------------------------------------------------------------------------------------
# Usuario
#-----------------------------------------------------------------------------------------------------
class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter()
    name = django_filters.CharFilter()
    biography = django_filters.CharFilter()
    email = django_filters.CharFilter()
    phone_number = django_filters.CharFilter()
    birthdate = django_filters.DateFilter(lookup_expr='exact')

    class Meta:
        model = User
        fields = [
            'username', 
            'name', 
            'biography',
            'email', 
            'phone_number',
            'birthdate',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)
        
#-----------------------------------------------------------------------------------------------------
# Pais
#-----------------------------------------------------------------------------------------------------
class CountryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter()
    abbreviation = django_filters.CharFilter()
    dialing_code = django_filters.CharFilter()

    class Meta:
        model = Country
        fields = [
            'name',
            'abbreviation',
            'dialing_code',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)

#-----------------------------------------------------------------------------------------------------
# Estado
#-----------------------------------------------------------------------------------------------------
class StatusFilter(django_filters.FilterSet):
    name = django_filters.CharFilter()
    description = django_filters.CharFilter()

    class Meta:
        model = Status
        fields = [
            'name',
            'description',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)

#-----------------------------------------------------------------------------------------------------
# Tipos de publicación
#-----------------------------------------------------------------------------------------------------
class TypePostFilter(django_filters.FilterSet):
    name = django_filters.CharFilter()
    description = django_filters.CharFilter()

    class Meta:
        model = TypePost
        fields = [
            'name',
            'description',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)
        
#-----------------------------------------------------------------------------------------------------
# Reportes
#-----------------------------------------------------------------------------------------------------
class ReportFilter(django_filters.FilterSet):
    observation = django_filters.CharFilter()

    class Meta:
        model = Report
        fields = [
            'observation',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)
        
#-----------------------------------------------------------------------------------------------------
# Publicaciones
#-----------------------------------------------------------------------------------------------------
class PostFilter(django_filters.FilterSet):
    body = django_filters.CharFilter()
    user_id = django_filters.NumberFilter(field_name='user__id', lookup_expr='exact')

    class Meta:
        model = Post
        fields = [
            'body',
            'user_id',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)
        
#-----------------------------------------------------------------------------------------------------
# Comentarios
#-----------------------------------------------------------------------------------------------------
class CommentFilter(django_filters.FilterSet):
    body = django_filters.CharFilter()

    class Meta:
        model = Comment
        fields = [
            'body',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)
        
class ShareFilter(django_filters.FilterSet):
    user_id = django_filters.NumberFilter(field_name='user__id', lookup_expr='exact')

    class Meta:
        model = Share
        fields = [
            'user_id',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self) 