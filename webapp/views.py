from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from .models import *
from django.contrib import messages
from django.db.models import Q
import uuid
from django.conf import settings
from django.core.mail import send_mail
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.


# index page
def index(request):
    return render(request, 'webapp/home.html')


# registration
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username already taken...')
                return render(request, 'webapp/register.html')
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already registered. Please login to your account!')
                return render(request, 'webapp/register.html')
            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                                email=email, password=password1)
                user.save()
                auth_token = str(uuid.uuid4())
                profile_obj = Profile.objects.create(user=user, auth_token=auth_token)
                profile_obj.save()
                send_mail_after_registration(email, auth_token)

                messages.info(request, 'A verification email has been sent to your mail id. Please verify to login!'
                                       'If you do not find the mail in inbox, please check in spam folder.')
                return render(request, 'webapp/login.html')
        else:
            messages.info(request, 'Password not matching...')
            return render(request, 'webapp/register.html')
    else:
        return render(request, 'webapp/register.html')


# email verification
def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()

        if profile_obj:
            if profile_obj.is_verified:
                messages.info(request, 'Your account is already verified. Login to proceed!')
                return redirect('/')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.info(request, 'Your account has been verified. Login to proceed!')
            return redirect('/')
        else:
            messages.info(request, 'Please verify your profile, check your email...')
            return render(request, 'webapp/login.html')
    except Exception as e:
        print(e)
        return render(request, 'webapp/login.html')


# verification mail
def send_mail_after_registration(email, token):
    subject = 'Your account needs to be verified'
    message = f'Hi click the link to verify your account  https://vivahtest.herokuapp.com/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


# user login
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = auth.authenticate(username=User.objects.get(email=username), password=password)
        except:
            user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_staff:
                return render(request, 'webapp/admin.html')
            profile_obj = Profile.objects.get(user=user)
            if not profile_obj.is_verified:
                messages.info(request, 'Profile is not verified check your mail.')
                return render(request, 'webapp/login.html')
            else:
                auth.login(request, user)
                events = Event.objects.all()
                candidates = Candidate.objects.filter(Approval='Yes').exclude(user_id=request.user).order_by('-candidate_id')[:10]
                if Candidate.objects.filter(user_id=user).exists():
                    return render(request, 'webapp/canhome.html', {'events': events, 'candidates': candidates})
                else:
                    messages.info(request, 'Please create your profile!')
                    return render(request, 'webapp/new_profile.html')
        else:
            messages.info(request, "Invalid Username or Password!")
            return render(request, 'webapp/login.html')
    else:
        return render(request, 'webapp/login.html')


# user logout
def logout(request):
    auth.logout(request)
    return redirect('/')


