from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, Meep, Message
from .forms import MeepForm, SignUpForm, ProfilePicForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import re
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Donation
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DonateSetting


stripe.api_key = settings.STRIPE_SECRET_KEY




def home(request):
	if request.user.is_authenticated:
		form = MeepForm(request.POST or None)
		if request.method == "POST":
			if form.is_valid():
				meep = form.save(commit=False)
				meep.user = request.user
				meep.save()
				messages.success(request, ("Your Meep Has Been Posted!"))
				return redirect('home')
		
		meeps = Meep.objects.all().order_by("-created_at")
		return render(request, 'home.html', {"meeps":meeps, "form":form})
	else:
		meeps = Meep.objects.all().order_by("-created_at")
		return render(request, 'home.html', {"meeps":meeps})


def profile_list(request):
	if request.user.is_authenticated:
		profiles = Profile.objects.exclude(user=request.user).select_related('user').order_by('-user__date_joined')
		return render(request, 'profile_list.html', {"profiles":profiles})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')

def unfollow(request, pk):
	if request.user.is_authenticated:
		# Get the profile to unfollow
		profile = Profile.objects.get(user_id=pk)
		# Unfollow the user
		request.user.profile.follows.remove(profile)
		# Save our profile
		request.user.profile.save()

		# Return message
		messages.success(request, (f"You Have Successfully Unfollowed {profile.user.username}"))
		return redirect(request.META.get("HTTP_REFERER"))

	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')

def follow(request, pk):
	if request.user.is_authenticated:
		# Get the profile to unfollow
		profile = Profile.objects.get(user_id=pk)
		# Unfollow the user
		request.user.profile.follows.add(profile)
		# Save our profile
		request.user.profile.save()

		# Return message
		messages.success(request, (f"You Have Successfully Followed {profile.user.username}"))
		return redirect(request.META.get("HTTP_REFERER"))

	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')




def profile(request, pk):
	if request.user.is_authenticated:
		profile = Profile.objects.get(user_id=pk)
		meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")

		# Post Form logic
		if request.method == "POST":
			# Get current user
			current_user_profile = request.user.profile
			# Get form data
			action = request.POST['follow']
			# Decide to follow or unfollow
			if action == "unfollow":
				current_user_profile.follows.remove(profile)
			elif action == "follow":
				current_user_profile.follows.add(profile)
			# Save the profile
			current_user_profile.save()



		return render(request, "profile.html", {"profile":profile, "meeps":meeps})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')		

def followers(request, pk):
	if request.user.is_authenticated:
		if request.user.id == pk:
			profiles = Profile.objects.get(user_id=pk)
			return render(request, 'followers.html', {"profiles":profiles})
		else:
			messages.success(request, ("That's Not Your Profile Page..."))
			return redirect('home')	
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')


def follows(request, pk):
	if request.user.is_authenticated:
		if request.user.id == pk:
			profiles = Profile.objects.get(user_id=pk)
			return render(request, 'follows.html', {"profiles":profiles})
		else:
			messages.success(request, ("That's Not Your Profile Page..."))
			return redirect('home')	
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')


#@login_required
#def login_user(request):
#    if request.method == "POST":
#        username = request.POST.get("username")
#        password = request.POST.get("password")
#        user = authenticate(request, username=username, password=password)
#
#        if user:
#            if hasattr(user, "emailaddress_set") and not user.emailaddress_set.filter(verified=True).exists():
#                messages.error(request, "Please verify your email first.")
#                return redirect("login")
#
#            login(request, user)
#            return redirect("home")
#
#        messages.error(request, "Invalid credentials")
#        return redirect("login")
#
#    return render(request, "login.html")


#def logout_user(request):
#	logout(request)
#	messages.success(request, ("You Have Been Logged Out. Sorry to Meep You Go..."))
#	return redirect('home')

