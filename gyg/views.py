from django.shortcuts import render, redirect, reverse
from .models import Category, Course,Course_Include,UserCourse,CouponCode,Video,File,LiveDoubtSession,Questions,Answer,Subscription
from .forms import AnswerForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, HttpResponseNotFound
import datetime
import razorpay

client = razorpay.Client(auth=("rzp_test_eCJ9lwppcNQcgV", "RPs0WZfsGV5uhsxsIv9ItVuR"))



# live sessions
def live_classes(request):
    user_c = UserCourse.objects.select_related('user').filter(
        user=request.user)
    now = datetime.datetime.now()
    today = now.strftime("%A")
    if user_c.exists():
        user_course = user_c.first()
        courses = user_course.courses.all()
        live = LiveDoubtSession.objects.filter(day=today, course__in=courses)

        return live
    else:
        return None

# user course list
def user_course_list(request):
    user_c = UserCourse.objects.select_related('user').filter(
        user=request.user).first()
    
    return user_c

def index(request):
    if request.user.is_authenticated:
        if request.user.is_teacher==True:
            return redirect('gyg:teacher_dashboard')
        elif request.user.is_student==True:
            return redirect('gyg:dashboard')

    else:
        context = {
            'categories':Category.objects.all(),
        }
        return render(request, 'landing.html',context)


def courseDesc(request, id):
    course = Course.objects.get(id=id)
    course_includes = Course_Include.objects.filter(course=course)

    context = {
        'course':course,
        'course_includes':course_includes,
    }
    if request.user.is_authenticated:
        user_c = UserCourse.objects.filter(user=request.user).first()

        if user_c == None:
            user_course = None
        else:
            user_course = user_c
        context.update({'user_course':user_course})
    return render(request, 'courseDesc.html',context)


def teacher_dashboard(request):
    return render(request, 'teachers/teacher_dashboard.html')


@login_required(login_url='/accounts/login/')
def dashboard(request):
    my_courses_list = user_course_list(request)
    live_class = live_classes(request)

    if my_courses_list == None:
        my_courses = None
    else:
        my_courses = my_courses_list.courses.all()

    if live_class == None:
        live = None
    else:
        live = live_class

    context = {
        'categories':Category.objects.all(),
        'my_courses':my_courses,
        'live':live,
    }
    return render(request, 'students/dashboard.html',context)


# def create_order(request):
#     order_amount = 50000
#     order_currency = 'INR'
#     order_receipt = 'order_rcptid_11'
#     notes = {'Shipping address': 'Bommanahalli, Bangalore'}   # OPTIONAL

#     client.order.create(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes)

@login_required(login_url='/accounts/login/')
def order_summary(request, id):
    course_selected = Course.objects.get(id=id)

    subscription = Subscription.objects.get(course=course_selected)

    if subscription != None:
        course_subscription = subscription
    else:
        course_subscription = None

    order_amount = 100
    order_currency = 'INR'

    response = client.order.create(
        dict(
            amount=order_amount * 100,
            currency=order_currency,
            payment_capture='0',
        ))

    order_id = response['id']
    order_status = response['status']

    if order_status == 'created':
        context = {
            'course_selected': course_selected,
            'course_subscription':course_subscription,
            'price': order_amount,
            'name': request.user.first_name,
            'email': request.user.email,
            'order_id': order_id,
        }
        return render(request, 'order_summary.html', context)

def apply_coupon(request):
    if request.method=='POST':
        coupon_applied = request.POST['coupon_applied']
        courseId = request.POST['courseId']
        order_id = request.POST['order_id']

        course_selected = Course.objects.get(id=courseId)
        course_amount = course_selected.price

        coupon_code = CouponCode.objects.filter(course=course_selected,coupon_name=coupon_applied).first()

        if coupon_code == None:
            coupon_code= None
            discount_amt = None
            final_amt = course_amount
        else:
            discount_amt = int(course_amount) * int(coupon_code.discount_per)/100
            final_amt = int(course_amount) - discount_amt        

        context = {
            'course_selected':course_selected,
            'order_id':order_id,
            'coupon_code':coupon_code,
            'discount_amt':discount_amt,
            'final_amt':final_amt,
        }
        return render(request, 'order_summary.html',context)

@csrf_exempt
def payment_status(request,id):
    response = request.POST
    # print(response)
    params_dict = {
        "razorpay_payment_id": response['razorpay_payment_id'],
        "razorpay_order_id": response['razorpay_order_id'],
        "razorpay_signature": response['razorpay_signature']
    }
    # Verify Signature
    try:
        status = client.utility.verify_payment_signature(params_dict)
        # add_course_to_user(request, id)
        print(status)
        context = {
            'status': 'Payment Successful'
        }
        add_course_to_user(request,id)
        # payment
        return render(request, 'payment_status.html', context)
    except:
        context = {
            'status': 'Payment Failure'
        }
        return render(request, 'payment_status.html', context)




# @login_required(login_url='/accounts/login/')
def add_course_to_user(request,id):
    try:
        course = Course.objects.get(id=id)

        user_course = UserCourse()
        user_course.user = request.user
        user_course.save()
    except Exception:
        return HttpResponseNotFound("Something Went Wrong!!!")

    user_course.courses.add(course)
    # return HttpResponseRedirect(reverse('gyg:courseDesc', args=(id, )))


@login_required(login_url='/accounts/login/')
def user_course_detail(request, id):
    course = Course.objects.get(id=id)

    context = {
        'first_video': course.videos.first(),
        'topics': course.topics.all(),
        'course_id': course.id
    }
    return render(request, 'students/watch_v.html', context)


@login_required(login_url='/accounts/login/')
def play_video(request, course_id, id):
    video = Video.objects.get(id=id)
    course = Course.objects.get(id=course_id)
    print(course)
    context = {
        'topics': course.topics.all(),
        'play_video': video,
        'course_id': course.id
    }
    return render(request, 'students/watch.html', context)

def discussion_detail(request, id):
    if request.method == 'POST':
        answer = request.POST.get('answer')
        answer_img = request.FILES.get('answer_img')
        question = Questions.objects.filter(id=id).first()
        answer_for = question
        answer_by = request.user

        answer_db = Answer()
        answer_db.answer_for = answer_for
        answer_db.answer_img = answer_img
        answer_db.answer_by = answer_by
        answer_db.answer = answer
        answer_db.save()

        return HttpResponseRedirect(
            reverse('gyg:discussion-detail', args=(id, )))
    form = AnswerForm()
    context = {
        'question': Questions.objects.get(id=id),
        'form': form,
    }
    return render(request, 'discussion-detail.html', context)