from django.shortcuts import render , get_object_or_404 , redirect
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponse , JsonResponse
from .forms import UserRegisterForm , UserEditForm , TicketForm , PostForm , SearchForm , CommentForm , EmailPostForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Post , Image , User , Contact , Ticket
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Greatest
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator , EmptyPage , PageNotAnInteger
from django.contrib import messages
# Create your views here.

def profile(request):
    if not request.user.is_authenticated:
        return redirect('social:login')
    user = request.user
    saved_posts = user.saved_posts.all()
    return render(request , 'social/home.html' , {'saved_posts':saved_posts})


def log_out(request):
    logout(request)
    return HttpResponse('you are loggedOut')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return render(request , 'registration/register_done.html' , {'user':user})
    else:
        form = UserRegisterForm()
    return render(request , 'registration/register.html' , {'form':form})

@login_required
def edit_user(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST , instance=request.user , files=request.FILES)
        # account_form = AccountEditForm(request.POST , instance=request.user.account , files=request.FILES)
        if user_form.is_valid():
            user_form.save()
            return redirect('social:profile')
    else:
        user_form = UserEditForm(instance=request.user)
        # account_form = AccountEditForm(instance=request.user.account)
    context = {
        # 'account_form' : account_form,
        'user_form' : user_form,
    }
    return render(request , 'registration/edit_user.html' , context)



def ticket(request):
    # sent = False
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            Ticket.objects.create(
                name = cd['name'],
                email = cd['email'],
                phone = cd['phone'],
                subject = cd['subject'],
                message = cd['message'],
            )


            message = f'{cd['name']}\n{cd['email']}\n{cd['phone']}\n{cd['message']}'
            send_mail(cd['subject'], message , 'ashkanbyo@gmil.com' , ['ashkanoqp@gmail.com'] , fail_silently=False)
            # sent = True
            messages.success(request , 'ایمیل شما ارسال شد .')
            return redirect('social:chat')
    else:
        form = TicketForm()
    return render(request , 'forms/ticket.html' , {'form':form}) # , 'sent':sent


def chat(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'forms/chat.html', {'tickets': tickets})



def post_list(request , tag_slug=None):
    tag = None
    if tag_slug :
        tag = get_object_or_404(Tag , slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])
    else :
        posts = Post.objects.all().order_by('-total_likes')

    page = request.GET.get('page')
    paginator = Paginator(posts , 2)
    # page_number = request.GET.get('page' , 1)
    try:
        posts = paginator.page(page)
    except EmptyPage:
        # posts = paginator.page(paginator.num_pages)
        posts = []
    except PageNotAnInteger:
        posts = paginator.page(1)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request , 'social/list_ejax.html' , {'posts' : posts})
    
    context = {
        'posts' : posts,
        'tag' : tag,
    }
    return render(request , 'social/list.html' , context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST , request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            Image.objects.create(image=form.cleaned_data['image'] , post=post)
            return redirect('social:profile')
    else:
        form = PostForm()
    
    context = {
        'form' : form,
    }
    return render(request , 'forms/create_post.html' , context)


@login_required
def post_detail(request , id):
    post = get_object_or_404(Post , id=id)

    post_tags_ids = post.tags.values_list('id',flat=True)
    similar_post = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_post = similar_post.annotate(same_tags=Count('tags')).order_by('-same_tags','-created')[:2]

    if request.method == 'POST' :
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            # return redirect('social:post_detail' , id=post.id)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'name': comment.name,
                    'created': comment.created.strftime('%b %d, %Y, %I:%M %p'),
                    'body': comment.body,
                    'count': post.comments.count()
                })
            return redirect('social:post_detail' , id=post.id)
    else:
        form = CommentForm()

    context = {
        'post' : post,
        'similar_post':similar_post,
        'form' : form,
    }
    return render(request , 'social/detail.html' , context)



def post_search(request):
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            results = Post.objects.annotate(
                similarity=TrigramSimilarity('description', query) + TrigramSimilarity('tags__name' , query)
            ).filter(similarity__gt=0.1).order_by('-similarity').distinct()

    context = {
        'results': results,
        'query': query,
    }
    return render(request, 'social/search.html', context)