# create new profile
def new_profile(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            if len(request.FILES) == 0:
                messages.info(request, 'Please upload your profile picture!')
                return render(request, 'webapp/new_profile.html')

            profile_pic = request.FILES['picture']
            name = request.POST.get('Name')
            gender = request.POST.get('Gender')
            dob = request.POST.get('Dob')
            occupation_type = request.POST.get('Occupation_type')
            occupation_detail = request.POST.get('Occupation_detail')
            education_title = request.POST.get('Education_title')
            education_area = request.POST.get('Education_area')
            hobby = request.POST.get('Hobby')
            about = request.POST.get('About')
            marital_st = request.POST.get('Marital_st')
            height = request.POST.get('Height')
            blood_group = request.POST.get('Blood_group')
            birth_name = request.POST.get('Birth_name')
            birth_time = request.POST.get('Birth_time')
            birth_place = request.POST.get('Birth_place')
            mother_tong = request.POST.get('Mother_tong')
            complexion = request.POST.get('Complexion')
            annual_income = request.POST.get('Annual_income')
            first_gotra = request.POST.get('First_gotra')
            second_gotra = request.POST.get('Second_gotra')
            address = request.POST.get('Address')
            city = request.POST.get('City')
            country = request.POST.get('Country')
            postal_code = request.POST.get('Postal_code')
            email = request.POST.get('Email')
            contact_1 = request.POST.get('contact_1')
            contact_1_name = request.POST.get('contact1_name')
            contact_1_relation = request.POST.get('contact1_rel')
            contact_2 = request.POST.get('contact_2')
            contact_2_name = request.POST.get('contact2_name')
            contact_2_relation = request.POST.get('contact2_rel')
            family = request.POST.get('Family_type')
            fathers_name = request.POST.get('fathers_name')
            fathers_occupation = request.POST.get('father_occupation')
            mothers_name = request.POST.get('mother_name')
            mothers_occupation = request.POST.get('mother_occupation')
            number_brother = request.POST.get('number_brother')
            brother_detail = request.POST.get('brother_detail')
            number_sister = request.POST.get('number_sister')
            sister_detail = request.POST.get('sister_detail')
            partner_compx = request.POST.get('partner_compx')
            partner_occupation = request.POST.get('partner_occupation')
            preffered_city = request.POST.get('preffered_city')
            partner_agefrom = request.POST.get('age_from')
            partner_ageto = request.POST.get('age_to')
            partner_height = request.POST.get('partner_height')
            partner_income = request.POST.get('partner_income')
            partner_qualification = request.POST.get('partner_qualification')

            candidate = Candidate.objects.create(Profile_pic=profile_pic, Name=name, Gender=gender, DOB=dob,
                                                 Occupation_type=occupation_type, Occupation_detail=occupation_detail,
                                                 Education_title=education_title, Education_area=education_area,
                                                 Hobby=hobby, About=about, Marital_st=marital_st,
                                                 Height=height, Blood_group=blood_group, Birth_name=birth_name,
                                                 Birth_place=birth_place, Birth_time=birth_time, Mother_tong=mother_tong,
                                                 Complexion=complexion, Annual_income=annual_income, user_id=request.user,
                                                 First_gotra=first_gotra, Second_gotra=second_gotra, Address=address,
                                                 City=city, Country=country, Postal_code=postal_code, Email=email,
                                                 Contact_1=contact_1, Contact_1_name=contact_1_name,
                                                 Contact_1_relation=contact_1_relation, Contact_2=contact_2,
                                                 Contact_2_name=contact_2_name, Contact_2_relation=contact_2_relation,
                                                 Family=family, Fathers_name=fathers_name,
                                                 Fathers_occupation=fathers_occupation, Mothers_name=mothers_name,
                                                 Mothers_occupation=mothers_occupation,
                                                 Number_brother=number_brother, Brother_detail=brother_detail,
                                                 Number_sister=number_sister, Sister_detail=sister_detail,
                                                 Partner_compx=partner_compx, Partner_occupation=partner_occupation,
                                                 Preffered_city=preffered_city, Partner_agefrom=partner_agefrom,
                                                 Partner_ageto=partner_ageto, Partner_height=partner_height,
                                                 Partner_income=partner_income,
                                                 Partner_qualification=partner_qualification)
            candidate.save()
            events = Event.objects.all()
            messages.info(request, "Profile created successfully!!! It will take 48 hours to activate."
                                   "Meanwhile you can edit your profile and add more images to gallery!")
            candidates = Candidate.objects.filter(Approval='Yes').exclude(user_id=request.user).order_by('-candidate_id')[:10]
            return render(request, 'webapp/canhome.html', {'events': events, 'candidates': candidates})
        else:
            return render(request, 'webapp/new_profile.html')


# go to dashboard
def dashboard(request):
    if request.user.is_authenticated:
        events = Event.objects.all()
        candidates = Candidate.objects.filter(Approval='Yes').exclude(user_id=request.user).order_by('-candidate_id')[:10]
        return render(request, 'webapp/canhome.html', {'events': events, 'candidates': candidates})
    else:
        return render(request, 'webapp/home.html')


# user(self) profile
def profile(request):
    if request.user.is_authenticated:
        data = Candidate.objects.filter(user_id=request.user)
        if len(data) == 0:
            messages.info(request, 'Please create your profile..')
            return render(request, 'webapp/new_profile.html')
        else:
            return render(request, 'webapp/profile.html', {'data': data})
    else:
        return render(request, 'webapp/home.html')


# move to update profile page
def update_profile(request):
    if request.user.is_authenticated:
        data = Candidate.objects.filter(user_id=request.user)
        return render(request, 'webapp/update_profile.html', {'data': data})
    else:
        return render(request, 'webapp/home.html')


# update profile
def update(request):
    if request.user.is_authenticated:
        candidate = Candidate.objects.get(user_id=request.user)
        if request.method == 'POST':
            iprofile_pic = candidate.Profile_pic
            if len(request.FILES) != 0:
                iprofile_pic = request.FILES['picture']

            iname = request.POST.get('Name')
            if len(request.POST.get('Name')) == 0:
                iname = candidate.Name
            igender = request.POST.get('Gender')
            if len(request.POST.get('Gender')) == 0:
                igender = candidate.Gender
            idob = request.POST.get('Dob')
            if len(request.POST.get('Dob')) == 0:
                idob = candidate.DOB
            ioccupation_type = request.POST.get('Occupation_type')
            if len(request.POST.get('Occupation_type')) == 0:
                ioccupation_type = candidate.Occupation_type
            ioccupation_detail = request.POST.get('Occupation_detail')
            if len(request.POST.get('Occupation_detail')) == 0:
                ioccupation_detail = candidate.Occupation_detail
            ieducation_title = request.POST.get('Education_title')
            if len(request.POST.get('Education_title')) == 0:
                ieducation_title = candidate.Education_title
            ieducation_area = request.POST.get('Education_area')
            if len(request.POST.get('Education_area')) == 0:
                ieducation_area = candidate.Education_area
            ihobby = request.POST.get('Hobby')
            if len(request.POST.get('Hobby')) == 0:
                ihobby = candidate.Hobby
            iabout = request.POST.get('About')
            if len(request.POST.get('About')) == 0:
                iabout = candidate.About
            imarital_st = request.POST.get('Marital_st')
            if len(request.POST.get('Marital_st')) == 0:
                imarital_st = candidate.Marital_st
            iheight = request.POST.get('Height')
            if len(request.POST.get('Height')) == 0:
                iheight = candidate.Height
            iblood_group = request.POST.get('Blood_group')
            if len(request.POST.get('Blood_group')) == 0:
                iblood_group = candidate.Blood_group
            ibirth_name = request.POST.get('Birth_name')
            if len(request.POST.get('Birth_name')) == 0:
                ibirth_name = candidate.Birth_name
            ibirth_time = request.POST.get('Birth_time')
            if len(request.POST.get('Birth_time')) == 0:
                ibirth_time = candidate.Birth_time
            ibirth_place = request.POST.get('Birth_place')
            if len(request.POST.get('Birth_place')) == 0:
                ibirth_place = candidate.Birth_place
            imother_tong = request.POST.get('Mother_tong')
            if len(request.POST.get('Mother_tong')) == 0:
                imother_tong = candidate.Mother_tong
            icomplexion = request.POST.get('Complexion')
            if len(request.POST.get('Complexion')) == 0:
                icomplexion = candidate.Complexion
            iannual_income = request.POST.get('Annual_income')
            if len(request.POST.get('Annual_income')) == 0:
                iannual_income = candidate.Annual_income
            ifirst_gotra = request.POST.get('First_gotra')
            if len(request.POST.get('First_gotra')) == 0:
                ifirst_gotra = candidate.First_gotra
            isecond_gotra = request.POST.get('Second_gotra')
            if len(request.POST.get('Second_gotra')) == 0:
                isecond_gotra = candidate.Second_gotra
            iaddress = request.POST.get('Address')
            if len(request.POST.get('Address')) == 0:
                iaddress = candidate.Address
            icity = request.POST.get('City')
            if len(request.POST.get('City')) == 0:
                icity = candidate.City
            ipostal_code = request.POST.get('Postal_code')
            if len(request.POST.get('Postal_code')) == 0:
                ipostal_code = candidate.Postal_code
            icountry = request.POST.get('Country')
            if len(request.POST.get('Country')) == 0:
                icountry = candidate.Country
            iemail = request.POST.get('Email')
            if len(request.POST.get('Email')) == 0:
                iemail = candidate.Email
            icontact_1 = request.POST.get('contact_1')
            if len(request.POST.get('contact_1')) == 0:
                icontact_1 = candidate.Contact_1
            icontact_1_name = request.POST.get('contact1_name')
            if len(request.POST.get('contact1_name')) == 0:
                icontact_1_name = candidate.Contact_1_name
            icontact_1_relation = request.POST.get('contact1_rel')
            if len(request.POST.get('contact1_rel')) == 0:
                icontact_1_relation = candidate.Contact_1_relation
            icontact_2 = request.POST.get('contact_2')
            if len(request.POST.get('contact_2')) == 0:
                icontact_2 = candidate.Contact_2
            icontact_2_name = request.POST.get('contact2_name')
            if len(request.POST.get('contact2_name')) == 0:
                icontact_2_name = candidate.Contact_2_name
            icontact_2_relation = request.POST.get('contact2_rel')
            if len(request.POST.get('contact2_rel')) == 0:
                icontact_2_relation = candidate.Contact_2_relation
            ifamily = request.POST.get('Family_type')
            if len(request.POST.get('Family_type')) == 0:
                ifamily = candidate.Family
            ifathers_name = request.POST.get('fathers_name')
            if len(request.POST.get('fathers_name')) == 0:
                ifathers_name = candidate.Fathers_name
            ifathers_occupation = request.POST.get('father_occupation')
            if len(request.POST.get('father_occupation')) == 0:
                ifathers_occupation = candidate.Fathers_occupation
            imothers_name = request.POST.get('mother_name')
            if len(request.POST.get('mother_name')) == 0:
                imothers_name = candidate.Mothers_name
            imothers_occupation = request.POST.get('mother_occupation')
            if len(request.POST.get('mother_occupation')) == 0:
                imothers_occupation = candidate.Mothers_occupation
            inumber_brother = request.POST.get('number_brother')
            if len(request.POST.get('number_brother')) == 0:
                inumber_brother = candidate.Number_brother
            ibrother_detail = request.POST.get('brother_detail')
            if len(request.POST.get('brother_detail')) == 0:
                ibrother_detail = candidate.Brother_detail
            inumber_sister = request.POST.get('number_sister')
            if len(request.POST.get('number_sister')) == 0:
                inumber_sister = candidate.Number_sister
            isister_detail = request.POST.get('sister_detail')
            if len(request.POST.get('sister_detail')) == 0:
                isister_detail = candidate.Sister_detail
            ipartner_compx = request.POST.get('partner_compx')
            if len(request.POST.get('partner_compx')) == 0:
                ipartner_compx = candidate.Partner_compx
            ipartner_occupation = request.POST.get('partner_occupation')
            if len(request.POST.get('partner_occupation')) == 0:
                ipartner_occupation = candidate.Partner_occupation
            ipreffered_city = request.POST.get('preffered_city')
            if len(request.POST.get('preffered_city')) == 0:
                ipreffered_city = candidate.Preffered_city
            ipartner_agefrom = request.POST.get('age_from')
            if len(request.POST.get('age_from')) == 0:
                ipartner_agefrom = candidate.Partner_agefrom
            iparnter_ageto = request.POST.get('age_to')
            if len(request.POST.get('age_to')) == 0:
                iparnter_ageto = candidate.Partner_ageto
            ipartner_height = request.POST.get('partner_height')
            if len(request.POST.get('partner_height')) == 0:
                ipartner_height = candidate.Partner_height
            ipartner_income = request.POST.get('partner_income')
            if len(request.POST.get('partner_income')) == 0:
                ipartner_income = candidate.Partner_income
            ipartner_qualification = request.POST.get('partner_qualification')
            if len(request.POST.get('partner_qualification')) == 0:
                ipartner_qualification = candidate.Partner_qualification

            candidate.Profile_pic = iprofile_pic
            candidate.Name = iname
            candidate.Gender = igender
            candidate.DOB = idob
            candidate.Occupation_type = ioccupation_type
            candidate.Occupation_detail = ioccupation_detail
            candidate.Education_title = ieducation_title
            candidate.Education_area = ieducation_area
            candidate.Hobby = ihobby
            candidate.About = iabout
            candidate.Marital_st = imarital_st
            candidate.Height = iheight
            candidate.Blood_group = iblood_group
            candidate.Birth_name = ibirth_name
            candidate.Birth_place = ibirth_place
            candidate.Birth_time = ibirth_time
            candidate.Mother_tong = imother_tong
            candidate.Complexion = icomplexion
            candidate.Annual_income = iannual_income
            candidate.First_gotra = ifirst_gotra
            candidate.Second_gotra = isecond_gotra
            candidate.Address = iaddress
            candidate.City = icity
            candidate.Postal_code = ipostal_code
            candidate.Country = icountry
            candidate.Email = iemail
            candidate.Contact_1 = icontact_1
            candidate.Contact_1_name = icontact_1_name
            candidate.Contact_1_relation = icontact_1_relation
            candidate.Contact_2 = icontact_2
            candidate.Contact_2_name = icontact_2_name
            candidate.Contact_2_relation = icontact_2_relation
            candidate.Family = ifamily
            candidate.Fathers_name = ifathers_name
            candidate.Fathers_occupation = ifathers_occupation
            candidate.Mothers_name = imothers_name
            candidate.Mothers_occupation = imothers_occupation
            candidate.Number_brother = inumber_brother
            candidate.Brother_detail = ibrother_detail
            candidate.Number_sister = inumber_sister
            candidate.Sister_detail = isister_detail
            candidate.Partner_compx = ipartner_compx
            candidate.Partner_occupation = ipartner_occupation
            candidate.Preffered_city = ipreffered_city
            candidate.Partner_agefrom = ipartner_agefrom
            candidate.Partner_ageto = iparnter_ageto
            candidate.Partner_height = ipartner_height
            candidate.Partner_income = ipartner_income
            candidate.Partner_qualification = ipartner_qualification

            candidate.save()

            data1 = Candidate.objects.filter(user_id=request.user)
            if candidate.Approval == 'No':
                messages.info(request, 'Profile updated successfully! Your profile is not approved yet, it can take 48 '
                                       'to 72 hours after creation of profile.')
                return render(request, 'webapp/profile.html', {'data': data1})
            else:
                messages.info(request, 'Profile updated successfully..!')
                return render(request, 'webapp/profile.html', {'data': data1})
        else:
            data = Candidate.objects.filter(user_id=request.user)
            return render(request, 'webapp/update_profile.html', {'data': data})
    else:
        return render(request, 'webapp/home.html')


# move to search page
def search(request):
    if request.user.is_authenticated:
        user = Candidate.objects.filter(user_id=request.user)
        if len(user) == 0:
            messages.info(request, 'Please create your profile first!')
            return render(request, 'webapp/new_profile.html')
        user = Candidate.objects.filter(Q(user_id=request.user) & Q(Approval='No'))
        if len(user) != 0:
            event = Event.objects.all()
            candidates = Candidate.objects.filter(Approval='Yes').exclude(user_id=request.user).order_by('-candidate_id')[:10]
            messages.info(request, 'Your profile is not approved yet. It takes 48 to 72 hours after creating profile!')
            return render(request, 'webapp/canhome.html', {'events': event, 'candidates': candidates})
        else:
            user = Candidate.objects.get(user_id=request.user)
            approved = Candidate.objects.filter(Approval='Yes')
            candidates = approved.exclude(Gender=user.Gender)
            return render(request, 'webapp/search.html', {'candidates': candidates})
    else:
        return render(request, 'webapp/home.html')


# search in whole data
def can_search(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            name_id = request.POST.get('name_id')
            approved = Candidate.objects.filter(Approval='Yes')
            find_one = approved.filter(candidate_id__icontains=name_id)
            if len(find_one) == 0:
                find_two = approved.filter(Name__icontains=name_id)
                if len(find_two) == 0:
                    user = Candidate.objects.get(user_id=request.user)
                    candidates = approved.exclude(Gender=user.Gender)
                    messages.info(request, 'Please enter valid ID or Name')
                    return render(request, 'webapp/search.html', {'candidates': candidates})
                else:
                    return render(request, 'webapp/search.html', {'candidates': find_two})
            else:
                return render(request, 'webapp/search.html', {'candidates': find_one})
        else:
            return render(request, 'webapp/home.html')
    else:
        messages.info(request, 'Login required!')
        return render(request, 'webapp/login.html')


# view profile of other candidate
def view_profile(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            user = Candidate.objects.filter(user_id=request.user)
            user1 = Candidate.objects.filter(Approval='No')
            user1 = user1.filter(user_id=request.user)
            if len(user) == 0:
                event = Event.objects.all()
                candidates = Candidate.objects.filter(Approval='Yes').exclude(user_id=request.user).order_by('-candidate_id')[:10]
                messages.info(request,
                              'Please create your profile first!')
                return render(request, 'webapp/canhome.html', {'events': event, 'candidates': candidates})
            if len(user1) != 0:
                event = Event.objects.all()
                candidates = Candidate.objects.filter(Approval='Yes').exclude(user_id=request.user).order_by(
                    '-candidate_id')[:10]
                messages.info(request,
                              'Your profile is not approved yet. It takes 48 to 72 hours after creating profile!')
                return render(request, 'webapp/canhome.html', {'events': event, 'candidates': candidates})
            else:
                canview = request.POST.get('canview')
                candidates = Candidate.objects.filter(candidate_id=canview)
                seen = Seen.objects.create(profile=canview, user=request.user)
                seen.save()
                all_img = Gallary.objects.filter(user=canview)
                return render(request, 'webapp/viewprofile.html', {'candidates': candidates, 'all_img': all_img})
        else:
            return render(request, 'webapp/home.html')
    else:
        return render(request, 'webapp/home.html')


# for password reset
def password_reset(request):
    return render(request, 'webapp/password_reset.html')


# add to favorites from search
def favorite(request):
    if request.user.is_authenticated:
        user = Candidate.objects.get(user_id=request.user)
        approved = Candidate.objects.filter(Approval='Yes')
        candidates = approved.exclude(Gender=user.Gender)
        if request.method == 'POST':
            fav = request.POST.get('favorit')
            rec = Favorite.objects.filter(Q(Profile=fav) & Q(user=request.user))
            if len(rec) == 0:
                add_fav = Favorite.objects.create(Profile=fav, user=request.user)
                add_fav.save()
                messages.info(request, "Added to favorites!")
                return render(request, 'webapp/search.html', {'candidates': candidates})
            else:
                messages.info(request, "Already added to favorites...")
                return render(request, 'webapp/search.html', {'candidates': candidates})
        else:
            return render(request, 'webapp/home.html')
    else:
        messages.info(request, 'Login required!')
        return render(request, 'webapp/login.html')


# add to favorites from user profile
def favorite_profile(request):
    if request.method == 'POST':
        fav = request.POST.get('canview')
        candidates = Candidate.objects.filter(candidate_id=fav)
        rec = Favorite.objects.filter(Q(Profile=fav) & Q(user=request.user))
        if len(rec) == 0:
            add_fav = Favorite.objects.create(Profile=fav, user=request.user)
            add_fav.save()
            messages.info(request, "Added to favorites!")
            return render(request, 'webapp/viewprofile.html', {'candidates': candidates})
        else:
            messages.info(request, "Already added to favorites...")
            return render(request, 'webapp/viewprofile.html', {'candidates': candidates})
    else:
        return render(request, 'webapp/home.html')


# show all favorites
def favorites(request):
    if request.user.is_authenticated:
        all_favs = Candidate.objects.filter(candidate_id__in=Favorite.objects.filter(user=request.user).values('Profile'))
        return render(request, 'webapp/favorite.html', {'all_favs': all_favs})
    else:
        messages.info(request, 'Login required!')
        return render(request, 'webapp/home.html')


# remove from favorites
def remove(request):
    if request.user.is_authenticated:
        user = Candidate.objects.filter(user_id=request.user)
        if len(user) == 0:
            messages.info(request, 'Please create your profile!')
            return render(request, 'webapp/new_profile.html')
        else:
            if request.method == 'POST':
                this = request.POST.get('this')
                to_remove = Favorite.objects.get(user=request.user, Profile=this)
                to_remove.delete()
                all_favs = Candidate.objects.filter(
                    candidate_id__in=Favorite.objects.filter(user=request.user).values('Profile'))
                return render(request, 'webapp/favorite.html', {'all_favs': all_favs})
            else:
                return render(request, 'webapp/home.html')
    else:
        messages.info(request, 'Login required!')
        return render(request, 'webapp/home.html')


# move to upcoming events page
def events(request):
    evento = Event.objects.all()
    return render(request, 'webapp/events.html', {'evento': evento})


# enroll for the event
def event_enroll(request):
    if request.user.is_authenticated:
        all_event = Event.objects.all()
        user1 = Candidate.objects.filter(user_id=request.user)
        if len(user1) == 0:
            messages.info(request, 'Please create your profile!')
            return render(request, 'webapp/new_profile.html')
        user = Candidate.objects.filter(Q(user_id=request.user) & Q(Approval='No'))
        if len(user) != 0:
            event = Event.objects.all()
            candidates = Candidate.objects.filter(Approval='Yes').exclude(user_id=request.user).order_by('-candidate_id')[:10]
            messages.info(request,
                              'Your profile is not approved yet. It takes 48 to 72 hours after creating profile!')
            return render(request, 'webapp/canhome.html', {'events': event, 'candidates': candidates})
        else:
            if request.method == 'POST':
                eventname = request.POST.get('eventname')
                evento = Event.objects.get(Name=eventname)
                user = Event_enroll.objects.filter(
                    (Q(user=request.user) & Q(Name=eventname)) | (Q(Name=eventname) & Q(user=request.user)))
                if len(user) == 0:
                    user = Candidate.objects.get(user_id=request.user)
                    reg = Event_enroll.objects.create(Name=evento.Name, user=request.user, vid=user.candidate_id,
                                                      Person_name=user.Name, Contact=user.Contact_1)
                    reg.save()
                    myevents = Event.objects.filter(Name__in=Event_enroll.objects.filter(user=request.user).values('Name'))
                    messages.info(request, "Enrolled for the event!")
                    return render(request, 'webapp/myevents.html', {'myevents': myevents})
                else:
                    messages.info(request, "You have already enrolled for this event.")
                    return render(request, 'webapp/events.html', {'evento': all_event})
            else:
                return render(request, 'webapp/home.html')
    else:
        messages.info(request, 'Login required!')
        return render(request, 'webapp/home.html')


# move to registered events page
def myevents(request):
    if request.user.is_authenticated:
        myevents = Event.objects.filter(Name__in=Event_enroll.objects.filter(user=request.user).values('Name'))
        return render(request, 'webapp/myevents.html', {'myevents': myevents})
    else:
        return render(request, 'webapp/home.html')


# move to event details page
def event_detail(request):
    if request.user.is_authenticated:
        eventname = request.POST.get('eventname')
        evento = Event.objects.filter(Name=eventname)
        candidates = Candidate.objects.filter(
            candidate_id__in=Event_enroll.objects.filter(Name=eventname).values('vid'))
        return render(request, 'webapp/event_page.html', {'candidates': candidates, 'evento': evento})
    else:
        return render(request, 'webapp/home.html')


# search in event
def event_cansearch(request):
    if request.user.is_authenticated:
        eventname = request.POST.get('eventname')
        name_id = request.POST.get('name_id')
        evento = Event.objects.filter(Name=eventname)
        candidates = Candidate.objects.filter(
            candidate_id__in=Event_enroll.objects.filter(Name=eventname).values('vid'))

        find_one = Candidate.objects.filter(
            candidate_id__in=Event_enroll.objects.filter(Q(Name=eventname) & Q(vid__icontains=name_id)).values('vid'))

        if len(find_one) == 0:
            find_two = Candidate.objects.filter(Name__icontains=Event_enroll.objects.filter(
                Q(Name=eventname) & Q(Person_name__icontains=name_id)).values('Person_name'))
            if len(find_two) == 0:
                messages.info(request, 'Please enter correct details!')
                return render(request, 'webapp/event_page.html', {'evento': evento, 'candidates': candidates})
            else:
                return render(request, 'webapp/event_page.html', {'candidates': find_two})
        else:
            return render(request, 'webapp/event_page.html', {'candidates': find_one})
    else:
        messages.info(request, 'Login required!')
        return render(request, 'webapp/home.html')


# Notifications for user
def notification(request):
    if request.user.is_authenticated:
        user = Candidate.objects.filter(user_id=request.user)
        if len(user) == 0:
            messages.info(request, 'Please create yout profile!')
            return render(request, 'webapp/new_profile.html')
        user = Candidate.objects.filter(Q(user_id=request.user) & Q(Approval='Yes'))
        if len(user) == 0:
            messages.info(request, 'Your profile is not approved yet!')
            return render(request, 'webapp/notifications.html')
        else:
            user = Candidate.objects.get(user_id=request.user)
            notify = Candidate.objects.filter(user_id__in=Favorite.objects.filter(Profile=user.candidate_id).values('user'))
            seen = Candidate.objects.filter(user_id__in=Seen.objects.filter(profile=user.candidate_id).values('user'))
            return render(request, 'webapp/notifications.html', {'notify': notify, 'seen': seen})
    else:
        return render(request, 'webapp/home.html')


# user gallery
def gallery(request):
    if request.user.is_authenticated:
        user1 = Candidate.objects.filter(user_id=request.user)
        if len(user1) == 0:
            messages.info(request, 'Please create your profile!')
            return render(request, 'webapp/new_profile.html')
        else:
            user1 = Candidate.objects.get(user_id=request.user)
            all_img = Gallary.objects.filter(user=user1.candidate_id)
            return render(request, 'webapp/gallery.html', {'all_img': all_img})
    else:
        messages.info(request, 'Login required!')
        return render(request, 'webapp/home.html')


# delete image from gallery
def delete_img(request):
    if request.user.is_authenticated:
        user1 = Candidate.objects.get(user_id=request.user)
        all_img = Gallary.objects.filter(user=user1.candidate_id)
        if len(all_img) == 0:
            return render(request, 'webapp/gallery.html', {'all_img': all_img})
        else:
            img = request.POST.get('image')
            if len(img) == 0:
                return render(request, 'webapp/gallery.html', {'all_img': all_img})
            else:
                del_img = Gallary.objects.get(Q(user=user1.candidate_id) & Q(images=img))
                del_img.delete()
                all_img = Gallary.objects.filter(user=user1.candidate_id)
                return render(request, 'webapp/gallery.html', {'all_img': all_img})
    else:
        messages.info(request, 'Login required!')
        return redirect('/')


# recommendation for matches
def matches(request):
    if request.user.is_authenticated:
        user = Candidate.objects.filter(user_id=request.user)
        if len(user) == 0:
            messages.info(request, 'Please create your profile!')
            return render(request, 'webapp/new_profile.html')
        user = Candidate.objects.filter(Q(user_id=request.user) & Q(Approval='Yes'))
        if len(user) == 0:
            messages.info(request, 'Your profile is not approved yet!')
            return render(request, 'webapp/matches.html')
        else:
            user = Candidate.objects.get(user_id=request.user)
            approved = Candidate.objects.filter(Approval='Yes')
            rec1 = approved.filter(Height__gte=user.Partner_height).exclude(Gender=user.Gender)
            rec = rec1.filter(Q(City__icontains=user.Preffered_city) | Q(Annual_income__icontains=user.Partner_income))
            if len(rec) == 0:
                rec = rec1
            fav = Favorite.objects.filter(user=request.user)

            if len(fav) != 0:
                data1 = Candidate.objects.all().exclude(Gender=user.Gender)
                if len(data1) == 0:
                    return render(request, 'webapp/matches.html', {'rec': rec})
                else:
                    datadf = pd.DataFrame.from_records(data1.values())
                    datadf['About'] = datadf['About'].fillna(' ')
                    tfv = TfidfVectorizer(min_df=1, max_features=None, strip_accents='unicode',
                                          analyzer='word', token_pattern=r'\w{1,}', ngram_range=(1, 3),
                                          stop_words='english')
                    tfv_matrix = tfv.fit_transform(datadf['About'])
                    sig = sigmoid_kernel(tfv_matrix, tfv_matrix)
                    indices = pd.Series(datadf.index, index=datadf['candidate_id']).drop_duplicates()
                    user = request.user
                    approved = Candidate.objects.filter(Approval='Yes')
                    t_user = approved.filter(candidate_id__in=Favorite.objects.filter(user=user).values('Profile'))[0]
                    get_user = t_user.candidate_id

                    idx = indices[get_user]
                    sig_scores = list(enumerate(sig[idx]))
                    sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
                    sig_scores = sig_scores[1:3]
                    can_indices = [i[0] for i in sig_scores]
                    ans = datadf['candidate_id'].iloc[can_indices]
                    cands = ans.values
                    approved = Candidate.objects.filter(Approval='Yes')
                    rec2 = approved.filter(candidate_id__in=[i for i in cands])
                    rec3 = rec.exclude(candidate_id__in=[i for i in cands])
                    return render(request, 'webapp/matches.html', {'rec': rec3, 'rec2': rec2})
            else:

                return render(request, 'webapp/matches.html', {'rec': rec})
    else:
        messages.info(request, 'Login required!')
        return render(request, 'webapp/home.html')


# export/download pdf of profile
def export_profile(request):
    if request.user.is_authenticated:
        canview = request.POST.get('canview')
        data = Candidate.objects.filter(candidate_id=canview)
        template_name = 'webapp/pdf.html'
        context = {'candidates': data}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="UserProfile.pdf"'
        template = get_template(template_name)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response
    else:
        return render(request, 'webapp/home.html')


# contact us at dashboard
def contact(request):
    return render(request, 'webapp/contact.html')


# feedback by user
def feedback(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            feed = request.POST.get('feed')
            suggest = request.POST.get('Suggestion')
            star = request.POST.get('star')
            if star is None:
                star = 1
                feed_obj = Feedback.objects.create(user=request.user, Feed=feed, Suggestion=suggest, Star=star)
                feed_obj.save()
                events = Event.objects.all()
                candidates = Candidate.objects.filter(Approval='Yes').exclude(user_id=request.user).order_by('-candidate_id')[:10]
                messages.info(request, "Feedback saved successfully!")
                return render(request, 'webapp/canhome.html', {'events': events, 'candidates': candidates})
        else:
            return render(request, 'webapp/feedback.html')
    else:
        return render(request, 'webapp/home.html')


# upload photos in gallery
def file_upload(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            user1 = Candidate.objects.filter(user_id=request.user)
            if len(user1) == 0:
                messages.info(request, 'Please create your profile!')
                return render(request, 'webapp/new_profile.html')
            else:
                user1 = Candidate.objects.get(user_id=request.user)
                all_img = Gallary.objects.filter(user=user1.candidate_id)
                user = user1.candidate_id
                user_id = request.user
                if len(request.FILES) == 0:
                    messages.info(request, 'Please select image to upload!')
                    return render(request, 'webapp/gallery.html', {'all_img': all_img})
                else:
                    images = request.FILES['uploadfoles']

                    img_num = Gallary.objects.filter(user_id=user_id)
                    if img_num.count() == 3:
                        messages.info(request, 'Maximum 3 photos can be added.')
                        return render(request, 'webapp/gallery.html', {'all_img': all_img})
                    else:
                        img_obj = Gallary.objects.create(user=user, user_id=user_id, images=images)
                        img_obj.save()
                        return render(request, 'webapp/gallery.html', {'all_img': all_img})
    else:
        messages.info(request, 'Login required!')
        return render(request, 'webapp/home.html')


# list of non approved users
@staff_member_required
def approval(request):
    var = Candidate.objects.filter(Approval='No')
    return render(request, 'webapp/approval.html', {'var': var})


# user profile to approve
def update_approval(request):
    if request.method == 'POST':
        prof = request.POST.get('profile')
        user = Candidate.objects.filter(candidate_id=prof)
        return render(request, 'webapp/approve.html', {'user': user})


# approval of user
def user_approve(request):
    if request.method == 'POST':
        user = request.POST.get('getuser')
        candidate = Candidate.objects.get(candidate_id=user)

        iprofile_pic = candidate.Profile_pic
        if len(request.FILES) != 0:
            iprofile_pic = request.FILES['picture']

        iname = request.POST.get('Name')
        if len(request.POST.get('Name')) == 0:
            iname = candidate.Name
        igender = request.POST.get('Gender')
        if len(request.POST.get('Gender')) == 0:
            igender = candidate.Gender
        idob = request.POST.get('Dob')
        if len(request.POST.get('Dob')) == 0:
            idob = candidate.DOB
        ioccupation_type = request.POST.get('Occupation_type')
        if len(request.POST.get('Occupation_type')) == 0:
            ioccupation_type = candidate.Occupation_type
        ioccupation_detail = request.POST.get('Occupation_detail')
        if len(request.POST.get('Occupation_detail')) == 0:
            ioccupation_detail = candidate.Occupation_detail
        ieducation_title = request.POST.get('Education_title')
        if len(request.POST.get('Education_title')) == 0:
            ieducation_title = candidate.Education_title
        ieducation_area = request.POST.get('Education_area')
        if len(request.POST.get('Education_area')) == 0:
            ieducation_area = candidate.Education_area
        ihobby = request.POST.get('Hobby')
        if len(request.POST.get('Hobby')) == 0:
            ihobby = candidate.Hobby
        iabout = request.POST.get('About')
        if len(request.POST.get('About')) == 0:
            iabout = candidate.About
        imarital_st = request.POST.get('Marital_st')
        if len(request.POST.get('Marital_st')) == 0:
            imarital_st = candidate.Marital_st
        iheight = request.POST.get('Height')
        if len(request.POST.get('Height')) == 0:
            iheight = candidate.Height
        iblood_group = request.POST.get('Blood_group')
        if len(request.POST.get('Blood_group')) == 0:
            iblood_group = candidate.Blood_group
        ibirth_name = request.POST.get('Birth_name')
        if len(request.POST.get('Birth_name')) == 0:
            ibirth_name = candidate.Birth_name
        ibirth_time = request.POST.get('Birth_time')
        if len(request.POST.get('Birth_time')) == 0:
            ibirth_time = candidate.Birth_time
        ibirth_place = request.POST.get('Birth_place')
        if len(request.POST.get('Birth_place')) == 0:
            ibirth_place = candidate.Birth_place
        imother_tong = request.POST.get('Mother_tong')
        if len(request.POST.get('Mother_tong')) == 0:
            imother_tong = candidate.Mother_tong
        icomplexion = request.POST.get('Complexion')
        if len(request.POST.get('Complexion')) == 0:
            icomplexion = candidate.Complexion
        iannual_income = request.POST.get('Annual_income')
        if len(request.POST.get('Annual_income')) == 0:
            iannual_income = candidate.Annual_income
        ifirst_gotra = request.POST.get('First_gotra')
        if len(request.POST.get('First_gotra')) == 0:
            ifirst_gotra = candidate.First_gotra
        isecond_gotra = request.POST.get('Second_gotra')
        if len(request.POST.get('Second_gotra')) == 0:
            isecond_gotra = candidate.Second_gotra
        iaddress = request.POST.get('Address')
        if len(request.POST.get('Address')) == 0:
            iaddress = candidate.Address
        icity = request.POST.get('City')
        if len(request.POST.get('City')) == 0:
            icity = candidate.City
        ipostal_code = request.POST.get('Postal_code')
        if len(request.POST.get('Postal_code')) == 0:
            ipostal_code = candidate.Postal_code
        icountry = request.POST.get('Country')
        if len(request.POST.get('Country')) == 0:
            icountry = candidate.Country
        iemail = request.POST.get('Email')
        if len(request.POST.get('Email')) == 0:
            iemail = candidate.Email
        icontact_1 = request.POST.get('contact_1')
        if len(request.POST.get('contact_1')) == 0:
            icontact_1 = candidate.Contact_1
        icontact_1_name = request.POST.get('contact1_name')
        if len(request.POST.get('contact1_name')) == 0:
            icontact_1_name = candidate.Contact_1_name
        icontact_1_relation = request.POST.get('contact1_rel')
        if len(request.POST.get('contact1_rel')) == 0:
            icontact_1_relation = candidate.Contact_1_relation
        icontact_2 = request.POST.get('contact_2')
        if len(request.POST.get('contact_2')) == 0:
            icontact_2 = candidate.Contact_2
        icontact_2_name = request.POST.get('contact2_name')
        if len(request.POST.get('contact2_name')) == 0:
            icontact_2_name = candidate.Contact_2_name
        icontact_2_relation = request.POST.get('contact2_rel')
        if len(request.POST.get('contact2_rel')) == 0:
            icontact_2_relation = candidate.Contact_2_relation
        ifamily = request.POST.get('Family_type')
        if len(request.POST.get('Family_type')) == 0:
            ifamily = candidate.Family
        ifathers_name = request.POST.get('fathers_name')
        if len(request.POST.get('fathers_name')) == 0:
            ifathers_name = candidate.Fathers_name
        ifathers_occupation = request.POST.get('father_occupation')
        if len(request.POST.get('father_occupation')) == 0:
            ifathers_occupation = candidate.Fathers_occupation
        imothers_name = request.POST.get('mother_name')
        if len(request.POST.get('mother_name')) == 0:
            imothers_name = candidate.Mothers_name
        imothers_occupation = request.POST.get('mother_occupation')
        if len(request.POST.get('mother_occupation')) == 0:
            imothers_occupation = candidate.Mothers_occupation
        inumber_brother = request.POST.get('number_brother')
        if len(request.POST.get('number_brother')) == 0:
            inumber_brother = candidate.Number_brother
        ibrother_detail = request.POST.get('brother_detail')
        if len(request.POST.get('brother_detail')) == 0:
            ibrother_detail = candidate.Brother_detail
        inumber_sister = request.POST.get('number_sister')
        if len(request.POST.get('number_sister')) == 0:
            inumber_sister = candidate.Number_sister
        isister_detail = request.POST.get('sister_detail')
        if len(request.POST.get('sister_detail')) == 0:
            isister_detail = candidate.Sister_detail
        ipartner_compx = request.POST.get('partner_compx')
        if len(request.POST.get('partner_compx')) == 0:
            ipartner_compx = candidate.Partner_compx
        ipartner_occupation = request.POST.get('partner_occupation')
        if len(request.POST.get('partner_occupation')) == 0:
            ipartner_occupation = candidate.Partner_occupation
        ipreffered_city = request.POST.get('preffered_city')
        if len(request.POST.get('preffered_city')) == 0:
            ipreffered_city = candidate.Preffered_city
        ipartner_agefrom = request.POST.get('age_from')
        if len(request.POST.get('age_from')) == 0:
            ipartner_agefrom = candidate.Partner_agefrom
        iparnter_ageto = request.POST.get('age_to')
        if len(request.POST.get('age_to')) == 0:
            iparnter_ageto = candidate.Partner_ageto
        ipartner_height = request.POST.get('partner_height')
        if len(request.POST.get('partner_height')) == 0:
            ipartner_height = candidate.Partner_height
        ipartner_income = request.POST.get('partner_income')
        if len(request.POST.get('partner_income')) == 0:
            ipartner_income = candidate.Partner_income
        ipartner_qualification = request.POST.get('partner_qualification')
        if len(request.POST.get('partner_qualification')) == 0:
            ipartner_qualification = candidate.Partner_qualification
        iapproval = request.POST.get('Approval')
        if len(request.POST.get('Approval')) == 0:
            iapproval = candidate.Approval
        imember = request.POST.get('Member_type')
        if len(request.POST.get('Member_type')) == 0:
            imember = candidate.Member

        candidate.Profile_pic = iprofile_pic
        candidate.Name = iname
        candidate.Gender = igender
        candidate.DOB = idob
        candidate.Occupation_type = ioccupation_type
        candidate.Occupation_detail = ioccupation_detail
        candidate.Education_title = ieducation_title
        candidate.Education_area = ieducation_area
        candidate.Hobby = ihobby
        candidate.About = iabout
        candidate.Marital_st = imarital_st
        candidate.Height = iheight
        candidate.Blood_group = iblood_group
        candidate.Birth_name = ibirth_name
        candidate.Birth_place = ibirth_place
        candidate.Birth_time = ibirth_time
        candidate.Mother_tong = imother_tong
        candidate.Complexion = icomplexion
        candidate.Annual_income = iannual_income
        candidate.First_gotra = ifirst_gotra
        candidate.Second_gotra = isecond_gotra
        candidate.Address = iaddress
        candidate.City = icity
        candidate.Postal_code = ipostal_code
        candidate.Country = icountry
        candidate.Email = iemail
        candidate.Contact_1 = icontact_1
        candidate.Contact_1_name = icontact_1_name
        candidate.Contact_1_relation = icontact_1_relation
        candidate.Contact_2 = icontact_2
        candidate.Contact_2_name = icontact_2_name
        candidate.Contact_2_relation = icontact_2_relation
        candidate.Family = ifamily
        candidate.Fathers_name = ifathers_name
        candidate.Fathers_occupation = ifathers_occupation
        candidate.Mothers_name = imothers_name
        candidate.Mothers_occupation = imothers_occupation
        candidate.Number_brother = inumber_brother
        candidate.Brother_detail = ibrother_detail
        candidate.Number_sister = inumber_sister
        candidate.Sister_detail = isister_detail
        candidate.Partner_compx = ipartner_compx
        candidate.Partner_occupation = ipartner_occupation
        candidate.Preffered_city = ipreffered_city
        candidate.Partner_agefrom = ipartner_agefrom
        candidate.Partner_ageto = iparnter_ageto
        candidate.Partner_height = ipartner_height
        candidate.Partner_income = ipartner_income
        candidate.Partner_qualification = ipartner_qualification
        candidate.Approval = iapproval
        candidate.Member = imember

        candidate.save()
        approval_mail(iemail)
        messages.info(request, 'Candidate approved...')
        var = Candidate.objects.filter(Approval='No')
        return render(request, 'webapp/approval.html', {'var': var})
    else:
        return render(request, 'webapp/home.html')


# approval mail to candidate
def approval_mail(iemail):
    subject = 'Your Vivah profile is now approved'
    message = f'Hi, Your vivah profile is now approved and active. You can enjoy the site features!' \
              f'https://vivahtest.herokuapp.com/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [iemail]
    send_mail(subject, message, email_from, recipient_list)


# go to ebook generation
def forebook(request):
    if request.method == 'POST':
        event = Event.objects.all()
        return render(request, 'webapp/admin.html', {'event': event})
    else:
        return render(request, 'webapp/home.html')


# generate ebook
def generate(request):
    if request.method == 'POST':
        eventname = request.POST.get('eventname')
        candidates = Candidate.objects.filter(
            candidate_id__in=Event_enroll.objects.filter(Name=eventname).values('vid'))
        mcandidates = candidates.filter(Gender='Male')
        fcandidates = candidates.filter(Gender='Female')
        event = Event.objects.filter(Name=eventname)
        template_name = 'webapp/ebook.html'
        context = {'mcandidates': mcandidates, 'fcandidates': fcandidates, 'event': event}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="EventBook.pdf"'
        template = get_template(template_name)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error')
        return response
    else:
        return render(request, 'webapp/home.html')