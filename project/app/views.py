from django.shortcuts import render
from django.shortcuts import render,get_object_or_404
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, View
from .forms import *
import random
import string
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from coupon_app.validations import validate_coupon
from coupon_app.models import Coupon
from django.contrib.auth.models import User
from coupon_app.validations import validate_coupon
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count,Q
from .filters import *
from filter_and_pagination import FilterPagination
from django.core import serializers
from django.http import JsonResponse
from django.http import HttpResponseRedirect

def create_ref_code():
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(values):
	valid = True
	for field in values:
		if field == '':
			valid = False
	return valid

def home(request):
	about = About.objects.all()
	items = Item.objects.all()
	carousels = Carousel.objects.all()
	gallery = Gallery.objects.all()
	footer_link = Footer.objects.all()
	services = Services.objects.all()
	context = {'about':about, 'items':'items', 'carousels':carousels,'footer_link':footer_link,'services':services,
	'gallery':gallery}
	form = UserContactForm()
	if request.method == 'POST':
		form = UserContactForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data.get('email')
			message = form.cleaned_data.get('message')
			try:
				contact = Contact()
				contact.email = email
				contact.message = message
				contact.save()
				messages.success(request, "Your response has been recieved! We will contact you shortly")
				return redirect("/")

			except ObjectDoesNotExist:
				messages.info(request, "Please ensure to fill in valid details")
				return redirect("/")
	return render(request, 'app/home.html', context)

def kitchen(request):
	items = Item.objects.all()
	footer_link = Footer.objects.all()
	context = {'items':items,'footer_link':footer_link}
	return render(request,'app/kitchen.html',context)

def item_detail(request, pk):
	footer_link = Footer.objects.all()
	item = get_object_or_404(Item,id=pk)

	context = {'item':item,'footer_link':footer_link}
	return render(request, 'app/item-detail.html', context)

@login_required
def add_to_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
			item=item,
			user=request.user,
			ordered=False)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			if order_item.item.slug == "delivery":
				order_item.quantity = 1
				order_item.save()
				messages.info(request, "You can only add a delivery fee per order")
				return redirect("kitchen")
			else:
				order_item.quantity += 1
				order_item.save()
				messages.info(request,"This item quantity was updated")
				return redirect("kitchen")
		else:
			order.items.add(order_item)
			messages.info(request,"This item was added to cart")
			return redirect('kitchen')
	
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request,"This item was added to cart")
	return redirect('kitchen')

@login_required
def remove_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		# check if the order item is in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			order.items.remove(order_item)
			order_item.delete()
			messages.info(request, "This item was removed from your cart.")
			return redirect("kitchen")
		else:
			messages.info(request, "This item was not in your cart")
			return redirect("kitchen")
	else:
		messages.info(request, "You do not have an active order")
		return redirect("kitchen")

@login_required
def remove_single_item_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
				order.items.remove(order_item)
			messages.info(request, "This item quantity was updated.")
			return redirect("kitchen")
		else:
			messages.info(request, "This item was not in your cart")
			return redirect("kitchen")
	else:
		messages.info(request, "You do not have an active order")
		return redirect("kitchen")

@login_required
def cart(request):
	try:
		order = Order.objects.get(user=request.user, ordered=False)
		footer_link = Footer.objects.all()
		context = {'order':order,'footer_link':footer_link}
		return render(request, 'app/cart.html', context)
	except ObjectDoesNotExist:
		messages.info(request, "You do not have an active Order")
		return redirect("kitchen")

@login_required
def add_to_cart_page(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
			item=item,
			user=request.user,
			ordered=False)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request,"This item quantity was updated")
			return redirect("cart")
		else:
			order.items.add(order_item)
			messages.info(request,"This item was added to cart")
			return redirect('cart')
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request,"This item quantity was updated")
	return redirect('cart')

