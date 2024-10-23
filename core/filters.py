import django_filters
from .models import *
from django.db.models import Q, Count

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
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = User
        fields = [
            'search',
            'username', 
            'name', 
            'biography',
            'email', 
            'phone_number',
            'birthdate',
        ]
        
    def filter_search(self, queryset, name, value):
        # Filtrar por username y name usando icontains
        return queryset.filter(
            Q(username__icontains=value) | Q(name__icontains=value)
        )

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
    iso = django_filters.CharFilter()

    class Meta:
        model = Country
        fields = [
            'name',
            'abbreviation',
            'dialing_code',
            'iso',
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
# Reacciones
#-----------------------------------------------------------------------------------------------------      
class ReactionFilter(django_filters.FilterSet):
    model = django_filters.CharFilter(method='filter_by_model')
    object_id = django_filters.NumberFilter(field_name='object_id', lookup_expr='exact')

    class Meta:
        model = Reaction
        fields = [
            'model', 
            'object_id'
            ]

    def filter_by_model(self, queryset, name, value):
        try:
            content_type = ContentType.objects.get(model=value.lower())
            return queryset.filter(content_type=content_type)
        except ContentType.DoesNotExist:
            return queryset.none

#-----------------------------------------------------------------------------------------------------
# Reportes
#-----------------------------------------------------------------------------------------------------
class ReportFilter(django_filters.FilterSet):
    observation = django_filters.CharFilter()
    model = django_filters.CharFilter(method='filter_by_model')
    object_id = django_filters.NumberFilter(field_name='object_id', lookup_expr='exact')

    class Meta:
        model = Report
        fields = [
            'observation', 
            'model', 
            'object_id'
            ]


    def filter_by_model(self, queryset, name, value):
        try:
            content_type = ContentType.objects.get(model=value.lower())
            return queryset.filter(content_type=content_type)
        except ContentType.DoesNotExist:
            return queryset.none()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)
        
class ReportGroupedFilter(django_filters.FilterSet):
    object_type = django_filters.CharFilter(method='filter_by_object_type')

    class Meta:
        model = Report
        fields = ['object_type']

    def filter_by_object_type(self, queryset, name, value):
        if value:
            if value == 'post':
                # Excluye los posts que tienen un post_id asociado (reposts)
                return queryset.filter(
                    content_type__model='post',
                    object_id__in=Post.objects.filter(post__isnull=True).values_list('id', flat=True)
                )
            elif value == 'comment':
                return queryset.filter(content_type__model='comment')
            elif value == 'repost':
                # Solo incluir los reposts que tienen un post_id asociado
                return queryset.filter(content_type__model='post').exclude(object_id__in=Post.objects.filter(post__isnull=True).values_list('id', flat=True))
        return queryset
        
#-----------------------------------------------------------------------------------------------------
# Publicaciones
#-----------------------------------------------------------------------------------------------------
class PostFilter(django_filters.FilterSet):
    body = django_filters.CharFilter()
    user_id = django_filters.NumberFilter(field_name='user__id', lookup_expr='exact')
    status_id = django_filters.NumberFilter(field_name='status__id', lookup_expr='exact')
    type_post_id = django_filters.NumberFilter(field_name='type_post__id', lookup_expr='exact')

    class Meta:
        model = Post
        fields = [
            'body',
            'user_id',
            'status_id',
            'type_post_id'  # Añadido para permitir filtrar por type_post_id
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)

#-----------------------------------------------------------------------------------------------------
# Comentarios
#-----------------------------------------------------------------------------------------------------
class CommentFilter(django_filters.FilterSet):
    body = django_filters.CharFilter()
    post_id = django_filters.NumberFilter(field_name='post__id', lookup_expr='exact')
    comment_id = django_filters.NumberFilter(field_name='comment__id', lookup_expr='exact')
    status_id = django_filters.NumberFilter(field_name='status__id', lookup_expr='exact')

    class Meta:
        model = Comment
        fields = [
            'body',
            'post_id',
            'comment_id',
            'status_id'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)
        
        if 'comment_id' not in self.data or not self.data.get('comment_id'):
            self.queryset = self.queryset.filter(comment__isnull=True)
        
#-----------------------------------------------------------------------------------------------------
# Compartidos
#-----------------------------------------------------------------------------------------------------
        
class ShareFilter(django_filters.FilterSet):
    user_id = django_filters.NumberFilter(field_name='user__id', lookup_expr='exact')

    class Meta:
        model = Share
        fields = ['user_id']

        
#-----------------------------------------------------------------------------------------------------
# Seguimientos
#-----------------------------------------------------------------------------------------------------
class FollowFilter(django_filters.FilterSet):
    followed_user_id = django_filters.NumberFilter(field_name='followed_user__id', lookup_expr='exact')
    following_user_id = django_filters.NumberFilter(field_name='following_user__id', lookup_expr='exact')
    search_followed = django_filters.CharFilter(method='filter_followed_user')
    search_following = django_filters.CharFilter(method='filter_following_user')

    class Meta:
        model = Follow
        fields = [
            'followed_user_id', 
            'following_user_id',
            'search_followed',
            'search_following',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)

    def filter_followed_user(self, queryset, name, value):
        return queryset.filter(
            Q(followed_user__username__icontains=value) | Q(followed_user__name__icontains=value)
        )

    def filter_following_user(self, queryset, name, value):
        return queryset.filter(
            Q(following_user__username__icontains=value) | Q(following_user__name__icontains=value)
        )
        
class StoryFilter(django_filters.FilterSet):
    user_id = django_filters.NumberFilter(field_name='user__id', lookup_expr='exact')
    status_id = django_filters.NumberFilter(field_name='status__id', lookup_expr='exact')

    class Meta:
        model = Story
        fields = [
            'user_id',
            'status_id'
            ]
        
#-----------------------------------------------------------------------------------------------------
# Seguimientos
#-----------------------------------------------------------------------------------------------------

class NotificationFilter(django_filters.FilterSet):
    receiver_user_id = django_filters.CharFilter(method='filter_receiver_user')

    class Meta:
        model = Notification
        fields = [
            'receiver_user_id',
            'type',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_icontains_filter(self)

    def filter_receiver_user(self, queryset, name, value):
        if value.lower() == 'null':
            return queryset.filter(receiver_user__isnull=True)
        return queryset.filter(receiver_user=value)