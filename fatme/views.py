from django.shortcuts import render
from django.template import RequestContext
from fatme.forms import WeightForm
from fatme.models import Weight
from datetime import date, timedelta

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
    today = Weight.view("fatme/all_weights", descending=True).first()
    begin = Weight.view("fatme/all_weights").first()

    start = 124.3
    goal = 89.9
    height = 182
    age = 29

    left = today['weight'] - goal
    done = start - today['weight']

    days = (today['date']-begin['date']).days

    days_left = round(left/(done/days), 1)
    est_day = date.today()+timedelta(days=int(days_left))
    final_day = date(2013, 11, 3)

    consumption = (66.5+(13.75*today['weight'])+(5.003*height)-(6.775*age))

    return render(request,
                  "home.html",
                  {
		   "weights": weights,
                   "goal": goal,
                   "today": today,
                   "left": left,
                   "done": done,
                   "consumption": consumption,
                   "begin": begin,
                   "days": days,
                   "days_left": days_left,
                   "est_day": est_day,
                   "final_day": final_day,
                  },
                  context_instance=RequestContext(request))

