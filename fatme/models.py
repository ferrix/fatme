from couchdbkit.ext.django.schema import *
from datetime import date

class Weight(Document):
    date = DateProperty(default=date.today(), required=True)
    weight = FloatProperty(required=True)

    def save(self, *args, **kwargs):
        self._id = self.date.isoformat()
        super(Weight, self).save(*args, **kwargs)
