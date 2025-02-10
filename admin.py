from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.html import mark_safe
from django.shortcuts import render
from django.contrib import messages
from .models import TempImage, TempProduct
from django.contrib.admin import SimpleListFilter

class TempImagesAdmin(admin.ModelAdmin):
    list_display = ('product', 'sort_order', 'title', 'width', 'height', 'file_size', 'zoom_scale', 'remove_bg', 'remove_wm')
    search_fields = ('product', 'title',)
    list_filter = ('remove_bg', 'remove_wm', 'created_at')
    list_editable = ('zoom_scale', 'remove_bg', 'remove_wm', 'sort_order')

class TempImagesInline(admin.TabularInline):
    model = TempImage
    fields = ('image_preview', 'file', 'sort_order', 'remove_bg', 'remove_wm', 'caption', 'title')
    readonly_fields = ('image_preview', 'file', 'caption')
    extra = 0
    search_fields = ['caption', 'file']

    def image_preview(self, obj):
        if obj.file:
            return mark_safe(f'<img src="{obj.file.url}" style="width: 100px; height: auto;" />')
        return None
    image_preview.short_description = 'Preview'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

class TempProductsAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'title', 'view_images_link',)
    search_fields = ('product_id', 'title',)
    inlines = [TempImagesInline]
    actions = ['mark_images_for_bg_removal', 'mark_images_for_wm_removal']

    def view_images_link(self, obj):
        url = reverse('admin:products_tempproductstable_view_images', args=[obj.product_id])
        return mark_safe(f'<a href="{url}">Посмотреть изображения</a>')

    view_images_link.short_description = 'View Images'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:product_id>/images/', self.admin_site.admin_view(self.view_images), name='products_tempproductstable_view_images'),
        ]
        return custom_urls + urls

    def view_images(self, request, product_id):
        product = TempProduct.objects.get(product_id=product_id)
        products_list = TempProduct.objects.all().order_by("id")
        images = TempImage.objects.filter(product=product).order_by('sort_order')
        
        images_quality_dict = {}
        for image in images:
            if image.width is not None and image.height is not None:
                if image.width + image.height >= 800:
                    images_quality_dict[image.id] = ['Хорошее качество']
                else:
                    images_quality_dict[image.id] = ['Низкое качество']

                aspect_ratio = image.width / image.height
                if 1.5 - 0.5 <= aspect_ratio <= 1.5 + 0.5:
                    images_quality_dict[image.id].append('Размеры хорошо вписываются в сайт')
                else:
                    images_quality_dict[image.id].append('Размеры плохо вписываются в сайт')
            else:
                images_quality_dict[image.id] = ['Недопустимые размеры (отсутствуют)']

        
        if request.method == 'POST':
            if 'delete_selected_images' in request.POST:
                delete_ids = request.POST.getlist('delete_images')
                TempImage.objects.filter(id__in=delete_ids).delete()
                messages.success(request, f'Удалено изображений: {len(delete_ids)}')
                return redirect('admin:products_tempproductstable_view_images', product_id=product.product_id)
    
            for image in images:
                remove_bg_field = f'remove_bg_{image.id}'
                remove_wm_field = f'remove_wm_{image.id}'
                sort_order_field = f'sort_order_{image.id}'
                zoom_scale_field = f'zoom_scale_{image.id}'
    
                if remove_bg_field in request.POST:
                    image.remove_bg = request.POST[remove_bg_field] == 'on'
                else:
                    image.remove_bg = False
    
                if remove_wm_field in request.POST:
                    image.remove_wm = request.POST[remove_wm_field] == 'on'
                else:
                    image.remove_wm = False
                    
                if zoom_scale_field in request.POST:
                    image.zoom_scale = float((request.POST[zoom_scale_field]).replace(',', '.'))
    
                if sort_order_field in request.POST:
                    image.sort_order = int(request.POST[sort_order_field])
    
                image.save()
    
            return redirect('admin:products_tempproductstable_view_images', product_id=product.product_id)
    
        context = {
            'product': product,
            'images': images,
            'title': product.title,
            'products_list': products_list,
            'images_quality_dict': images_quality_dict
        }
        return render(request, 'product_manager/view_images.html', context)


    def has_add_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff

    def mark_images_for_bg_removal(self, request, queryset):
        count = queryset.update(remove_bg=True)
        self.message_user(request, f'{count} images marked for background removal.')
    mark_images_for_bg_removal.short_description = "Mark images for background removal"

    def mark_images_for_wm_removal(self, request, queryset):
        count = queryset.update(remove_wm=True)
        self.message_user(request, f'{count} images marked for watermark removal.')
    mark_images_for_wm_removal.short_description = "Mark images for watermark removal"

admin.site.register(TempProduct, TempProductsAdmin)
admin.site.register(TempImage, TempImagesAdmin)