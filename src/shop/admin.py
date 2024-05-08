from django.contrib import admin
from shop.models import Product, Review, Category

admin.site.register(Product)
admin.site.register(Category)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'author', 'review', 'created_at']
    list_select_related = ['product', 'author']
    search_fields = ('product__name',)
    list_filter = ['created_at']

    def has_add_permission(self, request):
        """
        Метод запрещает создавать комментарии в админ-панели
        """

        return False

    def has_change_permission(self, request, obj=None):
        """
        Метод запрещает изменять комментарии в админ-панели
        """

        return False

    def get_search_results(self, request, queryset, search_term):
        """
        Метод для получения результатов поиска по заданному запросу.
        """

        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset |= self.model.objects.filter(product__name__icontains=search_term)
        return queryset, use_distinct

    def review(self, obj):
        """
        Метод ограничивает длину отображаемых символов до "100"
        """

        return (obj.text[:100] + '...') if len(obj.text) > 100 else obj.text