@login_required
def remove_from_cart_page(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		# check if the order item is in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			if order_item.item.slug == "delivery":
				order.items.remove(order_item)
				order_item.delete()
				messages.info(request, "Delivery has been removed from this order")
				return redirect("cart")
			else:
				order.items.remove(order_item)
				order_item.delete()
				messages.info(request, "This item was removed from your cart.")
				return redirect("cart")
		else:
			messages.info(request, "This item was not in your cart")
			return redirect("cart")
	else:
		messages.info(request, "You do not have an active order")
		return redirect("cart")

@login_required
def remove_single_item_from_cart_page(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
				order.items.remove(order_item)
			messages.info(request, "This item quantity was updated.")
			return redirect("cart")
		else:
			messages.info(request, "This item was not in your cart")
			return redirect("cart")
	else:
		messages.info(request, "You do not have an active order")
		return redirect("cart")

@login_required
def add_to_cart_item_detail_page(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
			item=item,
			user=request.user,
			ordered=False)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			if order_item.item.slug == "delivery":
				order_item.quantity = 1
				order_item.save()
				messages.info(request, "You can only add a delivery fee per order")
				return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
			else:
				order_item.quantity += 1
				order_item.save()
				messages.info(request,"This item quantity was updated")
				return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
		else:
			order.items.add(order_item)
			messages.info(request,"This item was added to cart")
			return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
	
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request,"This item was added to cart")
	return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

@login_required
def remove_from_cart_item_detail_page(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		# check if the order item is in the order
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			order.items.remove(order_item)
			order_item.delete()
			messages.info(request, "This item was removed from your cart.")
			return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
		else:
			messages.info(request, "This item was not in your cart")
			return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
	else:
		messages.info(request, "You do not have an active order")
		return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

class AddCouponView(LoginRequiredMixin, View):
	def post(self, *args, **kwargs):
		form = CouponForm(self.request.POST or None)
		if form.is_valid():
			try:
				code = form.cleaned_data.get('code')
				order = Order.objects.get(user=self.request.user,ordered=False)
				status = validate_coupon(coupon_code=code, user=self.request.user)
				if status['valid']:
					coupon = Coupon.objects.get(code=code)
					coupon.use_coupon(user=self.request.user)
					order.coupon = coupon
					order.save()
					messages.success(self.request, "Successfully added coupon")
				else:
					messages.warning(self.request, "This coupon does not exist")
				return redirect("checkout")

			except ObjectDoesNotExist:
				messages.warning(self.request, "The Coupon code is not valid")
				return redirect("checkout")
		else:
			messages.warning(self.request, "The Coupon code is not valid")
			return redirect("checkout")

class CheckoutView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			form = CheckoutForm()
			footer_link = Footer.objects.all()
			context={'order':order,'DISPLAY_COUPON_FORM': True,'form':form,'footer_link':footer_link,'couponform':CouponForm()}

			shipping_address_qs = Address.objects.filter(
				user =  self.request.user,
				default = True,
			)
			if shipping_address_qs.exists():
				context.update(
					{'default_delivery_address':shipping_address_qs[0]})

			return render(self.request, 'app/checkout.html',context)
		except ObjectDoesNotExist:
			messages.warning(self.request,"You do not have an active order")
			return redirect("kitchen")


	def post(self, *args, **kwargs):
		form = CheckoutForm(self.request.POST or None)
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			if form.is_valid():
				use_default_delivery = form.cleaned_data.get(
					'use_default_delivery')
				if use_default_delivery:
					address_qs = Address.objects.filter(
						user=self.request.user,
						default=True
					)
					if address_qs.exists():
						shipping_address = address_qs[0]
						order.street_address = shipping_address.street_address
						order.apartment_address = shipping_address.apartment_address
						order.city = shipping_address.city
						order.phone = shipping_address.phone

						order_items = order.items.all()
						order_items.update(ordered=True)
						for item in order_items:
							item.save()
						order.ordered = True
						order.status = "processing"
						order.ref_code = create_ref_code()
						order.save()
						messages.success(self.request, "Your Order was successfull")
						return redirect("/")
					else:
						messages.info(self.request, "No default address available")
						return redirect('checkout')
				else:
					street_address = form.cleaned_data.get('street_address')
					apartment_address = form.cleaned_data.get('apartment_address')
					phone = form.cleaned_data.get('phone')
					city = form.cleaned_data.get('city')

					if is_valid_form([street_address,apartment_address,city,phone]):
						shipping_address = Address(
							user=self.request.user,
							street_address=street_address,
							apartment_address=apartment_address,
							city = city,
							phone = phone
							)
						order.street_address = shipping_address.street_address
						order.apartment_address = shipping_address.apartment_address
						order.city = shipping_address.city
						order.phone = shipping_address.phone
						order.save()
						set_default_delivery = form.cleaned_data.get('set_default_delivery')
						if set_default_delivery:
							try:
								old_default_address = Address.objects.filter(user=self.request.user, default=True).update(default=False)
								shipping_address.default = True
								shipping_address.save()
							except ObjectDoesNotExist:
								shipping_address.default = True
								shipping_address.save()
						order_items = order.items.all()
						order_items.update(ordered=True)
						for item in order_items:
							item.save()
						order.ordered = True
						order.status = "processing"
						order.ref_code = create_ref_code()
						order.save()
						messages.success(self.request, "Your Order was successfull")
						return redirect("/")
					else:
						messages.info(self.request, "Please kindly fill in the required delivery address fields")
						return redirect("checkout")			
			else:
				print(form.errors)
				messages.info(self.request, "Please ensure to fill in valid details")
				return redirect("checkout")

		except ObjectDoesNotExist:
			messages.warning(self.request, "You currently do not have an active order")
			return redirect("kitchen")

@login_required
def dashboard(request, pk):
	customer = User.objects.get(id = pk)
	address = Address.objects.filter(user=request.user, default=True)
	footer_link = Footer.objects.all()
	orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	on_delivery = orders.filter(status = 'on delivery').count()
	delivered = orders.filter(status = 'delivered').count()
	cancelled = orders.filter(status = 'cancelled').count()
	total_orders = orders.count()
	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'on_delivery':on_delivery, 'delivered':delivered, 'cancelled':cancelled,
	'recent_orders':recent_orders,'footer_link':footer_link,'address':address,
	}
	if address.exists():
		context.update({'def_address':address[0]})

	return render(request, 'app/dashboard.html', context)


@login_required
def dash_profile(request, pk):
	customer = User.objects.get(id = pk)
	footer_link = Footer.objects.all()
	orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	on_delivery = orders.filter(status = 'on delivery').count()
	delivered = orders.filter(status = 'delivered').count()
	cancelled = orders.filter(status = 'cancelled').count()
	total_orders = orders.count()
	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'on_delivery':on_delivery, 'delivered':delivered, 'cancelled':cancelled,
	'recent_orders':recent_orders,'footer_link':footer_link
	}
	return render(request, 'app/dashboard-profile.html', context)

