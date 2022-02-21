from django.shortcuts import render,redirect
from .models import Contact,User,Product,Wishlist,Cart,Transaction
from django.conf import settings
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
import random
from django.core.mail import send_mail

def validate_email(request):
	email=request.GET.get('email')
	data={
	   'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)

# Create your views here.
def index(request):
	return render(request,'index.html')

def seller_index(request):
	return render(request,'seller_index.html')

def contact(request):
	if request.method=="POST":
		Contact.objects.create(
			name=request.POST['name'],
			email=request.POST['email'],
			phone=request.POST['phone'],
			message=request.POST['message']
			)
		msg="Contact Saved Successfully"
		return render(request,'contact.html',{'msg':msg})
	else:
		return render(request,'contact.html')

def signup(request):
	if request.method=="POST":
		try:
			user=User.object.get(email=request.POST['email'])
			msg="Email Allready Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
					usertype=request.POST['usertype'],
	                fname=request.POST['fname'],
			        lname=request.POST['lname'],
			        email=request.POST['email'],
			        mobile=request.POST['mobile'],
			        address=request.POST['address'],
			        password=request.POST['password']
			        )
				

				msg="Sign Up Successfully"
				return render(request,'login.html',{'msg':msg})
			else:
			    msg="Password & Confirm Password Does Not Matched"
			    return render(request,'signup.html')
	else:
		return render(request,'signup.html')

def login(request):
	if request.method=="POST":
		try:
		    user=User.objects.get(
			    email=request.POST['email'],
			    password=request.POST['password'],
			    )
		    if user.usertype=="user":
		    	request.session['email']=user.email
		    	request.session['fname']=user.fname
		    	wishlists=Wishlist.objects.filter(user=user)
		    	request.session['wishlist_count']=len(wishlists)
		    	carts=Cart.objects.filter(user=user,status=False)
		    	request.session['cart_count']=len(carts)
		    	return render(request,'index.html')
		    else:
		    	request.session['email']=user.email
		    	request.session['fname']=user.fname
		    	return render(request,'seller_index.html')
		except:
			msg="Email & Password Is Incorrect"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')	

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Matched"
				return render(request,'change_password.html',{'msg':msg})
		else:
			msg="Old Password Is Incorrect"
			return render(request,'change_password.html',{'msg':msg})
	else:
		return render(request,'change_password.html')

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			subject = 'OTP For Forgot Password'
			otp=random.randint(1000,9999)
			message= 'OTP For Forgot Password Is '+str(otp)						
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email, ]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'verify_otp.html',{'otp':otp,'email':user.email})
		except:
			msg="Email Does Not Exists"	
			return render(request,'forgot_password.html',{'msg':msg})
	else:
		return render(request,'forgot_password.html')

def verify_otp(request): 
	otp=request.POST['otp']
	uotp=request.POST['uotp']
	email=request.POST['email']

	if otp==uotp:
		return render(request,'new_password.html',{'email':email})
	else:
		msg="Invalid OTP"
		return render(request,'verify_otp.html',{'otp':otp,'email':email,'msg':msg})
		
def new_password(request):
	email=request.POST['email']
	new_password=request.POST['new_password']
	cnew_password=request.POST['cnew_password']

	if new_password==cnew_password:
		user=User.objects.get(email=email)
		user.password=new_password
		user.save()
		msg="Password Updated Successfully"
		return render(request,'login.html',{'msg':msg})
	else:
	    msg="New Password And Confirm New Password Does Not Matched"
	    return render(request,'new_password.html',{'email':email,'msg':msg})


def seller_change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Matched"
				return render(request,'seller_change_password.html',{'msg':msg})
		else:
			msg="Old Password Is Incorrect"
			return render(request,'seller_change_password.html',{'msg':msg})
	else:
		return render(request,'seller_change_password.html')	

	
def seller_add_product(request):
	if request.method=="POST":
		seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
			seller=seller,
			product_category=request.POST['product_category'],
			product_model=request.POST['product_model'],
			product_price=request.POST['product_price'],
			product_desc=request.POST['product_desc'],
			product_image=request.FILES['product_image'],
			)
		msg="Product Updated Successfully"
		return render(request,'seller_add_product.html',{'msg':msg})
	else:
		return render(request,'seller_add_product.html')

def seller_view_product(request):
	seller=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=seller)
	return render(request,'seller_view_product.html',{'products':products})

def seller_edit_product(request,pk):
    product=Product.objects.get(pk=pk)
    if request.method=="POST":
    	product.product_category=request.POST['product_category']
    	product.product_model=request.POST['product_model']
    	product.product_price=int(request.POST['product_price'])
    	product.product_desc=request.POST['product_desc']
    	try:
    		product.product_image=request.FILES['product_image']
    	except:
    		pass
    	product.save()
    	msg="Product Updated Successfully"
    	return render(request,'seller_edit_product.html',{'product':product,'msg':msg})
    else:
    	return render(request,'seller_edit_product.html',{'product':product})

def seller_delete_product(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('seller_view_product')

def product(request):
	products=Product.objects.all()
	return render(request,'product.html',{'products':products}) 	

def user_product_detail(request,pk):
	product=Product.objects.get(pk=pk)
	wishlist_flag=False
	cart_flag=False
	user=User.objects.get(email=request.session['email'])
	try:
	    Wishlist.objects.get(user=user,product=product)
	    wishlist_flag=True
	except:
		pass
	try:
	    Cart.objects.get(user=user,product=product,status=False)
	    cart_flag=True
	except:
		pass
	
	return render(request,'user_product_detail.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(
        user=user,
        product=product
		)
	return redirect('wishlist')

def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('wishlist')

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'wishlists':wishlists})

def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(
        user=user,
        product=product,
        product_price=product.product_price,
        total_price=product.product_price
		)
	return redirect('cart')

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product,status=False)
	cart.delete()
	return redirect('cart')

def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,status=False)
	for i in carts:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def change_qty(request):
	cid=request.POST['cid']
	product_qty=request.POST['product_qty']
	cart=Cart.objects.get(pk=cid,status=False)
	cart.product_qty=product_qty
	cart.total_price=int(product_qty)*int(cart.product_price)
	cart.save()
	return redirect('cart')

def initiate_payment(request):
	user=User.objects.get(email=request.session['email'])
	try:
		amount = int(request.POST['amount'])
	except:
		return render(request, 'cart.html', context={'error': 'Wrong Accound Details or amount'})

	transaction = Transaction.objects.create(made_by=user,amount=amount)
	transaction.save()
	merchant_key = settings.PAYTM_SECRET_KEY
	params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str("reematest97@gmail.com")),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
        )
	paytm_params = dict(params)
	checksum = generate_checksum(paytm_params, merchant_key)
    
	transaction.checksum = checksum
	transaction.save()
	carts=Cart.objects.filter(user=user)
	for i in carts:
		i.status=True
		i.save()
	carts=Cart.objects.filter(user=user,status=False)
	request.session['cart_count']=len(carts)
	paytm_params['CHECKSUMHASH'] = checksum
	print('SENT: ', checksum)
	return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,status=True)
	return render(request,'myorder.html',{'carts':carts})







