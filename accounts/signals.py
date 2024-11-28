from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User, Profile
  
@receiver(post_save, sender=User)
#reciever will get the signal->post_save from sender-> user
#reciever function below will create/update the userProfile accordingly
#immediately after creation/updation of user(sender)
def user_profile_save(sender, created, instance, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        try:
            profile = Profile.objects.get(user=instance)
            profile.save()
        except:
            Profile.objects.create(user=instance)
