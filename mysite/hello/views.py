from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


from . import models
from . import forms

# Create your views here.
# def index(request):
#     context = {
#         "title":"Hello Class!",
#         "header": "CINS465 Hello World"
#     }
#     return render(request, "index.html", context = context)

def view_snapshots(request):
    posts = models.SnapshotPostModel.objects.all()
    json_posts = []
    for post in posts:
        comments = models.PostCommentModel.objects.filter(post=post)
        json_comments = []
        for comment in comments:
            json_comments += [{
                "author": comment.author.username,
                "comment": comment.comment,
                "timestamp": comment.timestamp.strftime("%m-%d-%Y %H:%M")
            }]
        json_posts += [{
            "id": post.id,
            "image": post.image.url,
            "author": post.author.username,
            "caption": post.caption,
            "timestamp": post.timestamp.strftime("%m-%d-%Y %H:%M"),
            "comments": json_comments
        }]

    return render(request, 'index.html', context={
        "title": "Snapshot",
        "posts": json_posts
        })

@login_required
def make_post(request):
    if request.method == 'POST':
        form = forms.PostSnapshotForm(request.POST, request.FILES)
        print(form.is_valid())
        print(request.user.is_authenticated)
        if form.is_valid() and request.user.is_authenticated:
            form.save(request)
            return redirect('/')
    else:
        form = forms.PostSnapshotForm()
    return render(request, 'post.html', context={
        "title": "Create Snapshot",
        "form": form
    })

@login_required
def make_comment(request):
    post_id = request.GET.get('post_id')
    if request.method == 'POST':
        form = forms.PostCommentForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            form.save(request, post_id)
            return redirect('/')
    else:
        form = forms.PostCommentForm()
    return render(request, 'comment.html', context={
        "title": "Comment on Snapshot",
        "post_id": post_id,
        "form": form
    })

def logout_view(request):
    logout(request)
    return redirect('/')

def register_view(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)

        if form.is_valid():
            form.save(request)
            return redirect('/login/')
    else:
        form = forms.RegistrationForm()
    return render(request, 'registration/register.html', context={
        "title": "Create Snapshot Account",
        "form": form
    })