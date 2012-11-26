from django.shortcuts import render
from django.template import RequestContext
from fatme.forms import WeightForm
from fatme.models import Weight

def new_weight(request):
    weight = None
    if request.POST:
        form = WeightForm(request.POST)
        if form.is_valid():
            weight = form.save()
    else:
        form = WeightForm()

    return render(request,
                  "weight.html",
                  {
		   "form": form,
		   "weight": weight,
                  },
                  context_instance=RequestContext(request))

def home(request):

    weights = Weight.view("fatme/all_weights")

    return render(request,
                  "home.html",
                  {
		   "weights": weights,
                  },
                  context_instance=RequestContext(request))

