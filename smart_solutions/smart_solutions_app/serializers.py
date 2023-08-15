from rest_framework import serializers
from rest_framework.fields import empty
from . import models
from django.db.models import Count, Q, Sum, F, IntegerField

class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()
    
    
    class Meta:
        model = models.User
        fields = ('email', 'username', 'password', 'password2', 'phone', 'first_name', 'last_name')
 
    def save(self, *args, **kwargs):

        user = models.User(
            email=self.validated_data.get('email', None), 
            username=self.validated_data.get('username'),
            phone=self.validated_data.get('phone', None),
            first_name=self.validated_data.get('first_name', None),
            last_name=self.validated_data.get('last_name', None)
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({password: "Пароль не совпадает"})
        user.set_password(password)
        user.save()
        return user
    

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Service
        fields = '__all__'
        
class ServiceTariffPlanSerializer(serializers.ModelSerializer):
    in_cart = serializers.SerializerMethodField()
    
    class Meta:
        model = models.ServiceTariffPlan
        fields = '__all__'
        
    
    def get_in_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            service_price_list_qs = models.ServiceTariffPlan.objects.annotate(
                in_cart=Count('cart_tariff_plans', filter=Q(cart_tariff_plans__user=user))
            )
            service_price_list_obj = service_price_list_qs.get(id=obj.id)
            return True if service_price_list_obj.in_cart > 0 else False
        else:
            return False
        

class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ServiceGallery
        fields = ('image',)
        
    

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        exclude = ('user',)
        
    def create(self, validated_data):
        address, _ = models.Address.objects.update_or_create(
            user=validated_data.get('user'),
            defaults={
                'address': validated_data.get('address'),
                'floor': validated_data.get('floor', None),
                'entrance': validated_data.get('entrance', None),
                'intercom': validated_data.get('intercom', None),
                'apartment': validated_data.get('apartment', None)
            }
        )
        
        return address
       
    
class CreateAndRetrieveApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Application
        exclude = ('user',)
        
        
class ListApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Application
        fields = ('id','first_name', 'last_name', 'status')  

        
class ReviewFilterSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)
    

class RecursiveReviewSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data  


class ReviewSerializer(serializers.ModelSerializer):
    children = RecursiveReviewSerializer(many=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    
    class Meta:
        list_serializer_class = ReviewFilterSerializer
        model = models.Review
        fields = ('id','user', 'text', 'created_date', 'children')
        
        
        
class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        exclude = ('user',)
        

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        exclude = ('user',)
        
    def create(self, validated_data):
        employee_id = validated_data.get('employee')
        user=validated_data.get('user')

        rating, _ = models.Rating.objects.update_or_create(
            user=user,
            employee_id=employee_id,
            defaults={
                'star': validated_data.get('star', None)
            }
        )
        return rating
            
        
    
class EmployeeImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmployeeGallery
        fields = ('image',)

        
class EmployeeSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    employee_images = EmployeeImagesSerializer(many=True)
    employee_reviews = ReviewSerializer(many=True)
    
    class Meta:
        model = models.Employee
        fields = (
            'id',
            'first_name', 
            'last_name', 
            'characteristics', 
            'phone',
            'average_rating',
            'employee_images',
            'employee_reviews'
        )

        
    def get_average_rating(self, obj):
        query = models.Employee.objects.all().annotate(
            average_rating=Sum(F('employee_rating__star'), output_field=IntegerField()) / Count('employee_rating')
        )
        rating = query.get(id=obj.id)
        return rating.average_rating
        

        
        
class ServiceDetailSerializer(serializers.ModelSerializer):
    tariff_plan = ServiceTariffPlanSerializer(many=True)
    images = ServiceImageSerializer(many=True)
    employees = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Service
        fields = '__all__'
        
        
    def get_employees(self, obj):
        employees = obj.employees.filter(service_id=obj.id, busy=False)
        return EmployeeSerializer(employees, many=True).data
               

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        exclude = ('user',)
        
class CartViewSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()
    service = serializers.SlugRelatedField(slug_field='title', read_only=True)
    tariff_plan = serializers.SlugRelatedField(slug_field='description', read_only=True)
    
    class Meta:
        model = models.Cart
        exclude = ('user',)
        

class OrderServiceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()
    service = serializers.SlugRelatedField(slug_field='title', read_only=True)
    tariff_plan = serializers.SlugRelatedField(slug_field='description', read_only=True)
    
    class Meta:
        model = models.OrderService
        fields = ('service', 'tariff_plan', 'employee')
        
        
class OrderSerializer(serializers.ModelSerializer):
    order_services = OrderServiceSerializer(many=True)
    address = AddressSerializer()
    
    class Meta:
        model = models.Order
        exclude = ('user',)
        
        
class OrderForUserPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ('id', 'status', 'total_price')
        

        
class UserSerializer(serializers.ModelSerializer):
    user_address = AddressSerializer(many=True)
    user_orders = OrderForUserPageSerializer(many=True)
    class Meta:
        model = models.User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'phone',
                  'email',
                  'balance',
                  'user_address',
                  'user_orders')
        