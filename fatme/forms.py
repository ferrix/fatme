from fatme.models import Weight
from couchdbkit.ext.django.forms import *

class WeightForm(DocumentForm):
    class Meta:
        document = Weight
