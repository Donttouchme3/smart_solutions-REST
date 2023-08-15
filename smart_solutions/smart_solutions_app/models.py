from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from datetime import datetime
import uuid

from .utils import (get_star, 
                    get_status, 
                    employee_image_path, 
                    get_employee_application_status, 
                    application_image_path, 
                    application_passport_image_path)


class MyUserManager(BaseUserManager):
    
    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("Вы не ввели Логин")
        user = self.model(
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, *email, username, password, **phone):
        return self._create_user(*email, username, password, **phone)
 
    def create_superuser(self, *email, username, password):
        return self._create_user(*email, username, password, is_staff=True, is_superuser=True)
    

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True, unique=True) 
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True) 
    phone = models.CharField(max_length=50, null=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    avatar = models.ImageField(upload_to='user/', null=True, blank=True)
    balance = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True) 
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username' 
 
    objects = MyUserManager() 
    
    def __str__(self) -> str:
        return f'{self.username}'
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        
        
class Address(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='user_address')
    address = models.CharField(verbose_name='Адрес', max_length=200)
    floor = models.CharField(verbose_name='Этаж', max_length=10, blank=True, null=True)
    entrance = models.CharField(verbose_name='Подъезд', max_length=10, blank=True, null=True)
    intercom = models.CharField(verbose_name='Домофон', max_length=20, blank=True, null=True)
    apartment = models.CharField(verbose_name='Квартира дом', max_length=20, blank=True, null=True)
    

    def __str__(self) -> str:
        return f'Адрес пользователя: {self.user.username}'
        
    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'
        

class Service(models.Model):
    title = models.CharField(verbose_name='Наименование', max_length=50)
    description = models.TextField(verbose_name='Описание')
    
    def __str__(self) -> str:
        return self.title            
    
    class Meta:
        verbose_name = 'Сервис'
        verbose_name_plural = 'Сервисы'
        

class ServiceTariffPlan(models.Model):
    service = models.ForeignKey(Service, 
                                verbose_name='Сервис', 
                                on_delete=models.CASCADE, 
                                related_name='tariff_plan')
    description = models.TextField(verbose_name='Описание')
    price = models.IntegerField(verbose_name='Цена', default=0)
    
    def __str__(self) -> str:
        return f'{str(self.pk)} {self.description[:20]}'
    
    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
        

class ServiceGallery(models.Model):
    service = models.ForeignKey(Service, 
                                verbose_name='Сервис', 
                                on_delete=models.CASCADE, 
                                related_name='images')
    image = models.ImageField(verbose_name='Изображение', 
                              upload_to='service/', 
                              blank=True, null=True)
    

