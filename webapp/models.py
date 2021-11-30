from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


def gen_candidate_id():
    last_candidate = Candidate.objects.all().order_by('candidate_id').last()
    if not last_candidate:
        return '01001'
    candidate_id = last_candidate.candidate_id
    custom_int = int(candidate_id[:6])
    new_custom_int = custom_int+1
    new_candidate_id = str(new_custom_int).zfill(5)
    return new_candidate_id


def user_directory_path(instance, filename):
    this = Candidate.objects.filter(user_id=instance.user_id)

    if len(this) == 0:
        return 'user_{0}/{1}'.format(instance.user_id, filename)
    this = Candidate.objects.get(user_id=instance.user_id)
    if this.Profile_pic != filename:
        this.Profile_pic.delete(save=False)
        print(this.Profile_pic)
        return 'user_{0}/{1}'.format(instance.user_id, filename)
    else:
        return 'user_{0}/{1}'.format(instance.user_id, filename)


class Candidate(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    candidate_id = models.CharField(max_length=10, default=gen_candidate_id, editable=True)
    Profile_pic = models.ImageField(upload_to=user_directory_path)
    Name = models.CharField(max_length=200)
    Gender = models.CharField(max_length=10)
    DOB = models.CharField(max_length=40)
    Occupation_type = models.CharField(max_length=40)
    Occupation_detail = models.CharField(max_length=500, null=True, blank=True)
    Education_title = models.CharField(max_length=20)
    Education_area = models.CharField(max_length=200)
    Hobby = models.CharField(max_length=500)
    About = models.CharField(max_length=500)
    Marital_st = models.CharField(max_length=30)
    Height = models.FloatField()
    Blood_group = models.CharField(max_length=30)
    Birth_name = models.CharField(max_length=50)
    Birth_time = models.CharField(max_length=30)
    Birth_place = models.CharField(max_length=50)
    Mother_tong = models.CharField(max_length=30)
    Complexion = models.CharField(max_length=30)
    Annual_income = models.CharField(max_length=30)
    First_gotra = models.CharField(max_length=30)
    Second_gotra = models.CharField(max_length=30)
    Address = models.CharField(max_length=500)
    City = models.CharField(max_length=50)
    Country = models.CharField(max_length=30)
    Postal_code = models.BigIntegerField()
    Email = models.EmailField()
    Contact_1 = models.BigIntegerField()
    Contact_1_name = models.CharField(max_length=100)
    Contact_1_relation = models.CharField(max_length=30)
    Contact_2 = models.BigIntegerField(null=True, blank=True)
    Contact_2_name = models.CharField(max_length=100, null=True, blank=True)
    Contact_2_relation = models.CharField(max_length=30, null=True, blank=True)
    Family = models.CharField(max_length=30)
    Fathers_name = models.CharField(max_length=150)
    Fathers_occupation = models.CharField(max_length=100)
    Mothers_name = models.CharField(max_length=150)
    Mothers_occupation = models.CharField(max_length=100)
    Number_brother = models.IntegerField()
    Brother_detail = models.CharField(max_length=500, null=True, blank=True)
    Number_sister = models.IntegerField()
    Sister_detail = models.CharField(max_length=500, null=True, blank=True)
    Partner_compx = models.CharField(max_length=100)
    Partner_occupation = models.CharField(max_length=100)
    Preffered_city = models.CharField(max_length=100)
    Partner_agefrom = models.IntegerField()
    Partner_ageto = models.IntegerField()
    Partner_height = models.FloatField()
    Partner_income = models.CharField(max_length=50)
    Partner_qualification = models.CharField(max_length=100)
    Approve_choices = (
        ('No', 'No'),
        ('Yes', 'Yes')
    )
    Approval = models.CharField(max_length=10, choices=Approve_choices, default='No')
    Member_choices = (
        ('Normal', 'Normal'),
        ('Premium', 'Premium')
    )
    Member = models.CharField(max_length=10, choices=Member_choices, default='Normal')


def user_gallery(instance, filename):
    return 'gal_{0}/{1}'.format(instance.user_id, filename)


class Gallary(models.Model):
    user = models.CharField(max_length=10)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    images = models.ImageField(upload_to=user_gallery, null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.images.delete()
        super().delete(*args, **kwargs)


class Event(models.Model):
    Image = models.ImageField(upload_to='webapp/images')
    Name = models.CharField(max_length=100)
    Description = models.CharField(max_length=500)

    def __str__(self):
        return self.Name


class Event_enroll(models.Model):
    Name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    vid = models.CharField(max_length=10, null=True)
    Person_name = models.CharField(max_length=100, null=True)
    Contact = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.Person_name


class Favorite(models.Model):
    Profile = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Seen(models.Model):
    profile = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first = models.DateTimeField(auto_now=True)


class Feedback(models.Model):
    Feed_Choices = [
        ('Bug', 'Bug'),
        ('Feedback', 'Feedback'),
        ('Other', 'Other')
    ]

    Star_Choices = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Feed = models.CharField(max_length=30, choices=Feed_Choices)
    Suggestion = models.CharField(max_length=500)
    Star = models.CharField(max_length=20, choices=Star_Choices, null=True, blank=True)

