from django.shortcuts import render, redirect
from django.template import RequestContext
from fatme.forms import WeightForm
from fatme.models import Weight
from datetime import date, timedelta

from snip import logged_in_or_basicauth

@logged_in_or_basicauth('fatme')
def new_weight(request):
    weight = None
    if request.POST:
        form = WeightForm(request.POST)
        if form.is_valid():
            weight = form.save()
            return redirect('home')
    else:
        form = WeightForm()

    return render(request,
                  "form.html",
                  {
		   "form": form,
		   "weight": weight,
                  },
                  context_instance=RequestContext(request))

def home(request):

    weights = Weight.view("fatme/all_weights")
    today = Weight.view("fatme/all_weights", descending=True, limit=1).first()
    begin = Weight.view("fatme/all_weights", limit=1).first()

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

    min = {
           'change': 0,
           'chg_day': None,
           'weight': 0,
           'day': None,
          }
    max = {
           'change': 0,
           'chg_day': None,
           'weight': 0,
           'day': None,
          }

    prev = []
    prev_avg = 0

    for i, weight in enumerate(weights):
        if i > 0:
            change = weight['weight'] - prev[-1]
            weight['change'] = change
        
            if change < min['change']:
                min['change'] = change
                min['chg_day'] = weight['date']
            if change > max['change']:
                max['change'] = change
                max['chg_day'] = weight['date']
        else:
            weight['change'] = ''

        if not max['weight'] or weight['weight'] > max['weight']:
            max['weight'] = weight['weight']
            max['day'] = weight['date']
        if not min['weight'] or weight['weight'] < min['weight']:
            min['weight'] = weight['weight']
            min['day'] = weight['date']

        prev.append(weight['weight'])

        if len(prev) >= 10:
            weight['avg'] = sum(prev[-10:])/10
            if prev_avg:
                weight['chg_avg'] = round(weight['avg'] - prev_avg, 2)
            prev_avg = weight['avg']

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
                   "min": min,
                   "max": max,
                  },
                  context_instance=RequestContext(request))

