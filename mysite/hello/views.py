from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from html_sanitizer import Sanitizer


from . import models
from . import forms

# Create your views here.
sanitizer = Sanitizer({
    'tags': {"meta"},
    'attributes': {
        "meta": {
            "property",
            "name",
            "content",
        }
    },
    'empty': {},
    'separate': {}

})

def sort_chrono(post):
    return post.timestamp.isoformat()

def generate_generic_unfurl():
    # Cursed
    return """
    <meta property="og:type" content="website" />\n
    <meta property="og:title" content="Snapshot" />\n
    <meta property="og:description" content="Check out what's going on in the community!" />\n
    <meta property="og:image" content="https://snapshot.hugeblank.me/media/favicon.png" />\n

    <meta name="twitter:card" content="app" />\n
    <meta name="twitter:domain" content="snapshot.hugeblank.me" />\n
    <meta name="twitter:title" content="Snapshot" />\n
    <meta name="twitter:description" content="Check out what's going on in the community!" />\n
    <meta name="twitter:image" content="https://snapshot.hugeblank.me/media/favicon.png" />\n
    <meta name="twitter:url" content="https://snapshot.hugeblank.me/" />\n
    """

def generate_post_unfurl(post):
    caption = sanitizer.sanitize(post['caption'])
    # Cursed
    return """
    <meta property="og:type" content="website" />\n
    <meta property="og:title" content="%s's Post | Snapshot" />\n
    <meta property="og:description" content="%s" />\n
    <meta property="og:image" content="%s" />\n

    <meta name="twitter:card" content="summary_large_image" />\n
    <meta name="twitter:domain" content="snapshot.hugeblank.me" />\n
    <meta name="twitter:site" content="@hugeblank">
    <meta name="twitter:title" content="%s's Post | Snapshot" />\n
    <meta name="twitter:description" content="%s" />\n
    <meta name="twitter:image" content="https://snapshot.hugeblank.me%s" />\n
    <meta name="twitter:url" content="https://snapshot.hugeblank.me/post%s" />\n
    <meta name="twitter:label1" content="%s Likes" />\n
    <meta name="twitter:label2" content="%s" />\n
    """%(post['author'], caption, post['image'], post['author'], caption, post['image'], post['id'], post['likes'], post['timestamp'])

def get_context(request, title):
    if request.user.is_authenticated:
        return {
            "profile_icon": models.FancyUser.objects.get(username=request.user.username).image.url,
            "title": title,
            "meta": generate_generic_unfurl(),
        }
    else:
        return {
            "title": title,
            "meta": generate_generic_unfurl(),
        }

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
                "id": comment.id,
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
    context = get_context(request, "Global Posts | Snapshot") | {"posts": parse_posts(request, list(models.SnapshotPost.objects.all()))}
    return render(request, 'index.html', context)

def view_post(request, post_id):
    post = parse_posts(request, [models.SnapshotPost.objects.get(id=post_id)])
    context = get_context(request, "Post | Snapshot")  | {
        "posts": post,
        "meta": generate_post_unfurl(post[0])
    }
    return render(request, 'index.html', context)

def view_user(request, username):
    user = models.FancyUser.objects.get(username=username)
    is_following = False
    if (request.user.is_authenticated):
        requser = models.FancyUser.objects.get(username=request.user.username)
        is_following = models.FollowUser.objects.filter(followed_user=user, following_user=requser).count() == 1

    context = get_context(request, username+" | Snapshot")
    context = context | {
        "user": user,
        "follow_user_form": forms.FollowUserForm(),
        "follower_count": models.FollowUser.objects.filter(followed_user=user).count(),
        "following_count": models.FollowUser.objects.filter(following_user=user).count(),
        "is_following": is_following,
        "posts": parse_posts(request, list(models.SnapshotPost.objects.filter(author=user)))
    }
    return render(request, 'user.html', context)

