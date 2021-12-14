from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


from . import models
from . import forms

# Create your views here.

def sort_chrono(post):
    return post.timestamp.isoformat()

def parse_posts(request, postlist):
    postlist.sort(reverse=True, key=sort_chrono)
    json_posts = []
    for post in postlist:
        comments = models.PostComment.objects.filter(post=post)
        json_comments = []
        liked = False
        if (request.user.is_authenticated):
            liked = models.LikePost.objects.filter(post_id=post.id, liker_id=request.user.id).count() >= 1
        for comment in comments:
            json_comments += [{
                "author": comment.author.username,
                "author_image": comment.author.image.url,
                "comment": comment.comment,
                "timestamp": comment.timestamp.strftime("%m-%d-%Y %H:%M")
            }]
        
        json_posts += [{
            "id": post.id,
            "image": post.image.url,
            "author": post.author.username,
            "author_image": post.author.image.url,
            "caption": post.caption,
            "timestamp": post.timestamp.strftime("%m-%d-%Y %H:%M"),
            "comments": json_comments,
            "comment_form": forms.PostCommentForm(),
            "likes": models.LikePost.objects.filter(post=post).count(),
            "liked": liked,
            "like_form": forms.LikePostForm(),
        }]
    return json_posts

def view_global_snapshots(request):
    return render(request, 'index.html', context={
        "title": "Global Posts | Snapshot",
        "posts": parse_posts(request, list(models.SnapshotPost.objects.all()))
    })

def view_post(request):
    post_id = request.GET.get('post_id')
    return render(request, 'index.html', context={
        "title": "Post | Snapshot",
        "posts": parse_posts(request, [models.SnapshotPost.objects.get(id=post_id)])
    })

def view_user(request):
    username = request.GET.get('username')
    user = models.FancyUser.objects.get(username=username)
    is_following = False
    if (request.user.is_authenticated):
        requser = models.FancyUser.objects.get(username=request.user.username)
        is_following = models.FollowUser.objects.filter(followed_user=user, following_user=requser).count() == 1

    return render(request, 'user.html', context= {
        "title": username+" | Snapshot", 
        "user": user,
        "follow_user_form": forms.FollowUserForm(),
        "follower_count": models.FollowUser.objects.filter(followed_user=user).count(),
        "following_count": models.FollowUser.objects.filter(following_user=user).count(),
        "is_following": is_following,
        "posts": parse_posts(request, list(models.SnapshotPost.objects.filter(author=user)))
    })

def view_user_followers(request):
    username = request.GET.get('username')
    follower_list = models.FollowUser.objects.filter(followed_user=models.FancyUser.objects.get(username=username))
    users = []
    for followdata in follower_list:
        users.append({
            'username': followdata.following_user.username,
            'profile_icon': followdata.following_user.image.url,
            'timestamp': followdata.timestamp.strftime("%m-%d-%Y %H:%M"),
        })
    return render(request, 'listusers.html', {
        "title": username+"'s Followers | Snapshot", 
        'username': username,
        'type': 'followers',
        'userlist': users
    })

def view_user_following(request):
    username = request.GET.get('username')
    following_list = models.FollowUser.objects.filter(following_user=models.FancyUser.objects.get(username=username))
    users = []
    for followdata in following_list:
        users.append({
            'username': followdata.followed_user.username,
            'profile_icon': followdata.followed_user.image.url,
            'timestamp': followdata.timestamp.strftime("%m-%d-%Y %H:%M"),
        })
    return render(request, 'listusers.html', {
        "title": "Users "+username+"'s Following | Snapshot", 
        'username': username,
        'type': 'following',
        'userlist': users
    })

def view_post_likes(request):
    post = models.SnapshotPost.objects.get(id=request.GET.get('post_id'))
    likes = models.LikePost.objects.filter(post=post)
    users = []
    for likedata in likes:
        users.append({
            'username': likedata.liker.username,
            'profile_icon': likedata.liker.image.url,
            'timestamp': likedata.timestamp.strftime("%m-%d-%Y %H:%M"),
        })
    
    return render(request, 'listusers.html', {
        "title": "Likes | Snapshot", 
        'username': post.author.username,
        'type': 'likers',
        'userlist': users
    })

def view_follower_snapshots(request):
    if request.user.is_authenticated:
        postlist = []
        requser = models.FancyUser.objects.get(username=request.user)
        following_users = models.FollowUser.objects.filter(following_user=requser)
        for user in following_users:
            fuser = models.FancyUser.objects.get(username=user.followed_user.username)
            postlist += models.SnapshotPost.objects.filter(author=fuser)
        postlist.sort(key=sort_chrono)

        return render(request, 'index.html', context={
            "title": "My Feed | Snapshot",
            "posts": parse_posts(request, postlist)
            })
    else:
        return redirect("/global")

@login_required(login_url="/login")
def make_post(request):
    if request.method == 'POST':
        form = forms.PostSnapshotForm(request.POST, request.FILES)
        if form.is_valid() and request.user.is_authenticated:
            form.save(request)
            return redirect('/')
    else:
        form = forms.PostSnapshotForm()
    return render(request, 'post.html', context={
        "title": "Create Snapshot",
        "form": form
    })

@login_required(login_url="/login")
def make_comment(request):
    post_id = request.GET.get('post_id')
    if request.method == 'POST':
        form = forms.PostCommentForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            form.save(request, post_id)
    else:
        form = forms.PostCommentForm()
    return redirect('/')

@login_required(login_url="/login")
def follow_user(request):
    username = request.GET.get('username')
    user = models.FancyUser.objects.get(username=username)
    requser = models.FancyUser.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = forms.FollowUserForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            form.save(request, requser, user)
    else:
        form = forms.FollowUserForm()
    return redirect('/user?username=' + username)

@login_required(login_url="/login")
def like_post(request):
    post_id = request.GET.get('post_id')
    requser = models.FancyUser.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = forms.LikePostForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            form.save(request, post_id, requser)
    else:
        form = forms.LikePostForm()
    return redirect('/')

def logout_view(request):
    logout(request)
    return redirect('/')

def register_view(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            form.save(request)
            return redirect('/login/')
    else:
        form = forms.RegistrationForm()
    return render(request, 'registration/register.html', context={
        "title": "Create Snapshot Account",
        "form": form
    })