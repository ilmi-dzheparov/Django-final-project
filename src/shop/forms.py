from django import forms
from shop.models import Review


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['text'].widget.attrs.update({
            'name': "review",
            'id': "review",
            'placeholder': 'Отзывы',
            'class': 'form-textarea'
        })
        self.fields['text'].label = False