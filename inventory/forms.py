from django import forms
from .models import Jewelry  # make sure you have a Jewelry model

class JewelryForm(forms.ModelForm):
    class Meta:
        model = Jewelry
        fields = ['name', 'description', 'price', 'image']  # update fields to match your model
# inventory/forms.py
from django import forms
from .models import Jewelry, Banner

class JewelryForm(forms.ModelForm):
    class Meta:
        model = Jewelry
        fields = '__all__'

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['image', 'banner_type', 'title', 'subtitle']
        widgets = {
            'banner_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
