from django.db.models.signals import post_save , post_delete
from django.dispatch import receiver
from django.db.models import Q
from .models import *
clients = {}

#-----------------------------------------------------------------------------------------------------
# Funciones para eliminar al bloquear
#----------------------------------------------------------------------------------------------------- 

def delete_related_notifications_post(instance, content_type_id):

    Notification.objects.filter(
        object_id__in=Reaction.objects.filter(
            content_type_id=content_type_id,
            object_id=instance.id
        ).values_list('id', flat=True),
        content_type_id=ContentType.objects.get(model='reaction').id,
        type='reaction_post',
    ).delete()

    Notification.objects.filter(
        object_id__in=Comment.objects.filter(
            post_id=instance.id,
            comment_id__isnull=True
        ).values_list('id', flat=True),
        content_type_id=ContentType.objects.get(model='comment').id,
        type='comment_post',
    ).delete()

    Notification.objects.filter(
        object_id__in=Post.objects.filter(
            post_id=instance.id,
        ).values_list('id', flat=True),
        content_type_id=ContentType.objects.get(model='post').id,
        type='repost',
    ).delete()


def delete_related_notifications_comment(content_type_id, instance_id):

    Notification.objects.filter(
        object_id__in=Reaction.objects.filter(
            content_type_id=content_type_id,
            object_id=instance_id
        ).values_list('id', flat=True),
        content_type_id=ContentType.objects.get(model='reaction').id,
        type='reaction_comment',
    ).delete()

    Notification.objects.filter(
        object_id__in=Comment.objects.filter(
            comment_id=instance_id,
        ).values_list('id', flat=True),
        content_type_id=ContentType.objects.get(model='comment').id,
        type='comment_reply',
    ).delete()

#-----------------------------------------------------------------------------------------------------
# Share
#----------------------------------------------------------------------------------------------------- 

@receiver(post_delete, sender=Share)
def notification_delete_share(sender, instance, **kwargs):
    content_type_id = ContentType.objects.get(model='share').id

    try:
        Notification.objects.filter(
            content_type_id=content_type_id,
            object_id=instance.post_id
        ).delete()
    except Exception as e:
        print(f"Error al eliminar la notificación: {e}")

#-----------------------------------------------------------------------------------------------------
# Reaction
#----------------------------------------------------------------------------------------------------- 

@receiver(post_save, sender=Reaction)
def notification_reaction(sender, instance, created, **kwargs):
    if created:
        content_type_id = ContentType.objects.get(model='reaction').id
        content_type = ContentType.objects.get(id=instance.content_type_id)
        model_name = content_type.model

        try:
            if model_name == 'comment':
                comment = Comment.objects.get(id=instance.object_id)

                if comment.user_id != instance.user_id:
                    Notification.objects.create(
                        object_id=instance.id,
                        message='reacciono a tu comentario',
                        type='reaction_comment',
                        content_type_id=content_type_id,
                        receiver_user_id=comment.user_id,
                        user_id=instance.user_id,
                    )

            elif model_name == 'post':
                post = Post.objects.get(id=instance.object_id)

                if post.user_id != instance.user_id:
                    Notification.objects.create(
                        object_id=instance.id,
                        message='reacciono a tu publicacion',
                        type='reaction_post',
                        content_type_id=content_type_id,
                        receiver_user_id=post.user_id,
                        user_id=instance.user_id,
                    )

            elif model_name == 'story':
                story = Story.objects.get(id=instance.object_id)

                if story.user_id != instance.user_id:
                    Notification.objects.create(
                        object_id=instance.id,
                        message='reacciono a tu historia',
                        type='reaction_story',
                        content_type_id=content_type_id,
                        receiver_user_id=story.user_id,
                        user_id=instance.user_id,
                    )

        except Exception as e:
            print(f"Error al crear la notificación: {e}")


@receiver(post_delete, sender=Reaction)
def notification_delete_reaction(sender, instance, **kwargs):
    content_type_id = ContentType.objects.get(model='reaction').id

    try:
        Notification.objects.filter(
            content_type_id=content_type_id,
            object_id=instance.id
        ).delete()
    except Exception as e:
        print(f"Error al eliminar la notificación: {e}")

#-----------------------------------------------------------------------------------------------------
# Follow
#----------------------------------------------------------------------------------------------------- 

@receiver(post_save, sender=Follow)
def notification_follow(sender, instance, created, **kwargs):
    if created:
        try:
            content_type_id = ContentType.objects.get(model='follow').id

            Notification.objects.create(
                object_id=instance.id,
                message="ha comenzado a seguirte",
                type='follower',
                content_type_id=content_type_id,
                receiver_user_id=instance.followed_user_id,
                user_id=instance.following_user_id,
            )
        except Exception as e:
            print(f"Error al crear la notificación: {e}")


@receiver(post_delete, sender=Follow)
def notification_unfollow(sender, instance, **kwargs):
    try:
        content_type_id = ContentType.objects.get(model='follow').id

        Notification.objects.filter(
            content_type_id=content_type_id,
            object_id=instance.id
        ).delete()
    except Exception as e:
        print(f"Error al eliminar la notificación: {e}")

