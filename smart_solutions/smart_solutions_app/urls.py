from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterUserView.as_view({'post': 'create'}), name='register'),
    path('services/', views.ServiceViewSet.as_view({'get': 'list'})),
    path('services/<int:pk>/', views.ServiceViewSet.as_view({'get': 'retrieve'})),
    
    path('address/', views.AddressViewSet.as_view({'post': 'create'})),
    
    path('application/', views.ApplicationViewSet.as_view({'post': 'create'})),
    path('my-applications/', views.ApplicationViewSet.as_view({'get': 'list'})),
    path('my-applications/<int:pk>/', views.ApplicationViewSet.as_view({'get': 'retrieve'})),
    
    path('employee/<int:pk>/', views.EmployeeViewSet.as_view({'get': 'retrieve'})),

    path('review/employee/<int:employee_id>/', views.CreateReviewViewSet.as_view({'post': 'create'})),  
    path('review/children/<int:review_id>/', views.CreateReviewViewSet.as_view({'post': 'create'})),
    path('review/update/<int:pk>/', views.CreateReviewViewSet.as_view({'patch': 'partial_update'})),
    path('review/delete/<int:pk>/', views.CreateReviewViewSet.as_view({'delete': 'destroy'})),

    path('rating/<int:employee_id>/', views.RatingViewSet.as_view({'post': 'create'})),
    
    path('cart/add/', views.CartViewSet.as_view({'post': 'create'})),
    path('cart/delete/', views.CartViewSet.as_view({'delete': 'destroy'})),
    path('cart/delete/all/', views.CartViewSet.as_view({'delete': 'destroy'})),
    path('cart/', views.CartViewSet.as_view({'get': 'list'})),
    
    path('checkout/', views.CheckoutViewSet.as_view({'get': 'list'})),
    path('order/create/', views.OrderCreateViewSet.as_view({'get': 'list'})),
    path('order/cancel/<uuid:pk>/', views.OrderCreateViewSet.as_view({'delete': 'destroy'})),
    path('order/', views.OrderViewSet.as_view({'get': 'list'})),
    
    path('account/', views.UserViewSet.as_view({'get': 'list'})),
    
    path('payment/', views.PaymentView.as_view())
 
]
'''

    TODO убрать permissions для добавления товара в корзину и для показа моей корзины--------0
    TODO служба поддержки, ----------0
    TODO Фильтрация статуса заказов у пользователя -- 0           
''' 