class Employee(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    service = models.ForeignKey(Service,
                                verbose_name='Сервис',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                related_name='employees')
    first_name = models.CharField(verbose_name='Имя', max_length=50)
    last_name = models.CharField(verbose_name='Фамилия', max_length=50)
    phone = models.CharField(verbose_name='Телефон', max_length=20)
    passport = models.CharField(verbose_name='Паспортные данные', max_length=30)
    characteristics = models.TextField(verbose_name='Информация о работнике')
    busy = models.BooleanField(verbose_name='Статус занятости', default=False)
    
    def __str__(self) -> str:
        return self.user.username
    
    def get_first_photo(self, obj):
        if self.employee_images:
            try:
                return self.employee_images.first().image.url
            except:
                return 'https://www.raumplus.ru/upload/iblock/545/Skoro-zdes-budet-foto.jpg'
        else:
            return 'https://www.raumplus.ru/upload/iblock/545/Skoro-zdes-budet-foto.jpg'
        
    
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        

class EmployeeGallery(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_images')
    

    image  = models.ImageField(verbose_name='Изображение', upload_to=employee_image_path)
    
    def __str__(self) -> str:
        return f'Изображение сотрудника: {self.employee.user}'
    
    
    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        
        
class Application(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь',on_delete=models.CASCADE)
    service = models.ForeignKey(Service, verbose_name='Сервис' ,on_delete=models.CASCADE)
    first_name = models.CharField(verbose_name='Имя', max_length=50)
    last_name = models.CharField(verbose_name='Фамилия', max_length=50)
    passport = models.CharField(verbose_name='Паспортные данные', max_length=50)
    phone = models.CharField(verbose_name='Телефон', max_length=50)
    characteristics = models.TextField(verbose_name='Личная информация')
    passport_image = models.ImageField(verbose_name='Фотография паспорта', upload_to=application_passport_image_path)
    image = models.ImageField(verbose_name='Изображение', upload_to=application_image_path)
    status = models.CharField(verbose_name='Статус заявления', default='рассматривается', max_length=100, choices=get_employee_application_status())
    
    def __str__(self):
        return f'Заявка от пользователя: {self.user}'
    
    
    class Meta:
        verbose_name = 'Заявление'
        verbose_name_plural = 'Заявления'
        


    

class Review(models.Model):
    user = models.ForeignKey(User,
                             verbose_name='Пользователь', 
                             on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, 
                                 verbose_name='Работник',
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True,
                                 related_name='employee_reviews')
    text = models.CharField(verbose_name='Отзыв', max_length=400)
    parent = models.ForeignKey('self',
                               on_delete=models.CASCADE, 
                               null=True, 
                               blank=True,
                               related_name='children')
    created_date = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True, null=True)
    
    def __str__(self) -> str:
        return f'Отзыв пользователя: {self.user.username}'
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        
        
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, 
                                 verbose_name='Работник',
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True,
                                 related_name='employee_rating')
    star = models.CharField(choices=get_star(), max_length=20)
    
    def __str__(self) -> str:
        return f'Оценка пользователя: {self.user.username}'
    
    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
    

class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, verbose_name='Сервис',on_delete=models.CASCADE, related_name='cart_services')
    tariff_plan = models.ForeignKey(ServiceTariffPlan, verbose_name='Тарифный план', on_delete=models.CASCADE, related_name='cart_tariff_plans')
    employee = models.ForeignKey(Employee,
                                verbose_name ='Работник',
                                null=True,
                                blank=True,
                                on_delete = models.CASCADE)
    price = models.IntegerField(verbose_name='Цена', blank=True)
       
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'Корзина пользователя: {self.user.username}'
    
    
class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4(), primary_key=True, editable=False)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='user_orders')
    total_price = models.IntegerField(verbose_name='Стоимость заказа')
    status = models.CharField(verbose_name='Статус', choices=get_status(), max_length=30, default='Заказ оформлен')
    address = models.ForeignKey(Address, 
                                verbose_name='Адрес',
                                on_delete=models.SET_NULL, 
                                null=True, 
                                blank=True)
    
    
    def __str__(self) -> str:
        return f'Заказ пользователя: {self.user.username}'
    
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        

class OrderService(models.Model):
    order = models.ForeignKey(Order, verbose_name='Номер заказа', on_delete=models.CASCADE, related_name='order_services')
    service = models.ForeignKey(Service, verbose_name='Сервис',on_delete=models.CASCADE)
    tariff_plan = models.ForeignKey(ServiceTariffPlan, verbose_name='Тарифный план', on_delete=models.CASCADE, null=True)
    employee = models.ForeignKey(Employee,
                                verbose_name ='Работник',
                                null=True,
                                blank=True,
                                on_delete = models.CASCADE)
    
        
    def __str__(self) -> str:
        return f'Заказ номер: {self.order.id }'
    
    class Meta:
        verbose_name = 'Товар заказа'
        verbose_name_plural = 'Товары заказа'
        

class Transaction(models.Model):
    session_id = models.TextField(verbose_name='Номер транзакции',editable=False)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField(verbose_name='Сумма')
    
    def __str__(self) -> str:
        return self.user.username
    
    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    