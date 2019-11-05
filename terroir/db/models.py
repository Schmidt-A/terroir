from schematics.exceptions import ValidationError
from schematics.models import Model
from schematics.types import (FloatType, IntType, ListType, ModelType,
                              StringType, URLType)


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
    upc = IntType()
    producer = StringType()
    price = FloatType()
    country = StringType()
    websites = ListType(URLType)
    profile = ListType(StringType)
    description = StringType()
    image = URLType()
    stores = ListType(StringType)
