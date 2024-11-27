from django import forms
from django.forms import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .models import AttributeValue


class ProductLineAttributeValueFormSet(BaseInlineFormSet):
    """
    Dynamically filter the dropdowns for attribute values to include only that attributes
    which related to the product type of current product line.

    Ensure no duplicate attributes are in scope of product line at the form level.
    """

    def add_fields(self, form, index):
        super().add_fields(form, index)

        attrs_ids = self.instance.product_type_id.attributes.all().values_list(
            'id', flat=True
        )

        related_attributes_qs = AttributeValue.objects.filter(
            attribute_id__in=attrs_ids
        )

        # Dynamically set the queryset for the 'attribute_value' field
        form.fields['attribute_value'].queryset = related_attributes_qs

    def clean(self):
        super().clean()
        # use a set to track the unique attribute IDs
        attribute_ids = set()

        for form in self.forms:

            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                attribute_value = form.cleaned_data.get('attribute_value')

                if attribute_value and attribute_value.attribute_id:

                    if attribute_value.attribute_id in attribute_ids:

                        raise ValidationError(
                            f'Allowed only one unique attribute name per product line.'
                        )

                    attribute_ids.add(attribute_value.attribute_id)


class ProductLineAttributeValueForm(forms.ModelForm):
    """
    Form for filtering dropdown in the admin page / ProductLine inline
    """

    class Meta:
        model = AttributeValue.product_line_attribute_value.through
        fields = "__all__"
