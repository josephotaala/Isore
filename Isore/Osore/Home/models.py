from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
	LEADER = 'leader'
	MEMBER = 'member'
	ROLE_CHOICES = [(LEADER, 'Clan leader'), (MEMBER, 'Ordinary member')]

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=MEMBER)
	phone = models.CharField(max_length=30, blank=True)
	joined_at = models.DateTimeField(auto_now_add=True)
	is_active_member = models.BooleanField(default=True)

	def __str__(self):
		return self.user.get_username()


class Announcement(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
	title = models.CharField(max_length=160)
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.title


class Notification(models.Model):
	recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
	announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='notifications')
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']
		constraints = [
			models.UniqueConstraint(fields=['recipient', 'announcement'], name='one_notification_per_announcement'),
		]


class Photo(models.Model):
	uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
	image = models.FileField(upload_to='gallery/')
	caption = models.CharField(max_length=180, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.caption or f'{self.uploader.username} photo'
