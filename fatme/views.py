import csv
import json
import logging
from StringIO import StringIO
from datetime import date, timedelta

from django.core.urlresolvers import reverse
from django.conf import settings
from restkit.errors import RequestFailed
from django.template import RequestContext
from django.shortcuts import render, redirect
from couchdbkit.exceptions import ResourceConflict
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest

from withings import (WithingsCredentials, WithingsApi, WithingsAuth as WiAu,
                      OAuth1Session)

from fatme.forms import WeightForm
from fatme.models import Weight, Start
from fatme.snip import logged_in_or_basicauth

logger = logging.getLogger()


class WithingsAuth(WiAu):
    def get_authorize_url(self):
        oauth = OAuth1Session(self.consumer_key,
                              client_secret=self.consumer_secret,
                              callback_uri=self.callback_url)

        tokens = oauth.fetch_request_token('%s/request_token' % self.URL)
        self.oauth_token = tokens['oauth_token']
        self.oauth_secret = tokens['oauth_token_secret']

        return oauth.authorization_url('%s/authorize' % self.URL)


def get_withings_latest():
    start_obj = Start.view("fatme/start", limit=1).first()
    start_obj = Start.get(start_obj._id)

    access_token = start_obj.access_key
    access_token_secret = start_obj.access_secret
    user_id = start_obj.user_id

    c = WithingsCredentials(access_token=access_token,
                            access_token_secret=access_token_secret,
                            consumer_key=settings.WITHINGS_API_KEY,
                            consumer_secret=settings.WITHINGS_API_SECRET,
                            user_id=user_id)

    client = WithingsApi(c)

    return client.get_measures(limit=1, meastype=1)[0]


@logged_in_or_basicauth('fatme')
def withings_auth_start(request):
    auth = WithingsAuth(settings.WITHINGS_API_KEY,
                        settings.WITHINGS_API_SECRET)
    auth.callback_url = request.build_absolute_uri(reverse('withings_callback'))

    res = redirect(auth.get_authorize_url())

    request.session['oas'] = auth.oauth_secret

    return res


def withings_callback(request):
    start_obj = Start.view("fatme/start", limit=1).first()
    start_obj = Start.get(start_obj._id)

    try:
        oauth_verifier = request.GET['oauth_verifier']
        oauth_token = request.GET['oauth_token']
        user_id = request.GET['userid']
    except KeyError:
        return HttpResponseBadRequest()

    auth = WithingsAuth(settings.WITHINGS_API_KEY,
                        settings.WITHINGS_API_SECRET)
    auth.oauth_token = oauth_token
    auth.oauth_secret = request.session['oas']

    print 'OAUTH_SECRET', auth.oauth_secret

    creds = auth.get_credentials(oauth_verifier)

    start_obj.access_key = creds.access_token
    start_obj.access_secret = creds.access_token_secret
    start_obj.user_id = user_id
    start_obj.save()

    return redirect(reverse('withings'))


@logged_in_or_basicauth('fatme')
def withings(request):
    if not getattr(settings, 'WITHINGS_ENABLED', False):
        return HttpResponse('disabled')

    last_measure = get_withings_latest()

    resp = {'weight': last_measure.weight,
            'date': last_measure.date.isoformat()}

    return HttpResponse(json.dumps(resp),
                        content_type='application/json')


@logged_in_or_basicauth('fatme')
def withings_save(request):
    if not getattr(settings, 'WITHINGS_ENABLED', False):
        return HttpResponse('disabled')

    last_measure = get_withings_latest()

    new = True

    try:
        instance = Weight.get(last_measure.date.date().isoformat())
        new = False
    except:
        instance = Weight(date=last_measure.date.date().isoformat())

    instance.weight = float(last_measure.weight)
    instance.save()

    resp = {'date': last_measure.date.isoformat(),
            'weight': last_measure.weight,
            'new': new}

    return HttpResponse(json.dumps(resp),
                        content_type='application/json')


