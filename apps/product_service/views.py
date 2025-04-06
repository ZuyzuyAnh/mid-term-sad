# apps/product_service/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category, Product, ProductImage, ProductAttribute, ProductAttributeValue, Inventory
from .serializers import ProductSerializer, CategorySerializer
from .forms import ProductForm, ProductImageForm, InventoryForm


def product_list(request):
    """Hiển thị danh sách sản phẩm"""
    products = Product.objects.filter(status='published').order_by('-created_at')

    # Lọc theo danh mục
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Lọc theo giá
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sắp xếp
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'name_asc':
        products = products.order_by('name')

    # Phân trang
    paginator = Paginator(products, 12)  # 12 sản phẩm mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Lấy danh mục cho filter
    categories = Category.objects.filter(status=True)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    return render(request, 'product_service/product_list.html', context)


def product_detail(request, pk):
    """Xem chi tiết sản phẩm theo ID"""
    product = get_object_or_404(Product, pk=pk, status='published')
    return _render_product_detail(request, product)


def product_detail_by_slug(request, slug):
    """Xem chi tiết sản phẩm theo slug"""
    product = get_object_or_404(Product, slug=slug, status='published')
    return _render_product_detail(request, product)


def _render_product_detail(request, product):
    """Helper function để render trang chi tiết sản phẩm"""
    images = product.images.all()
    primary_image = images.filter(is_primary=True).first() or images.first()

    # Lấy các thuộc tính sản phẩm
    attributes = ProductAttributeValue.objects.filter(product=product).select_related('attribute')

    # Lấy sản phẩm liên quan
    related_products = Product.objects.filter(
        status='published',
        category=product.category
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'primary_image': primary_image,
        'images': images,
        'attributes': attributes,
        'related_products': related_products,
    }
    return render(request, 'product_service/product_detail.html', context)


def product_search(request):
    """Tìm kiếm sản phẩm"""
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            status='published'
        )
    else:
        products = Product.objects.none()

    # Phân trang
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'page_obj': page_obj,
    }
    return render(request, 'product_service/search_results.html', context)


def category_list(request):
    """Hiển thị danh sách danh mục"""
    categories = Category.objects.filter(status=True, parent=None)
    return render(request, 'product_service/category_list.html', {'categories': categories})


def category_detail(request, pk):
    """Xem chi tiết danh mục theo ID"""
    category = get_object_or_404(Category, pk=pk, status=True)
    return _render_category_detail(request, category)


def category_detail_by_slug(request, slug):
    """Xem chi tiết danh mục theo slug"""
    category = get_object_or_404(Category, slug=slug, status=True)
    return _render_category_detail(request, category)


def _render_category_detail(request, category):
    """Helper function để render trang chi tiết danh mục"""
    # Lấy danh sách sản phẩm thuộc danh mục
    products = Product.objects.filter(
        Q(category=category) | Q(category__parent=category),
        status='published'
    )

    # Phân trang
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Lấy danh mục con
    subcategories = Category.objects.filter(parent=category, status=True)

    context = {
        'category': category,
        'page_obj': page_obj,
        'subcategories': subcategories,
    }
    return render(request, 'product_service/category_detail.html', context)


@login_required
def vendor_products(request):
    """Danh sách sản phẩm của người bán"""
    products = Product.objects.filter(seller_id=request.user.id).order_by('-created_at')

    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        products = products.filter(status=status)

    # Phân trang
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status,
    }
    return render(request, 'product_service/vendor/products.html', context)


