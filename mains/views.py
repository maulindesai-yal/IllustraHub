from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Count
from mains.models import Illustration ,Category, CartItem
from authenticate.models import CustomUser
from authenticate.country_choices import COUNTRY_CHOICES
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

        # Validate required fields
        if not all([title, description, category_id, image]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'main_templates/my_artworks.html', {
                'categories': categories,
                'user_artworks': user_artworks
            })        
        try:

            if not category_id:
                messages.error(request, 'Invalid category selection. Please try again.')
                return render(request, 'main_templates/my_artworks.html', {
                    'categories': categories,
                    'user_artworks': user_artworks
                })  

            category = get_object_or_404(Category, id=category_id)
            
            Illustration.objects.create(
                title=title,
                description=description,
                category=category,
                price=price if price else None,
                image=image,
                uploaded_by=request.user
            )
            
            messages.success(request, 'Illustration uploaded successfully!')
            return redirect('my_artworks')
        
        except Exception as e:
            messages.error(request, f'Error uploading illustration: {str(e)}')
    
    return render(request, 'main_templates/my_artworks.html',{
        'categories': categories,
        'user_artworks': user_artworks
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
    return redirect('illustration_store')


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