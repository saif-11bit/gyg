from django.urls import path
from .views import (
    index, dashboard,
    teacher_dashboard,
    courseDesc,
    order_summary,
    payment_status,
    user_course_detail,
    play_video,
    discussion_detail,
)

app_name = 'gyg'


urlpatterns = [
    path('', index, name='index'),
    path('courseDesc/<int:id>/', courseDesc, name='courseDesc'),
    path('dashboard/', dashboard, name='dashboard'),
    path('teacher_dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('status/<int:id>/', payment_status, name='payment-status'),
    path('order-summary/<int:id>/', order_summary, name="order-summary"),
    path('<id>/watch/', user_course_detail, name='user-course-detail'),
    path('watch/<int:course_id>/<int:id>/', play_video, name="play_video"),
    path('discussion-detail/<int:id>/',discussion_detail,name='discussion-detail'),
]
 