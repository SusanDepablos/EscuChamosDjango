from django.shortcuts import render
from .models import Post, Group, User  # Asegúrate de que este es el nombre correcto del modelo
from .serializer import PostSerializer  # Importa el serializador correcto
from datetime import datetime
from babel.dates import format_datetime

def index(request):
    return render(request, 'index.html')

def recoverAcount(request):
    return render(request, 'recover_account_email.html', {
            'username': 'valentina',
            'verification_code': 555555
        })

def posts(request):
    try:
        group = Group.objects.get(id=1)
        
        # Filtrar usuarios que pertenecen al grupo 1
        users_in_group = User.objects.filter(groups=group)
        
        # Filtrar posts de los usuarios que están en el grupo 1
        type_1_posts = Post.objects.filter(user__in=users_in_group, type_post_id=1).order_by('-created_at')
        type_2_posts = Post.objects.filter(user__in=users_in_group, type_post_id=2).order_by('-created_at')
        
        # Serializar los datos de los posts
        serializer_type_1 = PostSerializer(type_1_posts, many=True, context={'request': request})
        serializer_type_2 = PostSerializer(type_2_posts, many=True, context={'request': request})
        
        response_data_type_1 = serializer_type_1.data
        response_data_type_2 = serializer_type_2.data
        
        type_1_posts_list = []
        type_2_posts_list = []
        
        for post_data in response_data_type_1:
            post = {
                'photo_profile': post_data['relationships']['user']['profile_photo_url'] or 'https://via.placeholder.com/50',
                'user': post_data['relationships']['user']['name'],
                'username': post_data['relationships']['user']['username'],
                'created_at': format_datetime(datetime.strptime(post_data['attributes']['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z'), format='dd MMM yyyy', locale='es'),
                'body': post_data['attributes']['body']
            }
            type_1_posts_list.append(post)
        
        for post_data in response_data_type_2:
            post = {
                'photo_profile': post_data['relationships']['user']['profile_photo_url'] or 'https://via.placeholder.com/50',
                'user': post_data['relationships']['user']['name'],
                'username': post_data['relationships']['user']['username'],
                'created_at': format_datetime(datetime.strptime(post_data['attributes']['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z'), format='dd MMM yyyy', locale='es'),
                'url': post_data['relationships']['files'][0]['attributes']['url'] if post_data['relationships']['files'] else 'https://via.placeholder.com/150',
                'body': post_data['attributes']['body'],
                'is_video': post_data['relationships']['files'][0]['attributes']['url'].lower().endswith('.mp4') if post_data['relationships']['files'] else False
            }
            type_2_posts_list.append(post)
        
        return render(request, 'posts/posts.html', {
            'type_1_posts': type_1_posts_list,
            'type_2_posts': type_2_posts_list
        })

    except Exception as e:
        print(f"Error al recuperar datos: {e}")
        return render(request, 'posts/posts.html', {
            'type_1_posts': [],
            'type_2_posts': []
        })
        
def error(request, exception=None):
    return render(request, 'error.html', status=404)