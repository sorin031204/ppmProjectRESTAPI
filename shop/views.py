from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .serializers import (
    CategorySerializer, ProductSerializer, CartSerializer,
    CartItemSerializer, OrderSerializer, OrderCreateSerializer
)
from .permissions import IsStoreManagerOrReadOnly, IsOwner


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStoreManagerOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsStoreManagerOrReadOnly]


class CartViewSet(viewsets.ViewSet):
    """
    Gestisce il carrello dell'utente autenticato.
    Ogni utente vede e modifica solo il proprio carrello.
    """
    permission_classes = [IsAuthenticated]

    def _get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def list(self, request):
        cart = self._get_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='items')
    def add_item(self, request):
        cart = self._get_cart(request.user)
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)

        if quantity > product.stock:
            return Response(
                {"error": f"Quantità richiesta ({quantity}) superiore allo stock disponibile ({product.stock})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        cart = self._get_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'store_manager':
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        items = cart.items.all()

        if not items.exists():
            return Response(
                {"error": "Il carrello è vuoto."},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in items:
            if item.quantity > item.product.stock:
                return Response(
                    {"error": f"Stock insufficiente per {item.product.name}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            order = Order.objects.create(user=request.user)
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price
                )
                item.product.stock -= item.quantity
                item.product.save()
            items.delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        if request.user.role != 'store_manager':
            return Response(
                {"error": "Solo lo store manager può aggiornare lo stato dell'ordine."},
                status=status.HTTP_403_FORBIDDEN
            )
        new_status = request.data.get('status')
        if new_status not in dict(Order.Status.choices):
            return Response(
                {"error": "Stato non valido."},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = new_status
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)