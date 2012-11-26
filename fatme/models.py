from couchdbkit.ext.django.schema import *
from datetime import date

class Weight(Document):
    date = DateProperty(default=date.today(), required=True)
    weight = FloatProperty(required=True)