#-----------------------------------------------------------------------------------------------------
# comment
#----------------------------------------------------------------------------------------------------- 

@receiver(post_save, sender=Comment)
def notification_comment(sender, instance, created, **kwargs):
    if created:
        try:
            content_type_id = ContentType.objects.get(model='comment').id
            post = Post.objects.get(id=instance.post_id)
            post_user_id = post.user_id  # El autor de la publicación

            # Obtener el autor del comentario original si es una respuesta
            if instance.comment_id:
                original_comment = Comment.objects.get(id=instance.comment_id)
                comment_user_id = original_comment.user_id  # El autor del comentario original
            else:
                comment_user_id = None

            # Si es un comentario a la publicación, notificar al autor de la publicación
            if post_user_id != instance.user_id and instance.comment_id is None:
                Notification.objects.create(
                    object_id=instance.id,
                    message='ha comentado tu publicación',
                    type='comment_post',
                    content_type_id=content_type_id,
                    receiver_user_id=post_user_id,
                    user_id=instance.user_id,
                )

            # Si es una respuesta, notificar al autor del comentario original
            if instance.comment_id and comment_user_id and comment_user_id != instance.user_id:
                Notification.objects.create(
                    object_id=instance.id,
                    message='ha respondido tu comentario',
                    type='comment_reply',
                    content_type_id=content_type_id,
                    receiver_user_id=comment_user_id,
                    user_id=instance.user_id,
                )

        except Exception as e:
            print(f"Error al crear la notificación: {e}")

@receiver(post_save, sender=Comment)
def notification_comment_update(sender, instance, created, **kwargs):
    if not created:
        try:
            content_type_id = ContentType.objects.get(model='comment').id
            blocked_id = Status.objects.get(name='Bloqueado').id
            report_id = Status.objects.get(name='Reportado').id
            resolved_id = Status.objects.get(name='Resuelto').id

            if instance.status_id == report_id and not Notification.objects.filter(
                object_id=instance.id, content_type_id=content_type_id, type__in=['report_comment', 'blocked_comment'] #prefuntarle a susan
                        ).exists():
                Notification.objects.create(
                    object_id=instance.id,
                    message='Reporte de comentario',
                    type='report_comment',
                    content_type_id=content_type_id,
                )

            elif instance.status_id == blocked_id and not Notification.objects.filter(
                object_id=instance.id, content_type_id=content_type_id, type='blocked_comment'
            ).exists():
                Notification.objects.create(
                    object_id=instance.id,
                    message='Tu comentario ha sido bloqueado',
                    type='blocked_comment',
                    content_type_id=content_type_id,
                    receiver_user_id=instance.user_id,
                )

                Notification.objects.filter(
                    content_type_id=content_type_id,
                    object_id=instance.id,
                    type='report_comment'
                ).delete()

                delete_related_notifications_comment(content_type_id, instance.id)

            elif instance.status_id == resolved_id:
                
                Notification.objects.filter(
                    content_type_id=content_type_id,
                    object_id=instance.id,
                    type='report_comment'
                ).delete()

        except Exception as e:
            print(f"Error al manejar la actualización: {e}")

@receiver(post_delete, sender=Comment)
def notification_comment_delete(sender, instance, **kwargs):
    try:
        content_type_id = ContentType.objects.get(model='comment').id

        Notification.objects.filter(
            content_type_id=content_type_id,
            object_id=instance.id
        ).delete()

    except Exception as e:
        print(f"Error al eliminar la notificación: {e}")

#-----------------------------------------------------------------------------------------------------
# post
#----------------------------------------------------------------------------------------------------- 

@receiver(post_save, sender=Post)
def notification_post(sender, instance, created, **kwargs):
    if created:
        try:
            content_type_id = ContentType.objects.get(model='post').id

            if instance.type_post_id == TypePost.objects.get(name='Republicado').id:
                repost_user_id = Post.objects.get(id=instance.post_id).user_id
                    
                if instance.post_id is not None and repost_user_id != instance.user_id:

                    Notification.objects.create(
                        object_id=instance.id,
                        message='ha reposteado tu publicación',
                        type='repost',
                        content_type_id=content_type_id,
                        receiver_user_id=repost_user_id,
                        user_id=instance.user_id,
                    )
            elif instance.type_post_id == TypePost.objects.get(name='Escuchamos').id:

                    Notification.objects.create(
                        object_id=instance.id,
                        message='ha subido una nueva publicacion',
                        type='notification_escuchamos',
                        content_type_id=content_type_id,
                        user_id=instance.user_id,
                    )

        except Exception as e:
            print(f"Error al crear la notificación: {e}")


