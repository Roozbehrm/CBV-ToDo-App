from django.db import models

# Create your models here.
#User = get_user_model()
class Task(models.Model):
    profile = models.ForeignKey(
        'accounts.profile', on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        order_with_respect_to = "profile"