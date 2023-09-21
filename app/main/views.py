from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.urls import reverse
from .models import Item, CartItem, Cart
from decimal import Decimal

def home(request):
    items = Item.objects.all()
    return render(request, 'main/home.html', {'items': items})


stripe.api_key = 'sk_test_51Ns71bAATCNTg8fJvTLaMyr1UYuThJpsVqoBnxVED7MZ1UY7J4QMhJR4jQnsTwQE4dbbTf7mKO97J1N0sEhvZcrL00WoHZn9JF'


@csrf_exempt
def get_session_id(request, item_id):
    if request.method == 'GET':
        try:
            item = get_object_or_404(Item, id=item_id)

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': item.currency,
                        'product_data': {
                            'name': item.name,
                            'description': item.description,
                        },
                        'unit_amount': int(item.price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('success')),
                cancel_url=request.build_absolute_uri(reverse('cancel')),
            )


            return JsonResponse({'session_id': session.id})
        except Item.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



def get_item_page(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
        return render(request, 'main/item_page.html', {'item': item})
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)


def success_view(request):
    return render(request, 'main/success.html')

def cancel_view(request):
    return render(request, 'main/cancel.html')


def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, item=item)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')


def cart_view(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)

    if request.method == 'POST' and request.POST.get('clear_cart') == '1':
        CartItem.objects.filter(cart=cart).delete()
        return redirect('cart')

    cart_items = CartItem.objects.filter(cart=cart)

    total_price = Decimal('0')

    for cart_item in cart_items:
        cart_item.subtotal = cart_item.quantity * cart_item.item.price
        total_price += cart_item.subtotal

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(request, 'main/cart.html', context)




@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            user = request.user
            cart, created = Cart.objects.get_or_create(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            line_items = []
            total_price = Decimal('0')

            for cart_item in cart_items:
                item_unit_amount = int(cart_item.item.price * 100)
                line_items.append({
                    'price_data': {
                        'currency': cart_item.item.currency,
                        'product_data': {
                            'name': cart_item.item.name,
                            'description': cart_item.item.description,
                        },
                        'unit_amount': item_unit_amount,
                    },
                    'quantity': cart_item.quantity,
                })
                total_price += cart_item.quantity * cart_item.item.price

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri(reverse('success')),
                cancel_url=request.build_absolute_uri(reverse('cancel')),
            )

            return JsonResponse({'session_id': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
