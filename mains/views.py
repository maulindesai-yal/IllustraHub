from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Min, Count
from mains.models import Illustration ,Category, CartItem,Bid
from authenticate.models import CustomUser
from django.db.models import Count, F, Q, Max
from authenticate.country_choices import COUNTRY_CHOICES
from django.utils.timezone import now,timedelta
from django.http import JsonResponse,HttpResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.urls import reverse
import json
#from .category import Categories
# Create your views here.

def collection_view(request):
    # Get all categories with their first (most recent) illustration
    categories = Category.objects.all()
    category_illustrations = []
    
    for category in categories:
        # Get the first uploaded illustration in this category
        first_illustration = Illustration.objects.filter(
            category=category
        ).order_by('-uploaded_at').first()
        
        if first_illustration:
            category_illustrations.append({
                'category': category,
                'illustration': first_illustration
            })
    
    return render(request, 'main_templates/collection.html', {
        'category_illustrations': category_illustrations
    })

def category_collection_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    # Get illustrators who have uploaded illustrations in this category
    illustrators = CustomUser.objects.filter(
        user_type='illustrator',
        mains_illustrations__category=category
    ).distinct()

    # Create a list of illustrators with their first uploaded illustration in this category
    illustrators_with_illustrations = []
    for illustrator in illustrators:
        first_illustration = Illustration.objects.filter(
            uploaded_by=illustrator,
            category=category
        ).order_by('uploaded_at').first()  # Get the first uploaded illustration

        if first_illustration:
            illustrators_with_illustrations.append({
                'illustrator': illustrator,
                'illustration': first_illustration
            })

    return render(request, 'main_templates/category_collection.html', {
        'category': category,
        'illustrators_with_illustrations': illustrators_with_illustrations
    })

def illustrator_category_collection_view(request, category_id, illustrator_email):
    category = get_object_or_404(Category, id=category_id)
    illustrator = get_object_or_404(CustomUser, email=illustrator_email)
    
    # Get all illustrations by this illustrator in this category
    illustrations = Illustration.objects.filter(
        category=category,
        uploaded_by=illustrator
    ).order_by('-uploaded_at')
    
    return render(request, 'main_templates/illustrator_category_collection.html', {
        'category': category,
        'illustrator': illustrator,
        'illustrations': illustrations
    })

@login_required
def my_artworks_view(request):
    if request.user.user_type != 'illustrator':
        messages.error(request, 'You do not have permission to upload illustrations.')
        return redirect('home')
    
    categories = Category.objects.all() #fetching category from database
    user_artworks = Illustration.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        selling_type = request.POST.get('selling_type')

        # Validate required fields
        if not all([title, description, category_id, image, selling_type]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'main_templates/my_artworks.html', {
                'categories': categories,
                'user_artworks': user_artworks
            })        
        try:
            category = get_object_or_404(Category, id=category_id)
            
            Illustration.objects.create(
                title=title,
                description=description,
                category=category,
                price=price if price else None,
                image=image,
                uploaded_by=request.user,
                selling_type=selling_type 
            )
            
            messages.success(request, 'Illustration uploaded successfully!')
            return redirect('my_artworks')
        
        except Exception as e:
            messages.error(request, f'Error uploading illustration: {str(e)}')
    
    return render(request, 'main_templates/my_artworks.html',{
        'categories': categories,
        'user_artworks': user_artworks
    })

@login_required
def edit_artwork(request, artwork_id):
    artwork = get_object_or_404(Illustration, id=artwork_id, uploaded_by=request.user)
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        selling_type = request.POST.get('selling_type')
        image = request.FILES.get('image')

        try:
            category = get_object_or_404(Category, id=category_id)
            
            artwork.title = title
            artwork.description = description
            artwork.category = category
            artwork.price = price if price else None
            artwork.selling_type = selling_type
            
            if image:
                artwork.image = image
            
            artwork.save()
            messages.success(request, 'Artwork updated successfully!')
            return redirect('my_artworks')
            
        except Exception as e:
            messages.error(request, f'Error updating artwork: {str(e)}')

    return render(request, 'main_templates/edit_artwork.html', {
        'artwork': artwork,
        'categories': categories
    })

