from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_id', 
            'product_name', 
            'product_image', 
            'company', 
            'product_description', 
            'quantity_in_stock', 
            'sell_price'
        ]
        widgets = {
            'product_description': forms.Textarea(attrs={'rows': 4}),
            'product_id': forms.TextInput(attrs={'readonly': False}), # Will be handled in view for edit
        }

    def __init__(self, *args, **kwargs):
        is_edit = kwargs.pop('is_edit', False) # Get is_edit flag if passed
        super().__init__(*args, **kwargs)
        if is_edit and self.instance and self.instance.pk:
            self.fields['product_id'].widget.attrs['readonly'] = True