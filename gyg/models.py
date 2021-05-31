from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import datetime

class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser,is_student,is_teacher, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            is_student=is_student,
            is_teacher=is_teacher,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password,**extra_fields):
        return self._create_user(email, password, False, False,True,False, **extra_fields)

    def create_superuser(self, email, password,**extra_fields):
        user=self._create_user(email, password, True, True,True,False, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=254, null=True, blank=True)
    last_name = models.CharField(max_length=254, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_student = models.BooleanField(default=True)
    is_teacher = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)


# 
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Course(models.Model):
    COURSE_PAY = [
        ('Subscription', 'Subscription'),
        ('One-Time-Pay', 'One-Time-Pay'),
    ]
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 null=True,
                                 related_name='courses')
    title = models.CharField(max_length=200)
    brief_desc = models.TextField(null=True)
    course_thumbnail = models.ImageField(upload_to="Course Thumbnail",
                                     null=True,
                                     blank=True)
    tutor = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    is_free = models.BooleanField(default=False)
    price = models.IntegerField(default=0, null=True)
    discount = models.FloatField(default=0, null=True)
    total = models.FloatField(default=0, null=True)
    course_pay = models.CharField(max_length=200, choices=COURSE_PAY)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return f" {self.title}-{self.course_pay}"



class Course_Include(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True)
    features = models.CharField(max_length=400)
    def __str__(self):
        return self.features



class Topic(models.Model):
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='topics')
    title = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.course}-{self.title}"


class Video(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='videos',
        null=True,
    )
    topic = models.ForeignKey(Topic,
                              on_delete=models.CASCADE,
                              related_name='videos',
                              null=True)
    title = models.CharField(max_length=500, null=True)
    content = models.CharField(max_length=1000)
    free_view = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('id', )


class File(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='files',
        null=True,
    )
    topic = models.ForeignKey(Topic,
                              on_delete=models.CASCADE,
                              related_name='files',
                              null=True)
    title = models.CharField(max_length=500, null=True)
    files = models.FileField(upload_to='Files', null=True, blank=True)
    preview = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Subscription(models.Model):
    EVERY = [
        ('1 MONTH', '1 MONTH'),
        ('2 MONTHS', '2 MONTHS'),
        ('3 MONTHS', '3 MONTHS'),
    ]
    FOR = [
        ('3 Months', '3 Months'),
        ('6 Months', '6 Months'),
        ('1 Year', '1 Year'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    every = models.CharField(choices=EVERY, max_length=100)
    till = models.CharField(choices=FOR, max_length=100)

    def __str__(self):
        return f"every {self.every} | for {self.till}"



class CouponCode(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    coupon_name = models.CharField(max_length=50)
    discount_per = models.IntegerField()
    valid_from = models.DateField()
    valid_till = models.DateField()
    limit = models.IntegerField()

    def __str__(self):
        return f"{self.coupon_name}-{self.course}"


class Payment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    amount = models.IntegerField()
    coupon = models.ForeignKey(CouponCode, on_delete=models.CASCADE, blank=True)
    
    def __str__(self):
        return f"{self.course}-{self.amount}"


class UserCourse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course,
                                     blank=True,
                                     related_name='user_courses')
    
    def __str__(self):
        return f'{self.user}'


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True)
    start_date = models.DateTimeField(default=datetime.datetime.now)
    next_payment_date = models.DateTimeField()
    last_payment_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user}-{self.next_payment_date}-{self.last_payment_date}"


DAYS = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
]


class LiveDoubtSession(models.Model):
    day = models.CharField(max_length=100, choices=DAYS, null=True)
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course,
                               on_delete=models.CASCADE,
                               related_name='live_doubts',
                               blank=True,
                               null=True)
    link = models.CharField(max_length=5000)
    thumbnail = models.ImageField(upload_to='Lives')
    from_time = models.TimeField(null=True)
    to_time = models.TimeField(null=True)

    def __str__(self):
        return f"{self.course}-{self.title}"


class Questions(models.Model):
    asked_by = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 related_name='user_questions')
    # course = models.ForeignKey(Course,
    #                            on_delete=models.CASCADE,
    #                            null=True,
    #                            related_name='questions')

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    ques_img = models.ImageField(upload_to='Question', blank=True, null=True)
    date = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f"{self.asked_by}"

    class Meta:
        ordering = ['-date']


class Answer(models.Model):
    answer_for = models.ForeignKey(Questions,
                                   on_delete=models.CASCADE,
                                   related_name='answers')
    answer_by = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  related_name='user_answers',
                                  null=True)
    answer_img = models.ImageField(upload_to='Answers', blank=True, null=True)
    answer = models.TextField()

    def __str__(self):
        return f"{self.answer_by}"