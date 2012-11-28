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
    today = Weight.view("fatme/all_weights", descending=True).first()['weight']

    start = 124.3
    goal = 89.9
    height = 182
    age = 29

    left = today - goal
    done = start - today

    consumption = (66.5+(13.75*today)+(5.003*height)-(6.775*age))

    return render(request,
                  "home.html",
                  {
		   "weights": weights,
                   "goal": goal,
                   "today": today,
                   "left": left,
                   "done": done,
                   "consumption": consumption,
                  },
                  context_instance=RequestContext(request))

