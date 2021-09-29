from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.db.models.signals import post_save
from tinymce.models import HTMLField
from coupon_app.models import *
from ckeditor.fields import RichTextField
from django.core.validators import RegexValidator


# Create your models here.

class Item(models.Model):
	name = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=7, decimal_places=2)
	discount_price = models.DecimalField(max_digits=7, decimal_places=2,blank=True, null=True)
	description = RichTextField(null=True, blank=True)
	image = models.ImageField(null=True, blank=True)
	out_of_stock = models.BooleanField(default=False)
	slug = models.SlugField()

	def __str__(self):
		return self.name

	@property
	def imageURL(self):
		try:
			url = self.image.url

		except:
			url = ''
		return url

	def get_absolute_url(self):
		return reverse('store',kwargs={
		'slug':self.slug
		})

	def get_add_to_cart_url(self):
			return reverse('add',kwargs={
			'slug':self.slug
			})

	def get_remove_from_cart_url(self):
		return reverse('remove',kwargs={
			'slug':self.slug
			})


class OrderItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	ordered = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.quantity}x  {self.item.name}"

	def get_total_item_price(self):
		return self.quantity * self.item.price

	def get_total_discount_item_price(self):
		return self.quantity * self.item.discount_price

	def get_amount_saved(self):
		return self.get_total_item_price() - self.get_total_discount_item_price()

	def get_final_price(self):
		if self.item.discount_price:
			return self.get_total_discount_item_price()
		else:
			return self.get_total_item_price()

class Order(models.Model):
	STATUS_CHOICES = (
		('processing','Processing'),
		('on delivery', 'On delivery'),
		('delivered', 'Delivered'),
		('refund requested', 'Refund requested'),
		('refund declined','Refund declined'),
		('refund granted', 'Refund granted'),
		('refund completed', 'Refund completed'),
		('cancelled', 'Cancelled'),

	)
	phone_message = 'Phone number must be entered in the format: (+7|8) 960 xxx-xx-xx ' 
	phone_regex = RegexValidator(
		regex=r'^(\+?7|8)\d{10}$',
		message=(phone_message)
	)

	DELIVERY_CHOICES = (
		('self pickup','Self Pickup'),
		('delivery', 'Delivery')
	)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	ref_code = models.CharField(max_length=20,blank=True, null=True)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
	ordered = models.BooleanField(default=False)
	status = models.CharField(max_length=100, choices=STATUS_CHOICES, blank=True, null=True)
	street_address = models.CharField(max_length=100,blank=False, null=False)
	apartment_address = models.CharField(max_length=100,blank=False, null=False)
	city = models.CharField(max_length=100,blank=False, null=False,validators=[RegexValidator(regex=r'kazan', message='City must be Kazan' )])
	phone = models.CharField(validators = [phone_regex], max_length=15,blank=False, null=False)
	

	def __str__(self):
		return str(self.id)


	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		if self.coupon:
			total = self.coupon.get_discounted_value(total)
		return total

	def set_order_status(self, val):
		status_dict = {x[1]:x[0] for x in STATUS_CHOICES}
		self.status = status_dict[val]


class Address(models.Model):
	phone_message = 'Phone number must be entered in the format: (+7|8) 960 xxx-xx-xx ' 
	phone_regex = RegexValidator(
		regex=r'^(\+?7|8)\d{10}$',
		message=(phone_message)
	)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
	street_address = models.CharField(max_length=100,blank=False, null=False)
	apartment_address = models.CharField(max_length=100,blank=False, null=False)
	city = models.CharField(max_length=100,blank=False, null=False,validators=[RegexValidator(regex=r'kazan', message='City must be Kazan' )])
	phone = models.CharField(validators = [phone_regex], max_length=15,blank=False, null=False)
	default = models.BooleanField(default=False)

	class Meta:
		verbose_name_plural = 'Addresses'

	def __str__(self):
		return f"{self.street_address}, {self.apartment_address}"


class Refund(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
	order = models.ForeignKey(Order, on_delete = models.CASCADE)
	reason = models.TextField()

	def __str__(self):
		return "order #" + str(self.order)


class Contact(models.Model):
	email = models.EmailField()
	message = models.TextField()
	read = models.BooleanField(default=False)
	def __str__(self):
		return self.email


class Carousel(models.Model):
	title = models.CharField(max_length=100,blank=True,default = ' ')
	description = RichTextField(null=True, blank=True)
	image = models.ImageField()

	def __str__(self):
		return "carousel #" + str(self.id)
	
	@property
	def imageURL(self):
		try:
			url = self.image.url

		except:
			url = ''
		return url
		
class About(models.Model):
	about_cuisine = RichTextField(null=True, blank=True)
	linder_pic = models.ImageField(null=True, blank=True)
	about_linder = RichTextField(null=True, blank=True)
	
	class Meta:
		verbose_name_plural = "About"
	
	def __str__(self):
		return "About Linder"

class Gallery(models.Model):
	image = models.ImageField(blank=True,null=True)
	
	@property
	def imageURL(self):
		try:
			url = self.image.url

		except:
			url = ''
		return url

	class Meta:
		verbose_name_plural = "Gallery"
	def __str__(self):
		return "Image"+str(self.id)

class Footer(models.Model):
	facebook = models.CharField(blank=True, null=True, max_length=200)
	phone = models.CharField(blank=True, null=True, max_length=200)
	email = models.CharField(blank=True, null=True, max_length=200)
	instagram = models.CharField(blank=True, null=True, max_length=200)
	copyright_text = models.CharField(blank=True, null=True, max_length=50)

	class Meta:
		verbose_name_plural = "Footer"
	def __str__(self):
		return "Footer"

class Services(models.Model):
	title = models.CharField(max_length=100)
	image = models.ImageField(blank=True, null=True)

	class Meta:
		verbose_name_plural = "Services"

	@property
	def imageURL(self):
		try:
			url = self.image.url

		except:
			url = ''
		return url
		
	def __str__(self):
		return self.title
