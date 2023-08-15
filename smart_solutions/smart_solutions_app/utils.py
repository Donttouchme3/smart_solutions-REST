from . import models

EMPLOYEE_CREATE_REVIEW_PATH = 'employee'    
CHILDREN_CREATE_REVIEW_PATH = 'children'
DELETE_ALL_CART_DATA_PATH = 'all'
CUSTOMER_DEFAULT_BALANCE = 0






def check(user, tariff_plan, service, employee=None):
    valid = models.ServiceTariffPlan.objects.filter(id=tariff_plan, service=service).exists()
    check_if_object_not_in_user_cart = models.Cart.objects.filter(user=user, tariff_plan=tariff_plan, service=service).exists()
    valid = valid and not check_if_object_not_in_user_cart
    valid = valid and models.Employee.objects.filter(id=employee, service=service, busy=False).exists()
    return {
        'valid': valid,
        'check_if_object_not_in_user_cart': check_if_object_not_in_user_cart,
    }
    
def employee_image_path(instance, filename):
    employee_id = instance.employee.id

    return f'employee/{employee_id}/{filename}'

def application_image_path(data, filename):
    return f'application/{data.user.pk}/{filename}'

def application_passport_image_path(data, filename):
    return f'application/{data.user.pk}/passport/{filename}'

def valid_order(first_name=None, last_name=None, phone=None):
    return True if first_name and last_name and phone else False

def get_star():
    return [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    ]

def get_status():
    return [
        ( 'Заказ оформлен', 'Заказ оформлен'),
        ('Заказ принят', 'Заказ принят'),
        ('Заказ на стадии выполнения','Заказ на стадии выполнения'),
        ( 'Заказ выполнен', 'Заказ выполнен'),
    ]   

def get_employee_application_status():
    return [
        ('принят', 'Принят'),
        ('отказано', 'Отказано'),
        ('рассматривается', 'Рассматривается'),
    ]