@login_required
def product_create(request):
    """Tạo sản phẩm mới"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller_id = request.user.id
            product.save()

            # Tạo inventory
            Inventory.objects.create(
                product=product,
                quantity=form.cleaned_data.get('initial_quantity', 0)
            )

            messages.success(request, "Sản phẩm đã được tạo thành công!")
            return redirect('product_service:product_update', pk=product.pk)
        else:
            messages.error(request, "Tạo sản phẩm không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = ProductForm()

    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'product_service/vendor/product_form.html', context)


@login_required
def product_update(request, pk):
    """Cập nhật sản phẩm"""
    product = get_object_or_404(Product, pk=pk, seller_id=request.user.id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Sản phẩm đã được cập nhật!")
            return redirect('product_service:vendor_products')
        else:
            messages.error(request, "Cập nhật sản phẩm không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = ProductForm(instance=product)

    # Lấy hình ảnh sản phẩm
    images = product.images.all()

    # Lấy thông tin inventory
    inventory = Inventory.objects.get_or_create(product=product)[0]

    context = {
        'form': form,
        'product': product,
        'images': images,
        'inventory': inventory,
        'is_edit': True,
    }
    return render(request, 'product_service/vendor/product_form.html', context)


@login_required
def product_delete(request, pk):
    """Xóa sản phẩm"""
    product = get_object_or_404(Product, pk=pk, seller_id=request.user.id)

    if request.method == 'POST':
        product.status = 'discontinued'
        product.save()
        messages.success(request, "Sản phẩm đã được xóa!")
        return redirect('product_service:vendor_products')

    return render(request, 'product_service/vendor/product_delete.html', {'product': product})


@login_required
def inventory_list(request):
    """Quản lý tồn kho"""
    inventory_items = Inventory.objects.filter(
        product__seller_id=request.user.id
    ).select_related('product').order_by('product__name')

    # Lọc theo tồn kho thấp
    low_stock = request.GET.get('low_stock')
    if low_stock:
        inventory_items = inventory_items.filter(quantity__lte=F('threshold_quantity'))

    # Phân trang
    paginator = Paginator(inventory_items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'low_stock_filter': low_stock,
    }
    return render(request, 'product_service/vendor/inventory_list.html', context)


@login_required
def inventory_update(request, pk):
    """Cập nhật tồn kho"""
    inventory = get_object_or_404(
        Inventory,
        pk=pk,
        product__seller_id=request.user.id
    )

    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            messages.success(request, "Thông tin tồn kho đã được cập nhật!")
            return redirect('product_service:inventory_list')
        else:
            messages.error(request, "Cập nhật tồn kho không thành công. Vui lòng kiểm tra lại thông tin.")
    else:
        form = InventoryForm(instance=inventory)

    context = {
        'form': form,
        'inventory': inventory,
        'product': inventory.product,
    }
    return render(request, 'product_service/vendor/inventory_update.html', context)


def attribute_list(request):
    """Danh sách thuộc tính sản phẩm"""
    attributes = ProductAttribute.objects.all().order_by('name')
    return render(request, 'product_service/attributes.html', {'attributes': attributes})


def attribute_detail(request, pk):
    """Chi tiết thuộc tính sản phẩm"""
    attribute = get_object_or_404(ProductAttribute, pk=pk)
    # Lấy danh sách sản phẩm có thuộc tính này
    product_values = ProductAttributeValue.objects.filter(attribute=attribute).select_related('product')
    context = {
        'attribute': attribute,
        'product_values': product_values,
    }
    return render(request, 'product_service/attribute_detail.html', context)


def product_attributes(request, pk):
    """Thuộc tính của sản phẩm"""
    product = get_object_or_404(Product, pk=pk, status='published')
    attributes = ProductAttributeValue.objects.filter(product=product).select_related('attribute')
    context = {
        'product': product,
        'attributes': attributes,
    }
    return render(request, 'product_service/product_attributes.html', context)


@api_view(['GET'])
def trending_products(request):
    """API endpoint để lấy sản phẩm thịnh hành"""
    products = Product.objects.filter(status='published', featured=True)[:8]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def new_arrivals(request):
    """API endpoint để lấy sản phẩm mới"""
    products = Product.objects.filter(status='published').order_by('-created_at')[:8]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def discounted_products(request):
    """API endpoint để lấy sản phẩm giảm giá"""
    products = Product.objects.filter(
        status='published',
        discount_price__isnull=False
    ).exclude(discount_price=0).order_by('-discount_price')[:8]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)