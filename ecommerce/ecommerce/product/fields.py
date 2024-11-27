from django.db import models
from django.core import checks
from django.db.models import Max
from django.core.exceptions import ValidationError


class OrderingField(models.PositiveIntegerField):
    description = 'Ordering model instances in scope of related FK attribute'

    def __init__(self, unique_for_field=None, *args, **kwargs):
        self.unique_for_field = unique_for_field
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_for_field_attributes(),
        ]

    def _check_for_field_attributes(self, **kwargs):
        if self.unique_for_field is None:
            return [
                checks.Error('OrderingField must define "unique_for_field" attribute.')
            ]
        elif self.unique_for_field not in [
            f.name for f in self.model._meta.get_fields()
        ]:
            return [
                checks.Error('OrderingField does not match an existing model field.')
            ]

        return []

    def pre_save(self, model_instance, add):
        related_field = getattr(model_instance, self.unique_for_field)
        # queryset = ProductLine.objects.filter(product_id=product)
        queryset = model_instance.__class__.objects.filter(
            **{self.unique_for_field: related_field}
        )
        value = getattr(model_instance, self.attname)

        if value is None:
            max_order_number = queryset.aggregate(Max(self.attname)).get(
                f'{self.attname}__max'
            )

            if max_order_number is None:
                max_order_number = 0

            setattr(model_instance, self.attname, max_order_number + 1)

        else:
            # logic of checking uniqueness
            _pk_field = model_instance._meta.pk.name

            if (
                queryset.filter(**{self.attname: value})
                .exclude(**{_pk_field: getattr(model_instance, _pk_field)})
                .exists()
            ):
                raise ValidationError(
                    {
                        self.attname: f'The display order "{value}" is already in use. Please choose a different value.'
                    }
                )
        return super().pre_save(model_instance, add)