def is_valid_queryparam(param):
	return param != '' and param is not None

@login_required
def dash_order(request, pk):
	customer = User.objects.get(id = pk)
	orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	on_delivery = orders.filter(status = 'on delivery').count()
	delivered = orders.filter(status = 'delivered').count()
	cancelled = orders.filter(status = 'cancelled').count()
	footer_link = Footer.objects.all()
	total_orders = orders.count()
	form = OrderForm()
	form_filter = OrderFilterForm()

	paginator = Paginator(orders, 10)
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		paginated_queryset = paginator.page(page)
	except PageNotAnInteger:
		paginated_queryset = paginator.page(1)
	except EmptyPage:
		paginated_queryset = paginator.page(paginator.num_pages)

	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'on_delivery':on_delivery, 'delivered':delivered, 'cancelled':cancelled,
	'recent_orders':recent_orders,'queryset':paginated_queryset, 'page_request_var':page_request_var,
	'footer_link':footer_link,'form':form
	}
	
	if request.method == "GET":
		date_min = request.GET.get('date_min')
		date_max = request.GET.get('date_max')
		status = request.GET.get('status')

		if is_valid_queryparam(date_min):
			orders = orders.filter(ordered_date__gte=date_min)
		if is_valid_queryparam(date_max):
			orders = orders.filter(ordered_date__lte=date_max)
		
		if is_valid_queryparam(status) and status != 'Choose...':
			orders = orders.filter(status=status)
		paginator = Paginator(orders, 10)
		page_request_var = 'page'
		page = request.GET.get(page_request_var)
		try:
			paginated_queryset = paginator.page(page)
		except PageNotAnInteger:
			paginated_queryset = paginator.page(1)
		except EmptyPage:
			paginated_queryset = paginator.page(paginator.num_pages)
		context.update({'queryset':paginated_queryset})

	return render(request, 'app/dashboard-order.html', context)

@login_required
def address(request, pk):
	customer = User.objects.get(id = pk)
	addresses = Address.objects.filter(user=customer).distinct()
	orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	on_delivery = orders.filter(status = 'on delivery').count()
	delivered = orders.filter(status = 'delivered').count()
	cancelled = orders.filter(status = 'cancelled').count()
	footer_link = Footer.objects.all()
	total_orders = orders.count()

	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'on_delivery':on_delivery, 'delivered':delivered, 'cancelled':cancelled,
	'recent_orders':recent_orders,'footer_link':footer_link,'addresses':addresses
	}
	return render(request, 'app/address.html', context)

