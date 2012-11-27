from django.shortcuts import render
from django.template import RequestContext
from fatme.forms import WeightForm
from fatme.models import Weight
from datetime import date

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

    goal = 89.9

    return render(request,
                  "home.html",
                  {
		   "weights": weights,
                   "goal": goal,
                  },
                  context_instance=RequestContext(request))

