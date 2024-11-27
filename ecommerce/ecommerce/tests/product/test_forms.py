import pytest

from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory

from collections import Counter

from ecommerce.product.models import (
    ProductLine,
    ProductLineAttributeValue,
)
from ecommerce.product.forms import (
    ProductLineAttributeValueForm,
    ProductLineAttributeValueFormSet,
)
from ecommerce.tests.factories import (
    ProductLineFactory,
    ProductTypeFactory,
    AttributeFactory,
    AttributeValueFactory,
)


@pytest.mark.django_db
class TestProductLineAttributeValueFormSet:
    def setup_method(self):
        # Create attributes and attribute values
        self.attribute1 = AttributeFactory(name="Color")
        self.attribute2 = AttributeFactory(name="Size")
        self.attribute3 = AttributeFactory(name="Material")

        self.attribute_value1 = AttributeValueFactory(
            value="Red", attribute_id=self.attribute1
        )
        self.attribute_value2 = AttributeValueFactory(
            value="Large", attribute_id=self.attribute2
        )
        self.attribute_value3 = AttributeValueFactory(
            value="Fabric", attribute_id=self.attribute3
        )

        # Create product type and assign attributes
        self.product_type = ProductTypeFactory(
            type_name='TypeA',
            attributes=[self.attribute1, self.attribute2, self.attribute3],
        )

        # Create product line linked to product type
        self.product_line = ProductLineFactory(product_type_id=self.product_type)

    def test_dynamic_queryset_dropdown(self):
        """
        Test if the `attribute_value` field's queryset is filtered correctly
        based on the attributes of the `product_type`.
        """
        # Inline formset creation
        formset_class = inlineformset_factory(
            ProductLine,
            ProductLineAttributeValue,
            form=ProductLineAttributeValueForm,
            formset=ProductLineAttributeValueFormSet,
            can_delete=True,
        )

        # Initialize
        formset_data = {
            "product_line_attribute_value_pl-TOTAL_FORMS": 3,
            "product_line_attribute_value_pl-INITIAL_FORMS": 0,
            "product_line_attribute_value_pl-MIN_NUM_FORMS": 0,
            "product_line_attribute_value_pl-MAX_NUM_FORMS": 1000,
            "product_line_attribute_value_pl-0-attribute_value": self.attribute_value1.pk,
            "product_line_attribute_value_pl-1-attribute_value": self.attribute_value2.pk,
            "product_line_attribute_value_pl-2-attribute_value": self.attribute_value3.pk,
        }

        formset_instance = formset_class(instance=self.product_line, data=formset_data)

        form = formset_instance.forms[0]
        queryset = form.fields["attribute_value"].queryset

        # Counter compares the contents of two lists irrespective of their order
        assert Counter(queryset) == Counter(
            [
                self.attribute_value1,
                self.attribute_value2,
                self.attribute_value3,
            ]
        )
        # Validate formset
        assert formset_instance.is_valid()
