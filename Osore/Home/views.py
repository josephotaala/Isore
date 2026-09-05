from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Announcement, Notification, Photo, Profile


def home(request):
	if request.user.is_authenticated:
		return redirect('dashboard')
	return render(request, 'Home/home.html')


def role_required(role):
	def decorator(view):
		@wraps(view)
		@login_required
		def wrapped(request, *args, **kwargs):
			if not hasattr(request.user, 'profile') or request.user.profile.role != role:
				return HttpResponseForbidden('This page is for clan leaders only.')
			return view(request, *args, **kwargs)
		return wrapped
	return decorator


@login_required
def dashboard(request):
	profile, _ = Profile.objects.get_or_create(user=request.user)
	context = {
		'profile': profile,
		'announcements': Announcement.objects.all()[:5],
		'unread_count': request.user.notifications.filter(is_read=False).count(),
		'notifications': request.user.notifications.select_related('announcement')[:5],
		'member_count': Profile.objects.filter(is_active_member=True).count(),
	}
	return render(request, 'Home/dashboard.html', context)


def login_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard')
	if request.method == 'POST':
		user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
		if user is not None:
			login(request, user)
			return redirect('dashboard')
		messages.error(request, 'Those details do not match an account.')
	return render(request, 'Home/login.html')


def logout_view(request):
	logout(request)
	return redirect('login')


def register(request):
	form = UserCreationForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		user = form.save()
		Profile.objects.create(user=user)
		login(request, user)
		return redirect('dashboard')
	return render(request, 'Home/register.html', {'form': form})


@role_required(Profile.LEADER)
def leader_page(request):
	return render(request, 'Home/leader.html', {
		'members': Profile.objects.select_related('user').order_by('-joined_at'),
		'announcements': Announcement.objects.all()[:8],
	})


@role_required(Profile.LEADER)
@require_POST
def create_announcement(request):
	title = request.POST.get('title', '').strip()
	message = request.POST.get('message', '').strip()
	if title and message:
		announcement = Announcement.objects.create(author=request.user, title=title, message=message)
		recipients = User.objects.filter(profile__is_active_member=True).exclude(pk=request.user.pk)
		Notification.objects.bulk_create([
			Notification(recipient=user, announcement=announcement) for user in recipients
		])
		messages.success(request, f'Announcement sent to {recipients.count()} members.')
	else:
		messages.error(request, 'Add a title and message before publishing.')
	return redirect('leader')


@login_required
def member_page(request):
	return render(request, 'Home/member.html', {
		'profile': getattr(request.user, 'profile', None),
		'notifications': request.user.notifications.select_related('announcement'),
	})


@login_required
def gallery(request):
	return render(request, 'Home/gallery.html', {'photos': Photo.objects.select_related('uploader')})


@login_required
@require_POST
def upload_photo(request):
	image = request.FILES.get('image')
	caption = request.POST.get('caption', '').strip()
	allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
	if not image:
		messages.error(request, 'Choose a photo before uploading.')
	elif image.name.lower().rsplit('.', 1)[-1] not in {extension[1:] for extension in allowed_extensions}:
		messages.error(request, 'Upload a JPG, PNG, GIF, or WEBP image.')
	elif image.size > 5 * 1024 * 1024:
		messages.error(request, 'Photos must be smaller than 5 MB.')
	else:
		Photo.objects.create(uploader=request.user, image=image, caption=caption)
		messages.success(request, 'Your photo was added to the clan gallery.')
	return redirect('gallery')


@login_required
@require_POST
def mark_notification_read(request, notification_id):
	notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
	notification.is_read = True
	notification.save(update_fields=['is_read'])
	return redirect(request.POST.get('next') or 'dashboard')

