from django.shortcuts import render, redirect
from item.models import Category, Item
from .models import Cart, CartItem
from .forms import SignupForm
from django.http import JsonResponse
from django.contrib.auth import logout
from django.http import HttpResponseBadRequest
import json
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    items = Item.objects.filter(isSold=False).order_by('-createdAt')[:6]
    categories = Category.objects.all()
    
    cart = None
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
    
    return render(request, 'core/index.html', {
        'items': items,
        'categories': categories,
        'cart': cart,
    })

def contact(request):
    return render(request, 'core/contact.html')

def signup(request):
    # Check if the form is submitted
    if request.method == 'POST':
        # Take all the data from the form and save it to the database
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
    else:
         form = SignupForm()
         
    return render(request, 'core/signup.html', {'form': form})

def logoutView(request):
    logout(request)
    return redirect('core:index')  # Redirect to your desired page after logout

def cart(request):
    
    cart = None
    cartItems = []
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
        cartItems = cart.cartItems.all()
        
        # Calcola il prezzo totale per ogni elemento nel carrello
        for cartItem in cartItems:
            cartItem.total_price = cartItem.quantity * cartItem.item.price
    
    context = {'cart': cart, 'cartItems': cartItems}
    
    return render(request, 'core/cart.html', context)

def addToCart(request):
    data = json.loads(request.body)
    item_id = data['id']
    item = Item.objects.get(id=item_id)
    
    cart = None
    numItem = 0
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, completed=False)
        cartitem, created = CartItem.objects.get_or_create(cart=cart, item=item)
        cartitem.quantity += 1
        cartitem.save()
        
        numItem = cart.numOfItems
        
        print(cartitem)
    
    return JsonResponse(numItem, safe=False)


@login_required
def removeFromCart(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        item_id = data['id']
        
        try:
            item = Item.objects.get(id=item_id)
            cart_item = CartItem.objects.get(cart=request.user.cart, item=item)
            
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
            
            cart = Cart.objects.get(user=request.user, completed=False)
            num_items = cart.numOfItems
            
            return JsonResponse(num_items, safe=False)
        
        except (Item.DoesNotExist, CartItem.DoesNotExist):
            return HttpResponseBadRequest("Invalid item ID or cart item does not exist.")
    
    return HttpResponseBadRequest("Invalid request.")

