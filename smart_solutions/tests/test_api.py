from rest_framework import status
import pytest
from smart_solutions_app import models as model
from . import mixins


@pytest.fixture
@pytest.mark.django_db
def create_services():
    objects_to_create = [
        model.Service(title='Уборка', description='Bent bone of left ulna, subs for clos fx w delay heal'),
        model.Service(title='Переезд', description='Transient paralysis'),
        model.Service(title='Ремонт', description='Traumatic rupture of symphysis pubis, initial encounter'),
    ]
    services = model.Service.objects.bulk_create(objects_to_create)
    return services

@pytest.fixture
@pytest.mark.django_db
def create_service_tariff_plans(create_services):
    objects_to_create = [
        model.ServiceTariffPlan(service_id=1, description='Уборка офисов', price=1500000),
        model.ServiceTariffPlan(service_id=1, description='Уборка квартир', price=1000000),
        model.ServiceTariffPlan(service_id=1, description='Мойка окон', price=500000),
        model.ServiceTariffPlan(service_id=2, description='Переезд', price=1200000),
        model.ServiceTariffPlan(service_id=3, description='Ремонт кухни', price=800000),
        model.ServiceTariffPlan(service_id=3, description='Монтаж', price=300000),
        model.ServiceTariffPlan(service_id=3, description='Ремонт квартиры', price=500000)]
    tariff_plans = model.ServiceTariffPlan.objects.bulk_create(objects_to_create)
    return tariff_plans

@pytest.fixture
@pytest.mark.django_db
def create_users():
    users = mixins.user_register_payload()
    status_codes = []
    for user in users:
        user_register_response = mixins.user_register(user)
        status_codes.append(user_register_response.status_code)
    return status_codes
    
@pytest.fixture
@pytest.mark.django_db
def users_token(create_users):
    users_token_dict = {}
    for user in model.User.objects.all():
        user_payload = {'username': user.username, 'password': 'As031001'}
        user_login_response = mixins.user_login(user_payload)
        users_token_dict[user.username] = {'Authorization': f'Token {user_login_response.json()["auth_token"]}'}
    return users_token_dict

@pytest.fixture
@pytest.mark.django_db
def create_address(users_token):
    user_token = users_token['asilbek']
    address_payload = mixins.user_address_payload()
    address_response = mixins.user_address(user_token, address_payload)
    
@pytest.fixture
@pytest.mark.django_db
def send_application(users_token, create_services):
    application_payload = mixins.user_application_payload()
    applications_json = [mixins.user_application(payload=application_payload[0], token=users_token['chou']).json(),
                         mixins.user_application(payload=application_payload[1], token=users_token['donttouchme']).json()]
    return applications_json

@pytest.fixture
@pytest.mark.django_db
def create_employee(create_users, create_services, send_application):
    for application in model.Application.objects.all():
        model.Employee.objects.create(user=application.user,
                                      service=application.service,
                                      first_name=application.first_name,
                                      last_name=application.last_name,
                                      phone=application.phone,
                                      passport=application.passport,
                                      characteristics=application.characteristics)
    return model.Employee.objects.all()

@pytest.fixture
@pytest.mark.django_db
def create_review(users_token, create_employee):
    user_token = users_token['asilbek']
    create_review_payload = [mixins.review_payload(1)['create_review'], mixins.review_payload(1)['create_review'], mixins.review_payload(2)['create_review']]
    create_children_for_review_payload = mixins.review_payload(employee_id=1)['children_review']
    reviews = []
    for payload in create_review_payload:
        employee_id = payload['employee']
        create_review_response = mixins.review_create(payload=payload, token=user_token, employee_id=employee_id)  
        reviews.append(create_review_response.json())      
    create_children_for_review_response = mixins.review_create_children(payload=create_children_for_review_payload,
                                                       token=user_token,
                                                       review_id=1)
    reviews.append(create_children_for_review_response.json())
    update_review_payload = mixins.review_payload(parent_id=1)['update_review']
    update_review_response = mixins.review_update(review_id=4, payload=update_review_payload, token=user_token)
    reviews[3] = update_review_response.json() 
    delete_review_response = mixins.review_delete(token=user_token, review_id=2)
    if delete_review_response.status_code == status.HTTP_204_NO_CONTENT:
        reviews.remove(reviews[1])
    return reviews