def illustrators_view(request):
    illustrators = CustomUser.objects.filter(
        user_type='illustrator'
    ).annotate(
        illustration_count=Count('mains_illustrations')
    ).filter(
        illustration_count__gt=0  # Only get illustrators with at least one illustration
    )

    sort_by = request.GET.get('sort', 'name_asc')
    if sort_by == 'name_asc':
        illustrators = illustrators.order_by('first_name','last_name')
    elif sort_by == 'name_desc':
        illustrators = illustrators.order_by('-first_name','-last_name')
    elif sort_by == 'newest':
        illustrators = illustrators.order_by('-date_joined')
    elif sort_by == 'most_illustrations':
        illustrators = illustrators.order_by('-illustration_count')

    country = request.GET.get('country')
    if country:
        illustrators = illustrators.filter(country=country)

    context = {
        'illustrators': illustrators,
        'country_choices': COUNTRY_CHOICES,
        'current_sort': sort_by,
        'current_country': country
    }
    return render(request ,'main_templates/illustrators.html', context)

@login_required
def illustration_store_view(request):
    illustrations = Illustration.objects.select_related('category')
    return render (request , 'main_templates/illustration_store.html', {
        'illustrations' : illustrations
    })


def illustrator_details_view(request, email):
    illustrator = get_object_or_404(CustomUser, email=email)
    illustrations = Illustration.objects.filter(uploaded_by=illustrator).order_by('-uploaded_at')

    return render(request, 'main_templates/illustrator_details.html', {
        'illustrator': illustrator,
        'illustrations': illustrations
    })

@login_required
def illustration_details_view(request, illustration_id):
    illustration = get_object_or_404(Illustration, id=illustration_id)
    return render(request, 'main_templates/illustration_details.html',{
        'illustration': illustration
    })

def contact_us_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you would typically implement email sending logic
        # For now, just print the message (replace with actual email sending)
        print(f"Contact Form Submission:\nName: {name}\nEmail: {email}\nSubject: {subject}\nMessage: {message}") 
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact_us')
    return render(request, 'main_templates/contact_us.html')    

def about_us_view(request):
    return render(request ,'main_templates/about_us.html')


@login_required
def place_bid(request, illustration_id):
    illustration = get_object_or_404(Illustration, id=illustration_id, is_bidding_active=True)
    if illustration.bidding_end_time < now():
        return JsonResponse({'success': False, 'error': "Bidding has ended."})
    
    bid_amount = float(request.POST.get('bid_amount', 0))
    highest_bid = illustration.bids.first()

    if bid_amount <= (highest_bid.amount if highest_bid else illustration.price):
        return JsonResponse({'success': False, 'error': "Your bid must be higher."})
    
    new_bid = Bid.objects.create(illustration=illustration, user=request.user, amount=bid_amount)
    async_to_sync(channel_layer.group_send)(
        f'bid_{illustration.id}',
        {
            'type': 'bid_update',
            'bidder': request.user.username,
            'bid_amount': str(new_bid.amount)
        }
    )
    return JsonResponse({'success': True, 'bidder': request.user.username, 'bid_amount': new_bid.amount})

channel_layer = get_channel_layer()

@login_required
def start_bidding(request, illustration_id):
    """Allows illustrators to start live bidding for an illustration."""
    illustration = get_object_or_404(Illustration, id=illustration_id)
    
    # Ensure only the illustrator who uploaded the illustration can start bidding
    if request.user != illustration.uploaded_by:
        messages.error(request, "You do not have permission to start bidding for this illustration.")
        return redirect('illustration_details', illustration_id=illustration.id)
    
    if illustration.is_bidding_active:
        messages.warning(request, "Bidding is already active.")
    else:
        illustration.start_bidding()
        messages.success(request, "Live bidding started!")
    return redirect(reverse('live_bidding'))