@receiver(post_save, sender=Post)
def notification_post_update(sender, instance, created, **kwargs):
    if not created:
        try:
            content_type_id = ContentType.objects.get(model='post').id
            blocked_id = Status.objects.get(name='Bloqueado').id
            report_id = Status.objects.get(name='Reportado').id
            resolved_id = Status.objects.get(name='Resuelto').id

            if instance.status_id == report_id and not Notification.objects.filter(
                object_id=instance.id, content_type_id=content_type_id, type__in=['report_post', 'blocked_post']).exists():
                Notification.objects.create(
                    object_id=instance.id,
                    message='Reporte de publicación',
                    type='report_post',
                    content_type_id=content_type_id,
                )

            elif instance.status_id == blocked_id and not Notification.objects.filter(
                object_id=instance.id, content_type_id=content_type_id, type='blocked_post'
            ).exists():
                reaction_content_type_id = ContentType.objects.get(model='reaction').id
                Notification.objects.create(
                    object_id=instance.id,
                    message='Tu publicación ha sido bloqueada',
                    type='blocked_post',
                    content_type_id=content_type_id,
                    receiver_user_id=instance.user_id,
                )

                Notification.objects.filter(
                    content_type_id=content_type_id,
                    object_id=instance.id,
                    type='report_post'
                ).delete()

                delete_related_notifications_post(instance, content_type_id)

            elif instance.status_id == resolved_id:
                
                Notification.objects.filter(
                    content_type_id=content_type_id,
                    object_id=instance.id,
                    type='report_post'
                ).delete()

        except Exception as e:
            print(f"Error al manejar la actualización: {e}")



@receiver(post_delete, sender=Post)
def notification_post_delete(sender, instance, **kwargs):
    try:
        content_type_id = ContentType.objects.get(model='post').id

        Notification.objects.filter(
            content_type_id=content_type_id,
            object_id=instance.id
        ).delete()

    except Exception as e:
        print(f"Error al eliminar la notificación: {e}")

#-----------------------------------------------------------------------------------------------------
# share
#----------------------------------------------------------------------------------------------------- 

@receiver(post_save, sender=Share)
def notification_share(sender, instance, created, **kwargs):
    if created:
        try:
            content_type_id = ContentType.objects.get(model='share').id
            post = Post.objects.get(id=instance.post_id)

            if post.user_id != instance.user_id:
                
                type = 'share'
                message = 'ha compartido tu publicación'
                receiver_user_id = post.user_id

                Notification.objects.create(
                    object_id=instance.id,
                    message=message,
                    type=type,
                    content_type_id=content_type_id,
                    receiver_user_id=receiver_user_id,
                    user_id=instance.user_id,
                )

        except Exception as e:
            print(f"Error al crear la notificación: {e}")


@receiver(post_delete, sender=Share)
def notification_share_delete(sender, instance, **kwargs):
    try:
        content_type_id = ContentType.objects.get(model='share').id

        Notification.objects.filter(
            content_type_id=content_type_id,
            object_id=instance.id
        ).delete()

    except Exception as e:
        print(f"Error al eliminar la notificación: {e}")

#-----------------------------------------------------------------------------------------------------
# Report
#----------------------------------------------------------------------------------------------------- 

@receiver(post_delete, sender=Report)
def notification_delete(sender, instance, **kwargs):
    try:
        resuelt_id = Status.objects.get(name='Resuelto').id
        blocked_id = Status.objects.get(name='Bloqueado').id
        content_type = ContentType.objects.get(id=instance.content_type_id)
        model_name = content_type.model

        if model_name == 'comment':
            comment = Comment.objects.get(id=instance.object_id)

            if comment.status_id == resuelt_id:
                type  = 'resolved_comment'
                message = 'Tu reporte ha sido recibido, pero el comentario no será eliminada tras su revisión'

            elif comment.status_id == blocked_id:
                type  = 'blocked_comment_report'
                message = 'Tu reporte ha sido recibido, el comentario ha sido bloqueado'

        elif model_name == 'post':
            post = Post.objects.get(id=instance.object_id)

            if post.status_id == blocked_id:
                type = 'blocked_post'
                message = 'Tu reporte ha sido recibido, la publicación ha sido bloqueada'
            elif post.status_id == resuelt_id:
                type = 'resolved_post'
                message = 'Tu reporte ha sido recibido, pero la publicación no será eliminada tras su revisión'

        notification_exists = Notification.objects.filter(
            Q(object_id=instance.object_id) &
            Q(message=message) &
            Q(type=type) &
            Q(content_type_id=instance.content_type_id) &
            Q(receiver_user_id=instance.user_id)
        ).exists()

        if not notification_exists:
            Notification.objects.create(
                object_id=instance.object_id,
                message=message,
                type=type,
                content_type_id=instance.content_type_id,
                receiver_user_id=instance.user_id,
            )

    except Exception as e:
        print(f"Error al eliminar la notificación: {e}")

#-----------------------------------------------------------------------------------------------------
# Notificaciones
#----------------------------------------------------------------------------------------------------- 

@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    user_id = instance.receiver_user.id
    if created:
        send_notification(user_id)
    else:
        if instance.is_read:
            send_notification(user_id)

def send_notification(user_id):
    if user_id in clients:
        unread_count = Notification.objects.filter(receiver_user_id=user_id, is_seen=False).count()
        for client in clients[user_id]:
            client.send(f"data: {{ 'notifications': {unread_count} }}\n\n")
