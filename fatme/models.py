from couchdbkit.ext.django.schema import *
from datetime import date

class Weight(Document):
    date = DateProperty(default=date.today, required=True)
    weight = FloatProperty(required=True)

    def save(self, *args, **kwargs):
        if not self._id:
            self._id = self.date.isoformat()
        super(Weight, self).save(*args, **kwargs)

class Start(Document):
    date = DateProperty(default=date.today, required=True)
    weight = FloatProperty(required=True)
    goal = FloatProperty(required=True)
    height = FloatProperty(required=True)
    age = IntegerProperty(required=True)
    final_day = DateProperty(required=True)
    name = StringProperty(required=True)
    picture = StringProperty(required=True)

    def save(self, *args, **kwargs):
        if not self._id:
            self._id = u's'+self.date.isoformat()
        super(Start, self).save(*args, **kwargs)