@pytest.fixture
@pytest.mark.django_db
def create_rating(users_token, create_employee):
    user_token = users_token['asilbek']
    rating_payloads = [mixins.rating_payload(2), mixins.rating_payload(1)]
    responses_json = []
    for payload in rating_payloads:
        rating_response = mixins.rating(token=user_token, payload=payload, employee_id=payload['employee'])
        responses_json.append(rating_response.json())
        assert rating_response.status_code == status.HTTP_201_CREATED 
    return responses_json
        
@pytest.fixture
@pytest.mark.django_db
def cart_add(users_token, create_service_tariff_plans, create_employee):
    user_token = users_token['asilbek']
    cart_add_payload = [mixins.cart_add_payload(service_id=1, employee_id=2, tariff_plan_id=3),
                        mixins.cart_add_payload(service_id=2, employee_id=1, tariff_plan_id=4)]
    for payload in cart_add_payload:
        cart_add_response = mixins.cart_add(payload=payload, token=user_token) 
        assert cart_add_response.status_code == status.HTTP_201_CREATED
    return model.Cart.objects.filter(user__username='asilbek')

@pytest.fixture
@pytest.mark.django_db
def payment(users_token):
    user_token = users_token['asilbek']
    payment_payload = mixins.payment_payload()
    payment_response = mixins.payment(user_token, payment_payload)
    return payment_response.status_code

@pytest.fixture
@pytest.mark.django_db
def order_create(users_token, cart_add, create_address, payment):
    user_token = users_token['asilbek']
    order_create_response = mixins.order_create(user_token)
    return order_create_response.status_code




@pytest.mark.django_db
def test_user_register(create_users):
    assert len(create_users) == 3
    for status_code in create_users:
        assert status_code == status.HTTP_201_CREATED
    
@pytest.mark.django_db
def test_send_application(send_application):
    assert len(send_application) == 2
    for application in send_application:
        assert application['first_name'] in mixins.FIRST_NAME
    
@pytest.mark.django_db
def test_my_applications(send_application, users_token):
    jsons_len = []
    status_codes = []
    for user_token in users_token.values():
        my_applications_response = mixins.user_applications(token=user_token)
        my_applications_by_id_response = mixins.user_applications_by_id(token=user_token)
        jsons_len.append(len(my_applications_response.json()))
        status_codes.append(my_applications_by_id_response.status_code)
        
    assert jsons_len.count(mixins.APPLICATION_JSON_LEN_IF_APPLICATION_EXISTS) == 2
    assert jsons_len.count(mixins.APPLICATION_JSON_LEN_IF_APPLICATION_NOT_EXISTS) == 1
    assert status_codes.count(mixins.APPLICATION_JSON_STATUS_CODE_IF_APPLICATION_EXISTS) == 1
    assert status_codes.count(mixins.APPLICATION_JSON_STATUS_CODE_IF_APPLICATION_NOT_EXISTS) == 2
    
@pytest.mark.django_db
def test_employee(create_employee, create_review, create_rating):
    for i in range(1, 3):
        employee_response = mixins.get_employee(i)
        assert employee_response.json()['first_name'] in mixins.FIRST_NAME
        assert employee_response.status_code == status.HTTP_200_OK      

@pytest.mark.django_db
def test_create_review(create_review):
    assert len(create_review) == 3
    for review in create_review:
        for i in review:
            assert i in ['id', 'text', 'created_date', 'employee', 'parent']

@pytest.mark.django_db
def test_rating(create_rating):
    assert len(create_rating) == 2
    for rating in create_rating:
        assert 'id' in rating
        assert 'employee' in rating

