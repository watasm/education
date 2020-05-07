from django.db import models
from django.contrib.auth.models import User
import uuid

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

class Profile(models.Model):
    user = models.OneToOneField(User, related_name = 'profile', on_delete = models.CASCADE)
    image = models.ImageField('image', upload_to='users/images', blank=True)
    is_verified = models.BooleanField('verified', default=False)
    verification_uuid = models.UUIDField('Unique Verification UUID', default=uuid.uuid4)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['id']

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if not self.id:
            self.image = self.compress_image(self.image)
        super(Profile, self).save(*args, **kwargs)

    def compress_image(self, uploaded_image):
        img = Image.open(uploaded_image).convert('RGB')
        outputIoStream = BytesIO()
        img = img.resize((400, 400))
        img.save(outputIoStream , format='JPEG', quality=100)
        outputIoStream.seek(0)
        uploaded_image = InMemoryUploadedFile(outputIoStream, 'ImageField', "{} avatar.jpg".format(self.user.username), 'image/jpeg', None, None)
        return uploaded_image
