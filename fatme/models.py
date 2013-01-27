from couchdbkit.ext.django.schema import *
from datetime import date

class Weight(Document):
    date = DateProperty(default=date.today(), required=True)
    weight = FloatProperty(required=True)

    def save(self, *args, **kwargs):
        self._id = self.date.isoformat()
        super(Weight, self).save(*args, **kwargs)

class Start(Document):
    date = DateProperty(default=date.today(), required=True)
    start = FloatProperty(required=True)
    goal = FloatProperty(required=True)
    height = FloatProperty(required=True)
    age = IntegerProperty(required=True)
    final_day = DateProperty(required=True)

    def save(self, *args, **kwargs):
        self._id = u's'+self.date.isoformat()
        super(Start, self).save(*args, **kwargs)