@pytest.mark.django_db
def test_get_services(create_services):
    get_services_response = mixins.get_services()
    data = get_services_response.json()
    assert len(data) == len(create_services)
    assert data[0]['title'] == create_services[0].title
    assert data[1]['title'] == create_services[1].title
    assert data[2]['title'] == create_services[2].title
    assert get_services_response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_get_service_by_id(create_services, create_review, create_rating, create_service_tariff_plans, users_token, cart_add):
    user_token = users_token['asilbek']
    get_service_by_id_response = mixins.get_service_by_id(token=user_token, service_id=1)
    data = get_service_by_id_response.json()
    employees = model.Employee.objects.filter(service_id=data['id'])
    tariff_plan = model.ServiceTariffPlan.objects.filter(service_id=data['id'])
    
    assert len(employees) == len(data['employees'])
    assert len(tariff_plan) == len(data['tariff_plan'])
    assert get_service_by_id_response.status_code == status.HTTP_200_OK
    
@pytest.mark.django_db
def test_cart_add(cart_add, create_services, create_service_tariff_plans):
    assert len(cart_add) == 2
    for i in cart_add:
        assert i.user.username == 'asilbek'
        assert i.service.id in [j.id for j in create_services]
        assert i.tariff_plan.id in [j.id for j in create_service_tariff_plans]
        
@pytest.mark.django_db
def test_cart_delete(cart_add, users_token):
    user_token = users_token['asilbek']
    cart_delete_payload = mixins.cart_delete_payload(1, 3)
    cart_delete_response = mixins.cart_delete(user_token, cart_delete_payload)
    assert cart_delete_response.status_code == status.HTTP_204_NO_CONTENT
    
@pytest.mark.django_db
def test_cart_clear(cart_add, users_token):
    user_token = users_token['asilbek']
    cart_clear_response = mixins.cart_clear(user_token)
    assert cart_clear_response.status_code == status.HTTP_204_NO_CONTENT
    assert not model.Cart.objects.filter(user__username='asilbek').exists()
    
@pytest.mark.django_db
def test_user_cart(cart_add, users_token):
    user_token = users_token['asilbek']
    cart_total_price = sum([i.price for i in cart_add])
    user_cart_response = mixins.cart(user_token)
    assert user_cart_response.status_code == status.HTTP_200_OK
    assert len(user_cart_response.json()) == 2
    assert cart_total_price == user_cart_response.json()['Общая стоимость корзины']
    
@pytest.mark.django_db
def test_checkout(cart_add, users_token, create_address):
    user_token = users_token['asilbek']
    user_address = model.Address.objects.filter(user__username='asilbek').first()
    checkout_response = mixins.checkout(user_token)
    assert checkout_response.status_code == status.HTTP_200_OK
    data = checkout_response.json()
    if user_address:
        assert data['Адрес']['id'] == user_address.id   
    else:
        assert data['Адрес'] == 'Вы еще не указали свой адрес'
        
@pytest.mark.django_db
def test_payment(users_token, payment):
    assert payment == status.HTTP_200_OK
    assert model.User.objects.get(username='asilbek').balance == int(mixins.payment_payload()['amount'])

@pytest.mark.django_db
def test_order_create(order_create):
    assert order_create == status.HTTP_201_CREATED
    order = model.Order.objects.filter(user__username='asilbek').first()
    assert len(model.OrderService.objects.filter(order=order.id)) == 2
    assert order
    
@pytest.mark.django_db
def test_order_cancel(order_create, users_token):
    order_id = model.Order.objects.filter(user__username='asilbek').first().id
    user_token = users_token['asilbek']
    order_cancel_response = mixins.order_cancel(user_token, order_id)
    assert order_cancel_response.status_code == status.HTTP_204_NO_CONTENT
    assert not model.Order.objects.filter(user__username='asilbek').exists()
    
@pytest.mark.django_db
def test_user_orders(order_create, users_token):
    user_token = users_token['asilbek']
    user_orders_response = mixins.order(user_token)
    order_id = model.Order.objects.filter(user__username='asilbek').first().id
    order_id_in_json = user_orders_response.json()[0]['id']
    assert str(order_id) == order_id_in_json
    assert user_orders_response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_account_for_user(users_token, order_create):
    user_token = users_token['asilbek']
    account_response = mixins.account(user_token)
    data = account_response.json()
    assert account_response.status_code == status.HTTP_200_OK
    assert str(model.Order.objects.filter(user__username=data['username']).first().id) == data['user_orders'][0]['id']
    assert model.Address.objects.filter(user__username=data['username']).exists()
    