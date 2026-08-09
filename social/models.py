from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from django_resized import ResizedImageField
# Create your models here.

class User(AbstractUser):
    date_of_birth = models.DateField(blank=True , null=True)
    bio = models.TextField(blank=True , null=True)
    photo = models.ImageField(upload_to='account_image/',blank=True , null=True)
    job = models.CharField(max_length=250 , blank=True , null=True)
    phone = models.CharField(max_length=11 , blank=True , null=True)
    following = models.ManyToManyField('self' , through='Contact' , related_name='followers' , symmetrical=False)

    def get_absolute_url(self):
        return reverse("social:user_detail", args=[self.username])

class Post(models.Model):
    author = models.ForeignKey(User , on_delete=models.CASCADE , related_name='user_posts')
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager()
    likes = models.ManyToManyField(User , related_name='liked_posts' , blank=True)
    saved_by = models.ManyToManyField(User , related_name='saved_posts')
    total_likes = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)


    class Meta:
        ordering = ['-created',]
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['-total_likes'])
        ]

    def __str__(self):
        return f"{self.author.username}  |  {self.description[:10]}..."
    
    def get_absolute_url(self):
        return reverse("social:post_detail", args=[self.id])
    

class Comment(models.Model):
    post = models.ForeignKey(Post , on_delete=models.CASCADE , related_name='comments')
    name = models.CharField(max_length=250)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created',]
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"Comment by {self.name} on {self.post.description[:10]}"
    


class Image(models.Model):
    post = models.ForeignKey(Post , on_delete=models.CASCADE , related_name='images')
    # image_file = models.ImageField(upload_to='post_images/')
    image = models.ImageField(upload_to='post_images_tag/')
    created = models.DateTimeField(auto_now_add=True)    

    class Meta:
        ordering = ['-created',]
        indexes = [
            models.Index(fields=['-created']),
        ]


class Contact(models.Model):
    user_from = models.ForeignKey(User , related_name='rel_from_set' , on_delete=models.CASCADE)
    user_to = models.ForeignKey(User , related_name='rel_to_set' , on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created'])
        ]
        ordering = ['-created',]
    
    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'



class Ticket(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject