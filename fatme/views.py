import csv
import json
import logging
from StringIO import StringIO
from datetime import date, timedelta

from django.http import HttpResponse
from restkit.errors import RequestFailed
from django.template import RequestContext
from django.shortcuts import render, redirect
from couchdbkit.exceptions import ResourceConflict

from fatme.forms import WeightForm
from fatme.models import Weight, Start
from snip import logged_in_or_basicauth

logger = logging.getLogger(__name__)

@logged_in_or_basicauth('fatme')
def new_weight(request):
    weight = None
    if request.POST:
        instance = None 
        if 'date' in request.POST:
            try:
                instance = Weight.get(request.POST['date'])
            except:
                pass 
        form = WeightForm(request.POST, instance=instance)
        if form.is_valid():
            logger.info('{0} stored a weight'.format(request.user))
            try:
                weight = form.save()
            except ResourceConflict:
                logger.error('Storing failed silently: date already exists')
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

def last_json(request):
    try:
        today = Weight.view("fatme/all_weights", descending=True, limit=1).first()
        begin = Weight.view("fatme/all_weights", limit=1).first()
        start_obj = Start.view("fatme/start", limit=1).first()
    except RequestFailed:
        return HttpResponse(json.dumps({'error': 'The service is temporarily unavailable', 'status': 503}), status=503)

    competition_start = date(2013, 1, 27)
    total_goal = 27.6

    result = {}
    result['start'] = total_goal+start_obj['goal']
    result['start_date'] = competition_start.isoformat()
    result['goal'] = start_obj['goal']
    result['goal_date'] = start_obj['final_day'].isoformat()
    result['diff'] = round(result['start'] - today['weight'], 2)
    result['goal_diff'] = total_goal
    result['latest'] = today['weight']
    result['latest_date'] = today['date'].isoformat()
    result['latest_days_left'] = (start_obj['final_day'] - today['date']).days
    result['today'] = date.today().isoformat()
    result['total_days'] = (start_obj['final_day'] - competition_start).days
    result['days_left'] = (start_obj['final_day'] - date.today()).days
    result['percent_done'] = round(result['diff'] / result['goal_diff'] * 100, 2)
    result['percent_days'] = round((float(result['days_left']) / float(result['total_days'])) * 100, 2)
    result['latest_age'] = result['latest_days_left'] - result['days_left']
    result['name'] = start_obj['name']
    result['picture'] = start_obj['picture']

    resp = HttpResponse(json.dumps(result, sort_keys=True), content_type='application/json')
    resp['Access-Control-Allow-Origin'] = '*'
    return resp

def csvhistory(request):
    weights = Weight.view("fatme/all_weights")
    start_obj = Start.view("fatme/start", limit=1).first()

    start = start_obj['start']
    start_date = start_obj['date']
    goal = start_obj['goal']

    if start is None:
        print 'wtf'
        if start_obj['name'] == 'Ferrix':
            start = 124.3
            start_date = date(2012, 10, 19)
        elif start_obj['name'] == 'Markus':
            start = 107.0
            start_date = date(2013, 1, 27)

    total_goal = start - goal
    total_days = (start_obj['final_day'] - start_date).days
    k = (total_goal/total_days)

    print 'total days', total_days
    print 'total goal', total_goal
    print 'start date', start_date

    output = StringIO()

    weightwriter = csv.writer(output, delimiter=',')
    weightwriter.writerow(['Date','Weight', 'Plan'])
    for weight in weights:
        days = (weight['date']-start_date).days
        goal_today = round(start-k*days, 4)
        weightwriter.writerow([weight['date'], weight['weight'], goal_today])

    resp = HttpResponse(output.getvalue(), content_type='text/csv')
    resp['Access-Control-Allow-Origin'] = '*'
    return resp

def home(request):

    weights = Weight.view("fatme/all_weights")
    today = Weight.view("fatme/all_weights", descending=True, limit=1).first()
    begin = Weight.view("fatme/all_weights", limit=1).first()
    start_obj = Start.view("fatme/start", limit=1).first()

    start = begin['weight']
    goal = start_obj['goal']
    height = start_obj['height']
    age = start_obj['age']
    final_day = start_obj['final_day']

    left = today['weight'] - goal
    done = start - today['weight']

    days = (today['date']-begin['date']).days
    total_days = (final_day - begin['date']).days

    if done < 1:
        days_left = total_days
    else:
        days_left = round(left/(done/days), 1)
    est_day = date.today()+timedelta(days=int(days_left))

    total_goal = start - goal
    goal_today = round(start-((total_goal/total_days)*days), 1)

    diff = today['weight'] - goal_today
    goal_loss_today = start - goal_today

    if diff > 0:
        actual = '{0} kg behind'.format(abs(diff))
    elif diff < 0:
        actual = '{0} kg ahead'.format(abs(diff))
    else:
        actual = 'exactly on target'

    goal_days_left = total_days - days

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

    height_m = start_obj['height'] / 100

    today['bmi'] = round(today['weight'] / (height_m ** 2), 2)
    today['trefethen'] = round((1.3 * today['weight']) / (height_m ** 2.5), 2)
    begin['bmi'] = round(begin['weight'] / (height_m ** 2), 2)
    begin['trefethen'] = round((1.3 * begin['weight']) / (height_m ** 2.5), 2)

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

        if len(prev) >= 7:
            weight['avg'] = round(sum(prev[-7:])/7, 2)
            weight['week_chg'] = round(weight['weight']-prev[-7], 2)
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
                   "goal_today": goal_today,
                   "actual": actual,
                   "total_days": total_days,
                   "total_goal": total_goal,
                   "goal_days_left": goal_days_left,
                   "goal_loss_today": goal_loss_today,
                  },
                  context_instance=RequestContext(request))

