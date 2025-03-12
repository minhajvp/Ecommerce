from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone,name, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not phone:
            raise ValueError("Users must have a phone number")
        if not name:
            raise ValueError("Users must have a Name")

        user = self.model(email=self.normalize_email(email), phone=phone,name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone,name, password=None):
        user = self.create_user(email, phone,name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone" 
    REQUIRED_FIELDS = ["email","name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    class CategoryChoices(models.TextChoices):
        FRESH = "Fresh", "Fresh"
        ORIENTAL_WOODY = "Oriental/Woody", "Oriental/Woody"
        FLORAL = "Floral", "Floral"

    class GenderChoices(models.TextChoices):
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"
        UNISEX = "Unisex", "Unisex"

    name = models.CharField(max_length=50)
    price = models.PositiveIntegerField()
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    sillage = models.PositiveIntegerField()  
    projection = models.PositiveIntegerField()
    longevity = models.PositiveIntegerField()
    top_note = models.CharField(max_length=50)
    middle_note = models.CharField(max_length=50)
    base_note = models.CharField(max_length=50)
    gender = models.CharField(
        max_length=20,
        choices=GenderChoices.choices,  # Adding choices
        default=GenderChoices.UNISEX  # Optional default category
    )
    category = models.CharField(
        max_length=20,
        choices=CategoryChoices.choices,  # Adding choices
        default=CategoryChoices.FRESH  # Optional default category
    )
    main_image = models.ImageField(upload_to="products/main_images/")
    created = models.DateTimeField(auto_now_add=True)
    disable = models.BooleanField(default=False)
    summer_pick=models.BooleanField(default=False)
    

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class Size(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizes")
    size = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.size}ml"

    class Meta:
        verbose_name = "Size"
        verbose_name_plural = "Sizes"


class Images(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/extra_images/")

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
    

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.cart_items.all())

    def __str__(self):
        return f"Cart - {self.user.name}"
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="cart_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
class Review(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    review=models.TextField()
    star=models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.name} -{self.star}"
    


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.name} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
    
class Banner(models.Model):
    banner=models.ImageField()
    created_at = models.DateTimeField(auto_now_add=True)

class Address(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    house_name=models.CharField(max_length=100)
    street=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    pincode=models.PositiveIntegerField()
    contact_no=models.PositiveIntegerField()
    contact_no2=models.PositiveIntegerField()
    created=models.DateTimeField(auto_now_add=True)