def view_user_followers(request, username):
    follower_list = models.FollowUser.objects.filter(followed_user=models.FancyUser.objects.get(username=username))
    users = []
    for followdata in follower_list:
        users.append({
            'username': followdata.following_user.username,
            'profile_icon': followdata.following_user.image.url,
            'timestamp': followdata.timestamp.strftime("%m-%d-%Y %H:%M"),
        })
    context = get_context(request, username+"'s Followers | Snapshot")
    context = context | {
        'username': username,
        'type': 'followers',
        'userlist': users
    }
    return render(request, 'listusers.html', context)

def view_user_following(request, username):
    following_list = models.FollowUser.objects.filter(following_user=models.FancyUser.objects.get(username=username))
    users = []
    for followdata in following_list:
        users.append({
            'username': followdata.followed_user.username,
            'profile_icon': followdata.followed_user.image.url,
            'timestamp': followdata.timestamp.strftime("%m-%d-%Y %H:%M"),
        })
    context = get_context(request, "Users "+username+"'s Following | Snapshot")
    context = context | {
        'username': username,
        'type': 'following',
        'userlist': users
    }
    return render(request, 'listusers.html', context)

def view_post_likes(request, post_id):
    post = models.SnapshotPost.objects.get(id=post_id)
    likes = models.LikePost.objects.filter(post=post)
    users = []
    for likedata in likes:
        users.append({
            'username': likedata.liker.username,
            'profile_icon': likedata.liker.image.url,
            'timestamp': likedata.timestamp.strftime("%m-%d-%Y %H:%M"),
        })
    context = get_context(request, "Likes | Snapshot")
    context = context | {
        'username': post.author.username,
        'type': 'likers',
        'userlist': users
    }
    return render(request, 'listusers.html', context)

def view_follower_snapshots(request):
    if request.user.is_authenticated:
        postlist = []
        requser = models.FancyUser.objects.get(username=request.user)
        following_users = models.FollowUser.objects.filter(following_user=requser)
        for user in following_users:
            fuser = models.FancyUser.objects.get(username=user.followed_user.username)
            postlist += models.SnapshotPost.objects.filter(author=fuser)
        postlist.sort(key=sort_chrono)
        context = get_context(request, "My Feed | Snapshot") | {"posts": parse_posts(request, postlist)}
        return render(request, 'index.html', context)
    else:
        return redirect("/global")

@login_required(login_url="/login")
def chat_view(request):
    context = get_context(request, "Join Chat Room | Snapshot")
    return render(request, 'chat/index.html', context)

@login_required(login_url="/login")
def view_room(request, room_name):
    if (request.user.is_authenticated):
        context = get_context(request, "Chat | Snapshot") | {"room_name": room_name}
        return render(request, 'chat/room.html', context)
    else:
        return redirect('/')

@login_required(login_url="/login")
def make_post(request):
    if request.method == 'POST':
        form = forms.PostSnapshotForm(request.POST, request.FILES)
        if form.is_valid() and request.user.is_authenticated:
            instance = form.save(request)
            return redirect('/post/' + str(instance.id))
    else:
        form = forms.PostSnapshotForm()
    context = get_context(request, "Create Post | Snapshot") | {"form": form}
    return render(request, 'post.html', context)

@login_required(login_url="/login")
def make_comment(request, post_id):
    if request.method == 'POST':
        form = forms.PostCommentForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            form.save(request, post_id)
    else:
        form = forms.PostCommentForm()
    return redirect('/post/' + str(post_id))

@login_required(login_url="/login")
def follow_user(request, username):
    user = models.FancyUser.objects.get(username=username)
    requser = models.FancyUser.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = forms.FollowUserForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            form.save(request, requser, user)
    else:
        form = forms.FollowUserForm()
    return redirect('/user/' + username)

@login_required(login_url="/login")
def like_post(request, post_id):
    requser = models.FancyUser.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = forms.LikePostForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            form.save(request, post_id, requser)
    else:
        form = forms.LikePostForm()
    return redirect('/post/' + str(post_id))

def logout_view(request):
    logout(request)
    return redirect('/global/')

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