@require_POST
def post_comment(request , id):
    post = get_object_or_404(Post , id=id)
    comment = None
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
    else : 
        form = CommentForm()
    
    context = {
        'post' : post,
        'form' : form,
        'comment' : comment,
    }
    # return render(request , 'forms/comment.html' , context)
    return render(request , 'social/detail.html' , context)



@login_required
def panel_admin(request):
    user = request.user
    posts = Post.objects.filter(author = user)

    context = {
        'posts':posts,
    }
    return render(request , 'social/panel_admin.html' , context)

@login_required
def delete_post(request , post_id):
    post = get_object_or_404(Post , id=post_id)
    if request.method =='POST':
        post.delete()
        return redirect('social:panel_admin')
    return render(request , 'forms/delete_post.html' , {'post':post})


@login_required
def edit_post(request , post_id):
    post = get_object_or_404(Post , id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST , request.FILES , instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            Image.objects.create(image=form.cleaned_data['image'] , post=post)
            return redirect('social:panel_admin')
    else:
        form = PostForm(instance=post)
    
    context = {
        'form' : form,
        'post':post,
    }
    return render(request , 'forms/create_post.html' , context)


@login_required
def delete_image(request , image_id):
    image = get_object_or_404(Image , id=image_id)
    post_id = image.post_id
    image.delete()
    return redirect('social:edit_post',post_id)


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post , id=post_id)
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        post_likes_count = post.likes.count()
        response_data = {
            'liked':liked,
            'liked_count':post_likes_count,
        }
    else:
        response_data = {'error':'Invalid post_id'}
    return JsonResponse(response_data)


@login_required
@require_POST
def save_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post , id=post_id)
        user = request.user

        if user in post.saved_by.all():
            post.saved_by.remove(user)
            saved = False
        else:
            post.saved_by.add(user)
            saved = True
        return JsonResponse({'saved':saved})
    return JsonResponse({'error':'Invalid request'})

@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request , 'user/user_list.html' , {'users':users})

@login_required
def user_detail(request , username):
    user = get_object_or_404(User , username=username , is_active=True)
    return render(request , 'user/user_detail.html' , {'user':user})


@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('id')
    if user_id :
        try:
            user = User.objects.get(id = user_id)
            if request.user in user.followers.all():
                Contact.objects.filter(user_from=request.user , user_to=user).delete()
                follow = False
            else:
                Contact.objects.get_or_create(user_from=request.user , user_to=user)
                follow = True
            following_count = user.following.count()
            followers_count = user.followers.count()
            return JsonResponse({'follow':follow , 'following_count':following_count , 'followers_count':followers_count})
        except Exception as e:
            return JsonResponse({'error':str(e)} , status=500)
    return JsonResponse({'error':'Invalid request'})

def user_followers(request, user_id):
    user = get_object_or_404(User, id=user_id)
    followers = user.followers.all()
    context = {
        'user': user, 
        'users_list': followers, 
        'status': 'Followers',
    }
    return render(request, 'user/user_list_followers.html', context)

def user_following(request, user_id):
    user = get_object_or_404(User, id=user_id)
    following = user.following.all()
    context = {
        'user': user, 
        'users_list': following, 
        'status': 'Following',
    }
    return render(request, 'user/user_list_followers.html', context)


@login_required
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            
            # subject = f"{cd['name']} پیشنهاد می‌کند این پست را بخوانید: {post.title}"
            subject = f'{request.user.username} recommends this post.'
            # message = f"پست '{post.title}' را در لینک زیر ببین:\n\n{post_url}\n\nتوضیحات پست:\n{post.description}\n\nپیام فرستنده: {cd['comments']}"
            message = f'Post description {post.description} \n\n View the post using this link \n\n {post_url}'
            # ارسال ایمیل
            send_mail(subject, message, 'ashkanbyo@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    
    return render(request, 'social/post_share.html', {'post': post, 'form': form, 'sent': sent})





