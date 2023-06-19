from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from .constants import PaymentStatus
from django.shortcuts import redirect, reverse

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

@csrf_exempt
def payments(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            result = razorpay_client.utility.verify_payment_signature(params_dict)

            if result is not None:
                try:
                    order = Order.objects.get(user=request.user, is_ordered=False, order_number=razorpay_order_id)

                    # Store transaction details inside Payment model
                    payment = Payment(
                        user=request.user,
                        payment_id=payment_id,
                        payment_method='Razorpay',
                        amount_paid=order.order_total,
                        status=PaymentStatus.SUCCESS,
                    )
                    payment.save()

                    order.payment = payment
                    order.is_ordered = True
                    order.save()

                    # Move the cart items to Order Product table
                    cart_items = CartItem.objects.filter(user=request.user)

                    for item in cart_items:
                        orderproduct = OrderProduct()
                        orderproduct.order_id = order.id
                        orderproduct.payment = payment
                        orderproduct.user_id = request.user.id
                        orderproduct.product_id = item.product_id
                        orderproduct.quantity = item.quantity
                        orderproduct.product_price = item.product.product_price
                        orderproduct.ordered = True
                        orderproduct.save()

                        cart_item = CartItem.objects.get(id=item.id)
                        product_variation = cart_item.variations.all()
                        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                        orderproduct.variations.set(product_variation)
                        orderproduct.save()

                        # Reduce the quantity of the sold products
                        product = Product.objects.get(product_id=item.product_id)
                        product.product_stock -= item.quantity
                        product.save()

                    # Clear cart
                    CartItem.objects.filter(user=request.user).delete()
                    return redirect(reverse('order_complete') + '?order_number='+order.order_number+'&payment_id='+payment.payment_id)
                    # return redirect('order_complete' + '?order_number='+order.order_number+'&payment_id='+payment.payment_id)
                except Exception as e:
                    print(f"Exception in Payment: {e}")

            else:
                return HttpResponse("Payment has been failed")
        except Exception as e:
            print(f"Exception in Payment: {e}")





def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.product_price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            currency = 'INR'
            amount = int(grand_total) * 100  # Rs. 200

            # Create a Razorpay Order
            razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                               currency=currency,
                                                               payment_capture='1'))
            razorpay_order_id = razorpay_order['id']
            data.order_number = razorpay_order_id
            data.save()
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=razorpay_order_id)
            context = {}

            callback_url = f"http://{request.get_host()}/orders/payments/"
            context['order'] = order
            context['cart_items'] = cart_items
            context['total'] = total
            context['tax'] = tax
            context['grand_total'] = grand_total
            context['razorpay_order_id'] = razorpay_order_id
            context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
            context['razorpay_amount'] = amount
            context['currency'] = currency
            context['callback_url'] = callback_url

            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
