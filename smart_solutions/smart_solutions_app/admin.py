from typing import Any
from django.contrib import admin
from django.utils.safestring import mark_safe
from . import models


# Register your models here.

class GalleryAdmin(admin.TabularInline):
    model = models.ServiceGallery
    fk_name = 'service'
    extra = 1
    

class EmployeeGalleryAdmin(admin.TabularInline):
    model = models.EmployeeGallery
    fk_name = 'employee'
    extra = 1

@admin.register(models.User)
class AdminCustomer(admin.ModelAdmin):
    list_display = ('id', 'username','first_name', 'last_name', 'phone','balance')
    
@admin.register(models.Address)
class AdminAddress(admin.ModelAdmin):
    list_display = ('id', 'user', 'address')
    
@admin.register(models.Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_price_list_count')
    inlines = [GalleryAdmin]
    
    def get_price_list_count(self, obj):
            return obj.price_lists.all().count()
        
    get_price_list_count.short_description = 'Количество тарифов'
    
@admin.register(models.ServiceTariffPlan)
class ServiceTariffPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'price')
    list_editable = ('price',)
    list_filter = ('service',)
    
@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'service',
                    'first_name', 'last_name', 'phone', 'busy', 'get_photo')
    list_editable = ('busy',)
    list_filter = ('service', 'busy')
    inlines = [EmployeeGalleryAdmin]
    
    def get_photo(self, obj):
        if obj.employee_images:
            try:
                return mark_safe(f'<img src="{obj.employee_images.first().image.url}" width="75">')
            except:
                return '-'
        else:
            return '-'

    get_photo.short_description = 'Миниатюра'
    

@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'employee', 'parent')
    list_filter = ('user',)
    
@admin.register(models.Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'employee', 'star')
    list_filter = ('star', 'user', 'employee')
    # readonly_fields = ('star',)
    

@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service', 'tariff_plan', 
                    'employee', 'price')
    

@admin.register(models.Order)
class AdminOrder(admin.ModelAdmin):
    list_display = ('id', 'user',
                    'total_price', 'status')
    list_editable = ('status',)
    
    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if change and form.cleaned_data['status'] == 'Заказ выполнен':
            orders = models.OrderService.objects.filter(order=obj)
            for order in orders:
                order.employee.busy = False
                order.employee.save()
            obj.save()
        elif change:
            obj.save()
         
    
    

    
@admin.register(models.OrderService)
class UserOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'service', 'tariff_plan', 'employee')
    list_filter = ('order',)
    
    
@admin.register(models.Transaction)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount')
    list_filter = ('user',)
    

@admin.register(models.Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status')
    readonly_fields = ('user', 'first_name', 'last_name', 'image', 'passport_image', 'passport', 'phone', 'characteristics')
    list_filter = ('status', 'user')
    actions = ['save_to_employee']
    
    
    def save_to_employee(self, request, queryset):
        for application in queryset:
            employee = models.Employee.objects.create(user=application.user,
                                            service=application.service,
                                            first_name=application.first_name,
                                            last_name=application.last_name,
                                            phone=application.phone,
                                            passport=application.passport,
                                            characteristics=application.characteristics)
            
            models.EmployeeGallery.objects.create(employee_id=employee.id, image=application.image)
            application.status = 'принят'
            application.save()