def end_bidding(request, illustration_id):
    """End bidding early for an illustration"""
    illustration = get_object_or_404(Illustration, id=illustration_id, uploaded_by=request.user)
    if not illustration.is_bidding_active:
        messages.warning(request, "Bidding is not active.")
    else:
        illustration.end_bidding()
        messages.success(request, "Bidding has ended.")

    return redirect('illustration_details', illustration_id=illustration.id)

@login_required
def mark_as_sold(request, illustration_id):
    illustration = get_object_or_404(Illustration, id=illustration_id, uploaded_by=request.user)
    highest_bid = illustration.bids.first()
    if highest_bid:
        illustration.mark_as_sold(highest_bid.user, highest_bid.amount)
        messages.success(request, f"Sold to {highest_bid.user.username} for ${highest_bid.amount}!")
    else:
        messages.warning(request, "No bids were placed.")

    return redirect('illustration_details', illustration_id=illustration.id)

@login_required
def buy_now(request, illustration_id):
    illustration = get_object_or_404(Illustration, id=illustration_id)
    # Redirect to checkout (or implement direct purchase logic)
    return redirect('checkout_page', illustration_id=illustration.id)


@login_required
def checkout_page(request, illustration_id):
    illustration = get_object_or_404(Illustration, id=illustration_id)


    user = request.user
    user_profile = CustomUser.objects.get(email=user.email)

    if request.method == 'POST':
        # Get user input
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        country = request.POST.get('country')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        payment_method = request.POST.get('payment_method')

        # Here, you would typically save the order in the database
        # Example: Order.objects.create(user=request.user, illustration=illustration, ...)

        # Redirect to a success page
        return redirect('order_success')

    return render(request, 'main_templates/checkout.html', {
        'illustration': illustration,
        'user_profile': user_profile
    })

def order_success(request):
    return render(request, 'main_templates/order_success.html')

@login_required
def live_bidding_view(request):
    illustrations = Illustration.objects.filter(selling_type='bid').select_related('uploaded_by')

    illustration_data = [
        {
            'id': illustration.id,
            'title': illustration.title,
            'price': illustration.price,
            'image': illustration.image.url,
            'illustrator_name': illustration.uploaded_by.get_full_name(),
            'is_bidding_active': illustration.is_bidding_active,
            'bidding_end_time': illustration.bidding_end_time,
        }
        for illustration in illustrations
    ]

    return render(request, 'main_templates/live_bidding.html', {'illustrations': illustration_data})

@login_required
def illustration_bidding_view(request, illustration_id):
    illustration = get_object_or_404(Illustration, id=illustration_id)
    bids = Bid.objects.filter(illustration=illustration).order_by('-timestamp')
    highest_bid = bids.first()
    bid_count = bids.count()

    return render(request, 'main_templates/illustration_bidding.html', {
        'illustration': illustration,
        'bids': bids,
        'highest_bid': highest_bid,
        'bid_count': bid_count,
    })

@login_required
def bidding_history(request, illustration_id):
    illustration = get_object_or_404(Illustration, id=illustration_id)
    bids = Bid.objects.filter(illustration=illustration).order_by('-timestamp')

    return render(request, 'main_templates/bidding_history.html', {
        'illustration': illustration,
        'bids': bids
    })

@login_required
def add_to_cart(request, illustration_id):
    illustration = get_object_or_404(Illustration, id=illustration_id)

    cart_item, created = CartItem.objects.get_or_create(
        user = request.user,
        illustration=illustration,
        defaults={ 'quantity' : 1 }
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{illustration.title} added to cart successfully.")
    return redirect('illustrator_category_collection', illustration.category.id, illustration.uploaded_by.email)


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)

    return render(request, 'main_templates/your_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('view_cart')

@login_required
def delete_artwork(request, artwork_id):
    artwork = get_object_or_404(Illustration, id=artwork_id, uploaded_by=request.user)
    
    if request.method == 'POST':
        artwork.delete()
        messages.success(request, 'Artwork deleted successfully!')
        return redirect('my_artworks')
    
    return render(request, 'main_templates/delete_artwork.html', {
        'artwork': artwork
    })