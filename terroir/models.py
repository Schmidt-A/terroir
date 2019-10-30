from schematics.exceptions import ValidationError
from schematics.models import Model
from schematics.types import (FloatType, ListType, ModelType, StringType,
                              URLType)


class WineType(StringType):
    def validate_content(self, value):
        wine_types = ['red', 'rose', 'sparkling', 'white']
        if value.lower() not in wine_types:
            raise ValidationError(
                f'Wine _type must be one of: {", ".join(wine_types)}')

class Grape(Model):
    name = StringType(required=True)
    _type = WineType()

class Wine(Model):
    name = StringType(required=True)
    grape = ModelType(Grape, required=True)
    price = FloatType()
    lc_website = URLType(required=True)
