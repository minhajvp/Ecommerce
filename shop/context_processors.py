from .models import Cart

def cart_context(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.cart_items.all()
        total_price = cart.total_price()

        for item in cart_items:
            item.row_total = item.product.price * item.quantity

        return {
            'cart_items': cart_items,
            'total_price': total_price,
        }
    else:
        # For unauthenticated users, return an empty cart context
        return {
            'cart_items': [],
            'total_price': 0,
        }
