from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import *

#-----------------------------------------------------------------------------------------------------
# Reaction
#----------------------------------------------------------------------------------------------------- 

@receiver(post_save, sender=Reaction)
def notification_reaction(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get(id=instance.content_type_id)
        model_name = content_type.model
        content_type_id = ContentType.objects.get(model='reaction').id

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

            if post_user_id != instance.user_id & comment_user_id != instance.user_id:
                
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