@login_required
def add_address(request, pk):
	customer = User.objects.get(id = pk)
	addresses = Address.objects.filter(user=customer)
	orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	on_delivery = orders.filter(status = 'on delivery').count()
	delivered = orders.filter(status = 'delivered').count()
	cancelled = orders.filter(status = 'cancelled').count()
	footer_link = Footer.objects.all()
	total_orders = orders.count()

	form = AddAddressForm()
	if request.method == 'POST':
		form = AddAddressForm(request.POST)
		if form.is_valid():
			street_address = form.cleaned_data.get('street_address')
			apartment_address = form.cleaned_data.get('apartment_address')
			city = form.cleaned_data.get('city')
			phone = form.cleaned_data.get('phone')
			try:
				address = Address()
				address.user = request.user
				address.street_address = street_address
				address.apartment_address = apartment_address
				address.city = city
				address.phone = phone
				address.save()
				messages.success(request, "New address added successfully!")
				return redirect("add-address",pk=pk)

			except ObjectDoesNotExist:
				messages.info(request, "Please ensure to fill in valid details")
				return redirect("add-address",pk=pk)
		else:
			messages.info(request, "Please ensure to fill in valid details")
			return redirect("add-address",pk=pk)

	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'on_delivery':on_delivery, 'delivered':delivered, 'cancelled':cancelled,
	'recent_orders':recent_orders,'footer_link':footer_link,'addresses':addresses,'form':form
	}
	return render(request, 'app/add-address.html', context)

@login_required
def edit_address(request, pk):
	customer = User.objects.get(id = request.user.id)
	address = Address.objects.get(id=pk)
	orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	on_delivery = orders.filter(status = 'on delivery').count()
	delivered = orders.filter(status = 'delivered').count()
	cancelled = orders.filter(status = 'cancelled').count()
	footer_link = Footer.objects.all()
	total_orders = orders.count()

	form = AddAddressForm(instance=address)
	if request.method == 'POST':
		form = AddAddressForm(request.POST, instance=address)
		if form.is_valid():
			try:
				form.save()
				messages.success(request, "Address successfully updated!")
				return redirect("edit-address",pk=pk)

			except ObjectDoesNotExist:
				messages.info(request, "Please ensure to fill in valid details")
				return redirect("edit-address",pk=pk)
		else:
			messages.info(request, "Please ensure to fill in valid details")
			return redirect("edit-address",pk=pk)

	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'on_delivery':on_delivery, 'delivered':delivered, 'cancelled':cancelled,
	'recent_orders':recent_orders,'footer_link':footer_link,'address':address,'form':form
	}
	return render(request, 'app/edit-address.html', context)

@login_required
def set_default_address(request, pk):
	customer = User.objects.get(id = request.user.id)
	address = Address.objects.filter(id=pk, user=request.user)
	orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	on_delivery = orders.filter(status = 'on delivery').count()
	delivered = orders.filter(status = 'delivered').count()
	cancelled = orders.filter(status = 'cancelled').count()
	footer_link = Footer.objects.all()
	total_orders = orders.count()

	if request.method == 'POST':
		try:
			old_default_address = Address.objects.filter(user=request.user, default=True)
			old_default_address.update(default=False)
			address.update(default=True)
			messages.success(request, "Default address successfully updated!")
			return redirect("address-list",pk=request.user.id)

		except ObjectDoesNotExist:
			messages.info(request, "There was an error processing this request")
			return redirect("address-list",pk=request.user.id)

	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'on_delivery':on_delivery, 'delivered':delivered, 'cancelled':cancelled,
	'recent_orders':recent_orders,'footer_link':footer_link,'address':address
	}
	return render(request, 'app/set-default-address.html', context)

@login_required
def delete_address(request, pk):
	customer = User.objects.get(id = request.user.id)
	address = Address.objects.filter(id=pk, user=request.user)
	orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	on_delivery = orders.filter(status = 'on delivery').count()
	delivered = orders.filter(status = 'delivered').count()
	cancelled = orders.filter(status = 'cancelled').count()
	footer_link = Footer.objects.all()
	total_orders = orders.count()

	if request.method == 'POST':
		try:
			address = Address.objects.filter(id=pk, user=request.user).delete()
			messages.success(request, "Address was successfully deleted!")
			return redirect("address-list",pk=request.user.id)

		except ObjectDoesNotExist:
			messages.info(request, "There was an error processing this request")
			return redirect("address-list",pk=request.user.id)

	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'on_delivery':on_delivery, 'delivered':delivered, 'cancelled':cancelled,
	'recent_orders':recent_orders,'footer_link':footer_link,'address':address
	}
	return render(request, 'app/delete-address.html', context)
