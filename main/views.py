from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import *
from user_login.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from cashback.tasks import SendOfferEmail
from .forms import *



def index(request):
    categories = Category.objects.all()
    offers = Offer.objects.filter(hot=1)
    template = loader.get_template('main/hot_offers.html')
    results = template.render({'offers':offers}, request)
    return render(request, 'main/index.html', {'categories': categories, 'results':results})

def offers(request):
    company_ids = request.POST.getlist('comp_filter[]')
    category_ids = request.POST.getlist('cat_filter[]')
    if len(company_ids)==0 and len(category_ids)>=1:
        offers = Offer.objects.filter(category__id__in=category_ids)
    elif len(company_ids)==1 and len(category_ids)==0:
        offers = Offer.objects.filter(company__id__in=company_ids)
    else:
        offers = Offer.objects.filter(company__id__in=company_ids).filter(category__id__in=category_ids)
    if request.user.is_superuser:
        return render(request, 'main/emailoffersform.html', {'offers':offers})
    else:
        return render(request, 'main/offers.html', {'offers': offers})
    

def company(request,comp_name):
    categories = Category.objects.all()
    offers = Offer.objects.filter(company__name__iexact=comp_name)
    template = loader.get_template('main/offers.html')
    results = template.render({'offers':offers}, request)
    comp_id = get_object_or_404(Company, name__iexact=comp_name).id
    return render(request,'main/offer_page.html', {'categories':categories, 'results':results, 'comp_id': comp_id})

def category(request, cat_name):
    companies = Company.objects.all()
    offers = Offer.objects.filter(category__name__iexact=cat_name)
    template = loader.get_template('main/offers.html')
    results = template.render({'offers':offers}, request)
    cat_id = get_object_or_404(Category, name__iexact=cat_name).id
    return render(request, 'main/offer_page.html', {'companies':companies, 'results':results, 'cat_id': cat_id})

@login_required
def shop(request, offer_id):
    offer = Offer.objects.get(id=offer_id)
    customer = request.user.customer;
    click = Click(user=customer, offer=offer)
    click.save()
    link = offer.url
    return HttpResponseRedirect('https://linksredirect.com/?pub_id=16923CL15205&subid='+str(click.id)+'&source=linkkit&url='+link)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def mailoffers(request):
    if(request.method=='POST'):
        offer_ids = request.POST.getlist('selected_offers[]')
        offers = Offer.objects.filter(id__in=offer_ids)
        category = offers[0].category
        template = loader.get_template('main/email_about_offers.html')
        result = template.render({'offers':offers},request)
        SendOfferEmail.delay(result, category)
        
    results = 'Please select a category from Filter.'
    categories = Category.objects.all()
    return render(request,'main/offer_page.html', {'categories':categories, 'results':results})

@login_required
def profile(request):
    customer = request.user.customer
    transactions = Transaction.objects.filter(user=customer)
    referrals = Customer.objects.filter(referee_code=customer.referral_code)
    categories = customer.categories.all()
    other_categories = Category.objects.exclude(pk__in=categories)
    return render(request, 'main/profile.html', {'customer': customer, 'transactions':transactions,
                                                 'referrals':referrals, 'categories':categories,
                                                 'other_categories':other_categories})

@login_required
def userSettings(request):
    customer = request.user.customer
    if(request.method=='POST'):
        form=UserSettingsForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            customer.phone = phone
            customer.email = email
            customer.save()
            print('user settings updated')
            
    return profile(request)

# not yet integrated with UI because UI needs change. This page should be entirely different.
@login_required
def changePassword(request):
    user = request.user
    customer = user.customer
    if(request.method=='POST'):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            confirm_passwrod = form.cleaned_data['confirm_password']
            if user.check_password(old_password) and new_password==confirm_password:
                user.set_password(new_password)
                user.save()
                
    return profile(request)
        
@login_required
def addBankDetails(request):
    customer = request.user.customer
    if(request.method=='POST'):
        form = BankDetailsForm(request.POST)
        if form.is_valid():
            account_name = form.cleaned_data['account_name']
            account_no = form.cleaned_data['account_no']
            ifsc = form.cleaned_data['ifsc']
            customer.account_name = account_name
            customer.account_no = account_no
            customer.ifsc = ifsc
            customer.save()
            
    return profile(request)

@login_required
def addPaytmDetails(request):
    customer = request.user.customer
    if(request.method=='POST'):
        form = PaytmDetailsForm(request.POST)
        if form.is_valid():
            paytm_name = form.cleaned_data['paytm_name']
            paytm_no = form.cleaned_data['paytm_no']
            customer.paytm_name = paytm_name
            customer.paytm_no = paytm_no
            customer.save()    
    return profile(request)

@login_required
def setCategoryPrefs(request):
    customer = request.user.customer
    if(request.method=='POST'):
        customer.categories.clear()
        for category_id in request.POST.getlist('categories[]'):
            category = Category.objects.get(id=category_id)
            customer.categories.add(category)
    return profile(request)

def contact(request):
    return render(request,'main/contact.html')

def terms(request):
    return render(request,'main/terms.html')
        
    




    

