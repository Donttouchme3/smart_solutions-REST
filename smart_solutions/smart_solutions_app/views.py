from rest_framework import permissions
from rest_framework import viewsets
from django.db.utils import IntegrityError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from configs import settings

from . import models
from . import serializers
from . import utils

import stripe

class RegisterUserView(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else: 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Service.objects.all()
            
    
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ServiceSerializer
        elif self.action == 'retrieve':
            return serializers.ServiceDetailSerializer


       
       
class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.AddressSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        

class ApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return models.Application.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ListApplicationSerializer
        elif self.action == 'retrieve':
            return serializers.CreateAndRetrieveApplicationSerializer
    
    
    def create(self, request, *args, **kwargs):
        user = request.user
        if models.Application.objects.filter(user=user, status='рассматривается'):
            return Response({'message': 'Вы уже оставили заявление на рассмотрение. Пожалуйста ожидайте ответа'}, status=status.HTTP_200_OK)
        elif len(models.Application.objects.filter(user=user)) >= 5:
            return Response({'message': 'Вы больше не можете оставлять заявление'}, status=status.HTTP_409_CONFLICT)
        elif models.Employee.objects.filter(user=user).exists():
            return Response({'message': 'Вы уже состоите в числе сотрудников'}, status=status.HTTP_200_OK)
        else:
            application_serializer = serializers.CreateAndRetrieveApplicationSerializer(data=request.data)
            if application_serializer.is_valid():
                application_serializer.save(user=user)
                return Response(application_serializer.data ,status=status.HTTP_201_CREATED)
            else:
                return Response(application_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                            
                
        
class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = models.Employee.objects.all()          
    serializer_class = serializers.EmployeeSerializer
    

class CreateReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CreateReviewSerializer
    queryset = models.Review.objects.all()
    
    def create(self, request, *args, **kwargs):
        try:
            if utils.EMPLOYEE_CREATE_REVIEW_PATH in self.request.path:
                EMPLOYEE_ID = self.kwargs['employee_id']
                my_serializer = self.get_serializer(data=self.request.data)
                if my_serializer.is_valid():
                    my_serializer.save(user=self.request.user, employee_id=EMPLOYEE_ID)
                    return Response(my_serializer.data, status=status.HTTP_201_CREATED)
            elif utils.CHILDREN_CREATE_REVIEW_PATH in self.request.path:
                REVIEW_ID = self.kwargs['review_id']
                my_serializer = self.get_serializer(data=self.request.data)
                if my_serializer.is_valid():
                    my_serializer.save(user=self.request.user, parent_id=REVIEW_ID)
                    return Response(my_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(my_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
                return Response({'message': 'Вы пытаетесь оставить отзыв на не существующий объект'}, 
                                status=status.HTTP_400_BAD_REQUEST)
                
    def partial_update(self, request, *args, **kwargs):
        query = self.get_object()
        my_serializer = self.get_serializer(query, data=request.data, partial=True)
        if my_serializer.is_valid():
            self.perform_update(my_serializer)
            return Response(my_serializer.data, status=status.HTTP_200_OK)
        
    def destroy(self, request, *args, **kwargs):
        query = self.get_object()
        self.perform_destroy(query)
        return Response({'message': 'Отзыв успешно удален'},status=status.HTTP_204_NO_CONTENT)
            
            
class RatingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.Rating.objects.all()
    serializer_class = serializers.RatingSerializer
    
    def create(self, request, *args, **kwargs):
        my_serializer = self.get_serializer(data=self.request.data)
        if my_serializer.is_valid():
            EMPLOYEE_ID = kwargs['employee_id']
            my_serializer.save(user=request.user, employee=EMPLOYEE_ID)
            return Response(my_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(my_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CartSerializer
    
    
    def list(self, request, *args, **kwargs):
        user = self.request.user
        instance = models.Cart.objects.filter(user=user)
        cart_total_price = sum([object.price for object in instance])
        my_serializer = serializers.CartViewSerializer(instance, many=True)
        return Response({
            'objects': my_serializer.data,
            'Общая стоимость корзины': cart_total_price,
            }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        my_serializer = self.get_serializer(data=request.data)
        user = self.request.user
        check = utils.check(user=user, tariff_plan=self.request.data['tariff_plan'], 
                            service=self.request.data['service'], 
                            employee=self.request.data['employee'])
        check_if_object_not_in_user_cart = check['check_if_object_not_in_user_cart']
        valid = check['valid']
       
        if my_serializer.is_valid() and valid:
            my_serializer.save(user=user)       
            return Response(status=status.HTTP_201_CREATED)
        elif check_if_object_not_in_user_cart:
            return Response({'message': 'Вы уже добавили этот объект в корзину'})
        else:
            return Response({'errors': my_serializer.errors,
                             'message': 'Не правильные данные для сохранения'}, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        my_serializer = self.get_serializer(data=request.data)
        path = self.request.path
        user = self.request.user
        delete_all_path = utils.DELETE_ALL_CART_DATA_PATH
        service = self.request.data['service'] if not delete_all_path in path else None
        tariff_plan = self.request.data['tariff_plan'] if not delete_all_path in path else None
        check_object_if_exists_in_user_cart = utils.check(user=user, tariff_plan=tariff_plan, service=service)['check_if_object_not_in_user_cart']
        
        if delete_all_path in path:
            instance = models.Cart.objects.filter(user=user)
            instance.delete()
            return Response({'Ваша корзина успешно удалена'}, status=status.HTTP_204_NO_CONTENT)
        
        elif my_serializer.is_valid() and check_object_if_exists_in_user_cart:
            instance = models.Cart.objects.get(user=user, tariff_plan=tariff_plan, service=service)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        elif my_serializer.is_valid() and not check_object_if_exists_in_user_cart:
            return Response({'message': 'Вы пытаетесь удалить несуществующий объект в вашей корзине'}, 
                            status=status.HTTP_404_NOT_FOUND)
            
        else:
            return Response(my_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class CheckoutViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        user = request.user
        user_address = models.Address.objects.filter(user=user).first()
        user_cart = models.Cart.objects.filter(user=user)
        cart_total_price = sum([object.price for object in user_cart]) 
        address_serializer = serializers.AddressSerializer(user_address)
        cart_serializer = serializers.CartViewSerializer(user_cart, many=True)
        
        return Response({'Корзина': cart_serializer.data if user_cart else 'Ваша корзина пуста',
                         'Адрес': address_serializer.data if user_address else 'Вы еще не указали свой адрес',
                         'Общая стоимость корзины': cart_total_price}, status=status.HTTP_200_OK)
        
        
class OrderCreateViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]


    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = models.Cart.objects.filter(user=user)
        user_address = models.Address.objects.filter(user=user).first()
        cart_total_price = sum([object.price for object in queryset])
        customer =models.User.objects.filter(username=user).first()
        customer_balance = customer.balance
        
        valid_order = utils.valid_order(first_name=customer.first_name,
                                        last_name=customer.last_name, 
                                        phone=customer.phone)

        if (queryset and user_address) and (customer_balance >= cart_total_price and valid_order):
            order = models.Order.objects.create(user=user, total_price=cart_total_price, address=user_address)
            for queryset_obj in queryset:
                obj = models.OrderService.objects.create(order=order, 
                                                         service=queryset_obj.service, 
                                                         tariff_plan=queryset_obj.tariff_plan,  
                                                         employee=queryset_obj.employee)
                employee_status_change = models.Employee.objects.get(id=queryset_obj.employee.id)
                employee_status_change.busy = True
                employee_status_change.save()
                queryset_obj.delete()
            customer.balance = customer_balance - cart_total_price
            customer.save()

            return Response({'message': 'Ваш заказ успешно оформлен'}, status=status.HTTP_201_CREATED)
        elif not queryset:
            return Response({'message':'Ваша корзина пуста'}, status=status.HTTP_409_CONFLICT)
        elif not user_address:
            return Response({'message': 'Вы еще не указали свой адрес'}, status=status.HTTP_409_CONFLICT)
        elif cart_total_price > customer_balance:
            return Response({'message': 'У вас недостаточно средств'},status=status.HTTP_409_CONFLICT)
        elif valid_order == False:
            return Response({'message': 'У нас недостаточно информации для оформления заказа. Пожалуйста заполните личную информацию'}, 
                            status=status.HTTP_400_BAD_REQUEST)  
    
    def destroy(self, request, *args, **kwargs):
        uuid = self.kwargs['pk']
        user = request.user
        user_order = models.Order.objects.filter(id=uuid, user=user, status__in=['Заказ оформлен', 'Заказ принят']).first()
        customer = models.User.objects.filter(username=user).first()
        if user_order:
            customer.balance += user_order.total_price
            customer.save()
            user_order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_409_CONFLICT)
            

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.OrderSerializer
    
    def get_queryset(self):
        return models.Order.objects.filter(user=self.request.user)
    
        
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        user = models.User.objects.filter(username=request.user).first()
        if user.is_staff:
            employee = models.Employee.objects.get(user=user).id
            employee_orders = models.Order.objects.filter(order_services__employee=employee)
            employee_orders_serializer = serializers.OrderForUserPageSerializer(set(employee_orders), many=True)
            user_serializer = serializers.UserSerializer(user)
            return Response({
                     'employee_orders_serializer': employee_orders_serializer.data}, status=status.HTTP_200_OK)
        else:
            user_serializer = serializers.UserSerializer(user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)


class PaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def post(self, request):
        data = request.data
        user = request.user
        amount = data['amount']
        
        session = stripe.checkout.Session.create(
            line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(amount),
                        'product_data': {
                            'name': 'Оплата'
                        },
                    },   
                    'quantity': 1,             
                }],
                mode='payment',
                success_url=request.build_absolute_uri(),
                cancel_url=request.build_absolute_uri()
            )
        if session:
            session_id = session['id']
            amount_total = session['amount_total']
            user_balance = models.User.objects.filter(username=user).update(balance=amount)
            models.Transaction.objects.create(user=user, session_id=session_id, amount=amount_total)
            return Response({'message': 'Транзакция прошла успешно'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Что-то пошло не так'}, status=status.HTTP_409_CONFLICT)
        
    




    
        
        