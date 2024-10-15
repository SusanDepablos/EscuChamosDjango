from django.db.models.signals import post_save , post_delete
from django.dispatch import receiver
from .models import *

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
            post_user_id = Post.objects.get(id=instance.post_id).user_id
            comment_user_id = Comment.objects.get(id=instance.post_id).user_id

            if post_user_id != instance.user_id and comment_user_id != instance.user_id:
                
                if instance.comment_id is None:
                    type = 'comment_post'
                    message = 'ha comentado tu publicación'
                    receiver_user_id = post_user_id
                else:
                    type = 'comment_reply'
                    message = 'ha respondido tu comentario'
                    receiver_user_id = comment_user_id

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


@receiver(post_save, sender=Comment)
def notification_comment_update(sender, instance, created, **kwargs):
    if not created:
        try:
            content_type_id = ContentType.objects.get(model='comment').id
            status_id = Status.objects.get(name='Bloqueado').id    
            
            if instance.status_id == status_id and not Notification.objects.filter(object_id=instance.id, content_type_id=content_type_id).exists():
                Notification.objects.create(
                    object_id=instance.id,
                    message='Tu comentario ha sido bloqueado',
                    type='blocked_comment',
                    content_type_id=content_type_id,
                    receiver_user_id=instance.user_id,
                )
            
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
            Type_post_id = TypePost.objects.get(name='Republicado').id
            repost_user_id = Post.objects.get(id=instance.post_id).user_id

            if repost_user_id != instance.user_id and instance.type_post_id == Type_post_id:
                
                if instance.post_id is not None:
                    type = 'repost'
                    message = 'ha reposteado tu publicación'
                    receiver_user_id = repost_user_id

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


@receiver(post_save, sender=Post)
def notification_post_update(sender, instance, created, **kwargs):
    if not created:
        try:
            content_type_id = ContentType.objects.get(model='post').id
            status_id = Status.objects.get(name='Bloqueado').id    
            
            if instance.status_id == status_id and not Notification.objects.filter(object_id=instance.id, content_type_id=content_type_id).exists():

                Notification.objects.create(
                    object_id=instance.id,
                    message='Tu publicación ha sido bloqueada',
                    type='blocked_post',
                    content_type_id=content_type_id,
                    receiver_user_id=instance.user_id,
                )
            
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