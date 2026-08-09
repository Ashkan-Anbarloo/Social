from django.db.models.signals import m2m_changed , post_delete , pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Post , User

@receiver(m2m_changed , sender=Post.likes.through)
def users_like_changed(sender , instance , **kwargs):
    instance.total_likes = instance.likes.count()
    instance.save()

@receiver(post_delete , sender=Post)
def send_email_on_post_delete(sender, instance, **kwargs):
    subject = 'A post was deleted'
    message = f'The post "{instance.description}" has been deleted.'

    send_mail(
        subject,
        message,
        'ashkanbyo@gmail.com',
        ['ashkanoqp@gmail.com'],  # , instance.author.email
        fail_silently=False,
    )

@receiver(pre_save, sender=User)
def set_default_user_data(sender, instance, **kwargs):
    if not instance.job:
        instance.job = "No Job Specified"
    
    if not instance.photo:
        instance.photo = "user_photo_data/images.jpg"