#def register_user(request):
#    if request.method == "POST":
#        form = SignUpForm(request.POST)
#        if form.is_valid():
#            form.save()
#            messages.success(
#                request,
#                "Account created. Please check your email to verify."
#            )
#            return redirect("account_login")  # ❗ ไป login allauth
#    else:
#        form = SignUpForm()
#
#    return render(request, "account/signup.html", {"form": form})




def update_user(request):
	if request.user.is_authenticated:
		current_user = User.objects.get(id=request.user.id)
		profile_user = Profile.objects.get(user__id=request.user.id)
		# Get Forms
		user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)
		profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()

			login(request, current_user)
			messages.success(request, ("Your Profile Has Been Updated!"))
			return redirect('home')

		return render(request, "update_user.html", {'user_form':user_form, 'profile_form':profile_form})
	else:
		messages.success(request, ("You Must Be Logged In To View That Page..."))
		return redirect('home')
	
def meep_like(request, pk):
	if request.user.is_authenticated:
		meep = get_object_or_404(Meep, id=pk)
		if meep.likes.filter(id=request.user.id):
			meep.likes.remove(request.user)
		else:
			meep.likes.add(request.user)
		
		return redirect(request.META.get("HTTP_REFERER"))

	else:
		messages.success(request, ("You Must Be Logged In To View That Page..."))
		return redirect('home')


def meep_show(request, pk):
	meep = get_object_or_404(Meep, id=pk)
	if meep:
		return render(request, "show_meep.html", {'meep':meep})
	else:
		messages.success(request, ("That Meep Does Not Exist..."))
		return redirect('home')		


def delete_meep(request, pk):
	if request.user.is_authenticated:
		meep = get_object_or_404(Meep, id=pk)
		# Check to see if you own the meep
		if request.user.username == meep.user.username:
			# Delete The Meep
			meep.delete()
			
			messages.success(request, ("The Meep Has Been Deleted!"))
			return redirect(request.META.get("HTTP_REFERER"))	
		else:
			messages.success(request, ("You Don't Own That Meep!!"))
			return redirect('home')

	else:
		messages.success(request, ("Please Log In To Continue..."))
		return redirect(request.META.get("HTTP_REFERER"))


def edit_meep(request,pk):
	if request.user.is_authenticated:
		# Grab The Meep!
		meep = get_object_or_404(Meep, id=pk)

		# Check to see if you own the meep
		if request.user.username == meep.user.username:
			
			form = MeepForm(request.POST or None, instance=meep)
			if request.method == "POST":
				if form.is_valid():
					meep = form.save(commit=False)
					meep.user = request.user
					meep.save()
					messages.success(request, ("Your Meep Has Been Updated!"))
					return redirect('home')
			else:
				return render(request, "edit_meep.html", {'form':form, 'meep':meep})
	
		else:
			messages.success(request, ("You Don't Own That Meep!!"))
			return redirect('home')

	else:
		messages.success(request, ("Please Log In To Continue..."))
		return redirect('home')



@login_required
def search(request):
    if request.method == "POST":
        query = request.POST.get("search", "").strip()

        # 🔍 Search User
        if query.startswith("@"):
            username = query[1:]
            profiles = Profile.objects.filter(
                user__username__icontains=username
            )
            return render(request, "search.html", {
                "mode": "users",
                "query": query,
                "profiles": profiles
            })

        # 🔍 Search Hashtag
        elif query.startswith("#"):
            tag = query[1:]
            posts = Meep.objects.filter(body__icontains=f"#{tag}")
            return render(request, "search.html", {
                "mode": "hashtag",
                "query": query,
                "searched": posts
            })

        # 🔍 Search Posts (default)
        else:
            posts = Meep.objects.filter(body__icontains=query)
            return render(request, "search.html", {
                "mode": "posts",
                "query": query,
                "searched": posts
            })

    return render(request, "search.html")

	