@login_required
def order_detail(request, pk):
	single_order = Order.objects.get(id=pk, ordered = True)
	customer = User.objects.get(id = request.user.id)
	orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	on_delivery = orders.filter(status = 'on delivery').count()
	delivered = orders.filter(status = 'delivered').count()
	cancelled = orders.filter(status = 'cancelled').count()
	total_orders = orders.count()
	footer_link = Footer.objects.all()
	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'on_delivery':on_delivery, 'delivered':delivered, 'cancelled':cancelled,
	'recent_orders':recent_orders, 'single_order':single_order,'footer_link':footer_link
	}
	return render(request, 'app/order-detail.html', context)

@login_required
def refund_order(request, pk):
	customer = User.objects.get(id = pk)
	orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	on_delivery = orders.filter(status = 'on delivery').count()
	delivered = orders.filter(status = 'delivered').count()
	cancelled = orders.filter(status = 'cancelled').count()
	request_refund = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	cancelled_orders  = orders.filter(status = 'cancelled')
	total_orders = orders.count()
	footer_link = Footer.objects.all()
	paginator = Paginator(request_refund, 10)
	page_request_var = 'page'
	page = request.GET.get(page_request_var)
	try:
		paginated_queryset = paginator.page(page)
	except PageNotAnInteger:
		paginated_queryset = paginator.page(1)
	except EmptyPage:
		paginated_queryset = paginator.page(paginator.num_pages)

	form = RefundForm()
	if request.method == "POST":
		form = RefundForm(request.POST)
		if form.is_valid():
			ref_code = form.cleaned_data.get('ref_code')
			reason = form.cleaned_data.get('reason')
			try:
				order = Order.objects.get(ref_code=ref_code)
				if order.status == 'cancelled':
					messages.warning(request, "Cannot refund already cancelled Order!")
					return redirect('ref', pk=pk)
				elif order.status == 'refund requested':
					messages.warning(request, "You already requested for a refund!")
					return redirect('ref', pk=pk)
				elif order.status == 'refund declined':
					messages.warning(request, "Your request for refund has been declined!")
					return redirect('ref', pk=pk)
				elif order.status == "refund granted":
					messages.info(request, "Your refund request has already been accepted!")
					return redirect('ref', pk=pk)
				elif order.status == "refund completed":
					messages.info(request, "Your refund request has already been completed")
					return redirect('ref', pk=pk)
				elif order.status == "on delivery":
					messages.info(request, "you cannot request refund while order is on delivery.")
					return redirect('ref', pk=pk)
				else:
					order.status = 'refund requested'
					order.save()

					refund = Refund()
					refund.user = request.user
					refund.order = order
					refund.reason = reason
					refund.save()

					messages.info(request, "Your request was recieved, We will contact you as soon as possible")
					return redirect("ref", pk=pk)

			except ObjectDoesNotExist:
				messages.warning(request, "This order does not exist")
				return redirect("ref", pk=pk)

	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'on_delivery':on_delivery, 'delivered':delivered, 'cancelled':cancelled,
	'recent_orders':recent_orders,'request_refund':request_refund,'cancelled_orders':cancelled_orders,'form':form,
	'footer_link':footer_link,'queryset':paginated_queryset, 'page_request_var':page_request_var,
	}
	return render(request, 'app/refund-order.html', context)

@login_required
def cancel_order(request, pk):
	single_order = Order.objects.get(id=pk, ordered = True)
	customer = User.objects.get(id = request.user.id)
	orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')
	recent_orders  = Order.objects.filter(user = customer, ordered = True).order_by('-ordered_date')[0:5]
	on_delivery = orders.filter(status = 'on delivery').count()
	delivered = orders.filter(status = 'delivered').count()
	cancelled = orders.filter(status = 'cancelled').count()
	total_orders = orders.count()
	footer_link = Footer.objects.all()
	
	if request.method == "POST":
		try:
			single_order.status = 'cancelled'
			single_order.save()
			messages.success(request, "Your Order has been Cancelled!")
			return redirect('order-detail',pk=pk)
		except Exception:
			messages.error(request, "Error! Your Order was not cancelled")
			return redirect('order-detail',pk=pk)

	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'on_delivery':on_delivery, 'delivered':delivered, 'cancelled':cancelled,
	'recent_orders':recent_orders, 'single_order':single_order,'footer_link':footer_link
	}
	return render(request, 'app/cancel-order.html', context)