@logged_in_or_basicauth('fatme')
@csrf_exempt
def new_weight(request):
    ''' Add a weight measurement with POST '''
    try:
        instance = Weight.get(request.POST['date'])
    except:
        instance = None

    weight = None
    if request.POST:
        form = WeightForm(request.POST, instance=instance)

        if form.is_valid():
            logger.info('{0} stored a weight'.format(request.user))
            try:
                weight = form.save()
            except ResourceConflict:
                logger.error('Storing failed silently: date already exists')
            return redirect('home')
    else:
        form = WeightForm(instance=instance)

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
        start_obj = Start.view("fatme/start", limit=1).one()
    except RequestFailed:
        return HttpResponse(json.dumps({'error': 'The service is temporarily unavailable', 'status': 503}), status=503)

    logger.info(start_obj)

    competition_start = date(2013, 1, 27)
    total_goal = 27.6

    result = {}
    result['start'] = total_goal + start_obj['goal']
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
    resp['Access-Control-Allow-Headers'] = 'X-Requested-With'
    return resp


def csvhistory(request):
    try:
        weights = Weight.view("fatme/all_weights")
        start_obj = Start.view("fatme/start", limit=1).first()
    except RequestFailed:
        return HttpResponse(json.dumps({'error': 'The service is temporarily unavailable', 'status': 503}), status=503)

    start = start_obj['weight']
    start_date = start_obj['date']
    goal = start_obj['goal']

    logger.info(dict(start_obj))

    if start is None and start_obj['name'] == 'Markus':
        start = 107.0
        start_date = date(2013, 1, 27)

    total_goal = start - goal
    total_days = (start_obj['final_day'] - start_date).days
    k = (total_goal / total_days)

    output = StringIO()

    weightwriter = csv.writer(output, delimiter=',')
    weightwriter.writerow(['Date', 'Plan', 'Weight'])

    for weight in weights:
        days = (weight['date'] - start_date).days
        if days >= total_goal:
            goal_today = goal
        else:
            goal_today = round(start - (k * days), 4)

        weightwriter.writerow([weight['date'], goal_today, weight['weight']])

    resp = HttpResponse(output.getvalue(), content_type='text/csv')
    resp['Access-Control-Allow-Origin'] = '*'
    resp['Access-Control-Allow-Headers'] = 'X-Requested-With'
    return resp


def harris_benedict(weight, height, age):
    return (66.5 + (13.75 * weight) + (5.003 * height) - (6.775 * age))


def cm_to_m(cm):
    return cm / 100


def bmi(weight, height):
    return round(weight / (cm_to_m(height) ** 2), 2)


def trefethen(weight, height):
    return round((1.3 * weight) / (cm_to_m(height) ** 2.5), 2)


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

    days = (today['date'] - begin['date']).days
    total_days = (final_day - begin['date']).days

    if done < 1:
        days_left = total_days
    else:
        days_left = round(left / (done / days), 1)
    est_day = date.today() + timedelta(days=int(days_left))

    total_goal = start - goal

    if total_days > days:
        goal_today = round(start - ((total_goal / total_days) * days), 1)
        goal_loss_today = start - goal_today
    else:
        goal_today = goal
        goal_loss_today = start - goal

    diff = today['weight'] - goal_today

    if diff > 0:
        actual = '{0} kg behind'.format(abs(diff))
    elif diff < 0:
        actual = '{0} kg ahead'.format(abs(diff))
    else:
        actual = 'exactly on target'

    goal_days_left = total_days - days

    consumption = harris_benedict(today['weight'], height, age)

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

    height = start_obj['height']

    today['bmi'] = bmi(today['weight'], height)
    today['trefethen'] = trefethen(today['weight'], height)

    begin['bmi'] = bmi(begin['weight'], height)
    begin['trefethen'] = trefethen(begin['weight'], height)

    sorted_weights = []
    m = begin['date'].month
    mw = []

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
            weight['avg'] = round(sum(prev[-7:]) / 7, 2)
            weight['week_chg'] = round(weight['weight'] - prev[-7], 2)
            if prev_avg:
                weight['chg_avg'] = round(weight['avg'] - prev_avg, 2)
            prev_avg = weight['avg']

        if weight['date'].month == m:
            mw.insert(0, weight)
        else:
            m = weight['date'].month
            sorted_weights.extend(mw)
            mw = [weight]

    sorted_weights.extend(mw)

    return render(request,
                  "home.html",
                  {"weights": reversed(sorted_weights),
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
