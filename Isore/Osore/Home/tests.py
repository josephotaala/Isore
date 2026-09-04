from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import Announcement, Notification, Photo, Profile


class ClanWorkflowTests(TestCase):
	def setUp(self):
		self.leader = User.objects.create_user('leader', password='test-password-123')
		Profile.objects.create(user=self.leader, role=Profile.LEADER)
		self.member = User.objects.create_user('member', password='test-password-123')
		Profile.objects.create(user=self.member)

	def test_member_can_register_and_reaches_dashboard(self):
		response = self.client.post(reverse('register'), {
			'username': 'new-member',
			'password1': 'test-password-123',
			'password2': 'test-password-123',
		})

		self.assertRedirects(response, reverse('dashboard'))
		self.assertTrue(Profile.objects.filter(user__username='new-member').exists())

	def test_only_leaders_can_publish_and_members_are_notified(self):
		self.client.login(username='member', password='test-password-123')
		forbidden = self.client.get(reverse('leader'))
		self.assertEqual(forbidden.status_code, 403)

		self.client.login(username='leader', password='test-password-123')
		response = self.client.post(reverse('create_announcement'), {
			'title': 'Clan gathering',
			'message': 'We are meeting this weekend.',
		})

		self.assertRedirects(response, reverse('leader'))
		announcement = Announcement.objects.get(title='Clan gathering')
		self.assertTrue(Notification.objects.filter(recipient=self.member, announcement=announcement).exists())

	def test_member_can_only_mark_own_notification_read(self):
		announcement = Announcement.objects.create(author=self.leader, title='Hello', message='Welcome home.')
		notification = Notification.objects.create(recipient=self.member, announcement=announcement)
		self.client.login(username='leader', password='test-password-123')

		response = self.client.post(reverse('mark_notification_read', args=[notification.id]))

		self.assertEqual(response.status_code, 404)
		notification.refresh_from_db()
		self.assertFalse(notification.is_read)

	def test_member_can_upload_photo_to_gallery(self):
		self.client.login(username='member', password='test-password-123')
		image = SimpleUploadedFile('family.png', b'fake-image-data', content_type='image/png')

		response = self.client.post(reverse('upload_photo'), {'image': image, 'caption': 'Together'}, follow=True)

		self.assertRedirects(response, reverse('gallery'))
		self.assertTrue(Photo.objects.filter(uploader=self.member, caption='Together').exists())

	def test_gallery_rejects_non_image_extensions(self):
		self.client.login(username='member', password='test-password-123')
		document = SimpleUploadedFile('notes.txt', b'not-a-photo', content_type='text/plain')

		self.client.post(reverse('upload_photo'), {'image': document})

		self.assertEqual(Photo.objects.count(), 0)
