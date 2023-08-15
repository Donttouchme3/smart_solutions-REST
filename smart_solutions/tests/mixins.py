from rest_framework.test import APIClient
import base64

client = APIClient()


def user_register(payload): return client.post('/api/register/', payload)
def user_login(payload): return client.post('/auth/token/login/', payload)
def user_address(token, payload): return client.post('/api/address/', headers=token, data=payload)
def user_application(payload, token): return client.post('/api/application/', headers=token, data=payload)
def user_applications(token): return client.get('/api/my-applications/', headers=token)
def user_applications_by_id(token): return client.get('/api/my-applications/1/', headers=token)
def get_employee(id): return (client.get(f'/api/employee/{id}/'))
def get_services(): return client.get('/api/services/')
def get_service_by_id(token=None, service_id=1): return client.get(f'/api/services/{service_id}/', headers=token)
def review_create(employee_id, payload, token): return client.post(f'/api/review/employee/{employee_id}/', data=payload, headers=token)
def review_create_children(review_id, token, payload): return client.post(f'/api/review/children/{review_id}/', data=payload, headers=token)
def review_update(review_id, payload, token): return  client.patch(f'/api/review/update/{review_id}/', data=payload, headers=token)
def review_delete(review_id, token): return client.delete(f'/api/review/delete/{review_id}/', headers=token)
def rating(token, payload, employee_id): return client.post(f'/api/rating/{employee_id}/', headers=token, data=payload)
def cart_add(token, payload): return client.post('/api/cart/add/', headers=token, data=payload)
def cart_delete(token, payload): return client.delete('/api/cart/delete/', headers=token, data=payload)
def cart_clear(token): return client.delete('/api/cart/delete/all/', headers=token)
def cart(token): return client.get('/api/cart/', headers=token)
def checkout(token): return client.get('/api/checkout/', headers=token)
def payment(token, payload): return client.post('/api/payment/', headers=token, data=payload)
def order_create(token): return client.get('/api/order/create/', headers=token)
def order_cancel(token, uuid): return client.delete(f'/api/order/cancel/{uuid}/', headers=token)
def order(token): return client.get('/api/order/', headers=token)
def account(token): return client.get('/api/account/', headers=token)

def user_register_payload():
    return [{
        'username': 'asilbek',
        'email': 'asil007bek@icloud.com',
        'first_name': 'Asilbek',
        'last_name': 'Shavkatov',
        'phone': '+79780078792',
        'password': 'As031001',
        'password2': 'As031001',},
           {'username': 'chou',
        'email': 'asil007bek@gmail.com',
        'first_name': 'TestUsername1',
        'last_name': 'TestLastname1',
        'phone': '+79780078798',
        'password': 'As031001',
        'password2': 'As031001',},
           {'username': 'donttouchme',
        'email': 'asilek@gmail.com',
        'first_name': 'TestUsername2',
        'last_name': 'TestLastname2',
        'phone': '+79780078797',
        'password': 'As031001',
        'password2': 'As031001',}]
    
def user_address_payload():
    return {
        'address': 'Чорсу коратош',
        'floor': '5',
        'entrance': '2',
        'apartment': '20'
    }

def user_application_payload():
    return [{
        'service': 2,
        'first_name': 'Асилбек',
        'last_name': 'Шавкатов',
        'passport': 'As031001',
        'phone': '+79780078792',
        'characteristics': 'Test Characteristics',
        'passport_image': ('1.jpg', open('C:/Users/asil0/Downloads/1.jpg', 'rb')),
        'image': ('1.jpg', open('C:/Users/asil0/Downloads/1.jpg', 'rb')),
    },
            {
        'service': 1,
        'first_name': 'Асилбек1',
        'last_name': 'Шавкатов1',
        'passport': 'As031001',
        'phone': '+79780078793',
        'characteristics': 'Test Characteristics',
        'passport_image': ('1.jpg', open('C:/Users/asil0/Downloads/1.jpg', 'rb')),
        'image': ('1.jpg', open('C:/Users/asil0/Downloads/1.jpg', 'rb')),
    }]
    

def review_payload(employee_id=None, parent_id=None, review_id=None):
    return {
        'create_review': {
            'employee': employee_id,
            'text': f'Я добавил отзыв для сотрудника {employee_id}'
        },
        'children_review': {
            'employee': employee_id,
            'text': f'Я добавил отзыв на отзыв 11:54',
        },
        'update_review': {
            'text': f'Я обновил отзыв 12:04',
            'parent': parent_id
        }
    }


def rating_payload(employee_id):
    return {
        'employee': employee_id,
        'star': 5
    }
    
def cart_add_payload(employee_id, service_id, tariff_plan_id):
    return {
        'employee': employee_id,
        'service': service_id,
        'tariff_plan': tariff_plan_id,
        'price': 50000
    }
    
def cart_delete_payload(service_id, tariff_plan_id):
    return {
        'service': service_id,
        'tariff_plan': tariff_plan_id
    }
    
def payment_payload():
    return {
        'card': '986035018855703',
        'valid_to': '03/12',
        'year': '2028',
        'cvs': '697',
        'amount': '10000000'
    }


APPLICATION_JSON_LEN_IF_APPLICATION_EXISTS = 1
APPLICATION_JSON_LEN_IF_APPLICATION_NOT_EXISTS = 0
APPLICATION_JSON_STATUS_CODE_IF_APPLICATION_EXISTS = 200
APPLICATION_JSON_STATUS_CODE_IF_APPLICATION_NOT_EXISTS = 404
FIRST_NAME = ['Асилбек', 'Асилбек1']