@login_required
def inbox(request):
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('timestamp')

    # ดึงรายชื่อคนที่เคยคุย
    users = set()
    for msg in messages:
        users.add(msg.sender)
        users.add(msg.receiver)
    users.discard(request.user)

    return render(request, "inbox.html", {"users": users})


@login_required
def dm_room(request, pk):
    other_user = get_object_or_404(User, id=pk)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    # mark as read
    messages.filter(receiver=request.user, is_read=False).update(is_read=True)

    if request.method == "POST":
        body = request.POST.get("body")
        if body:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                body=body
            )
            return redirect("dm_room", pk=pk)

    return render(request, "dm_room.html", {
        "other_user": other_user,
        "messages": messages
    })



@login_required
def send_attachment(request, pk):
    receiver = get_object_or_404(User, id=pk)

    if request.method == "POST":
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            image=request.FILES.get("image"),
            file=request.FILES.get("file")
        )
        return redirect("dm_room", pk=pk)
	

@login_required
def delete_chat_room(request, pk):
    other_user = get_object_or_404(User, id=pk)

    # ป้องกัน action แปลก ๆ
    if request.method != "GET":
        return redirect("inbox")

    Message.objects.filter(
        sender=request.user, receiver=other_user
    ).delete()

    Message.objects.filter(
        sender=other_user, receiver=request.user
    ).delete()

    return redirect("inbox")


def calculate_trend_score(tag):
    since = timezone.now() - timedelta(hours=24)

    meeps = Meep.objects.filter(
        body__icontains=f"#{tag}",
        created_at__gte=since
    )

    post_count = meeps.count()
    user_count = meeps.values('user').distinct().count()
    like_count = meeps.aggregate(
        total=Count('likes')
    )['total'] or 0

    score = post_count + user_count + like_count

    return {
        "tag": tag,
        "posts": post_count,
        "users": user_count,
        "likes": like_count,
        "score": score,
    }


def trending_list(request):
    since = timezone.now() - timedelta(hours=24)

    meeps = Meep.objects.filter(created_at__gte=since)

    hashtags = {}
    for meep in meeps:
        tags = re.findall(r"#(\w+)", meep.body.lower())
        for tag in tags:
            if tag not in hashtags:
                hashtags[tag] = calculate_trend_score(tag)

    trending = sorted(
        hashtags.values(),
        key=lambda x: x["score"],
        reverse=True
    )[:10]

    return render(request, "trending.html", {"trending": trending})


def trending_detail(request, tag):

    meepps = Meep.objects.filter(
        body__icontains=f"#{tag}"
    ).order_by("-created_at")

    return render(request, "trending_detail.html", {
        "tag": tag,
        "meepps": meepps
    })

def donate_view(request):
    if request.method == "POST":
        amount = int(request.POST.get("amount"))

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "thb",
                    "product_data": {
                        "name": "Support Donation ☕",
                    },
                    "unit_amount": amount * 100,  # บาท → สตางค์
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri("/donate/success/"),
            cancel_url=request.build_absolute_uri("/donate/"),
        )

        Donation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            amount=amount,
            stripe_session_id=session.id,
			status="pending"
        )

        return redirect(session.url)

    #return render(request, "donate.html", {
    #    "stripe_public_key": settings.STRIPE_PUBLIC_KEY
    #})

def donate_success(request):
    messages.success(request, "💙 Thank you for your support!")
    return render(request, "donate_success.html")

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # ✅ PAYMENT SUCCESS
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        try:
            donation = Donation.objects.get(
                stripe_session_id=session["id"]
            )
            donation.status = "paid"
            donation.payment_intent = session["payment_intent"]
            donation.save()
        except Donation.DoesNotExist:
            pass

    # ❌ PAYMENT FAILED
    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        Donation.objects.filter(
            payment_intent=intent["id"]
        ).update(status="failed")

    return HttpResponse(status=200)


def donate(request):
    donate_setting = DonateSetting.objects.filter(is_active=True).first()
    return render(request, "donate.html", {
        "donate": donate_setting
    })