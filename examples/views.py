"""
The implementation of these examples differs strongly per site
Understand the example and consult the ogone docs to roll your own
"""

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from django_ogone.ogone import Ogone
from django_ogone.forms import ogone_forms
from django_ogone import ogone_settings


def checkout(request):
    data = {}
    #transaction data
    data['orderID'] = '1'
    data['amount'] = '500'
    data['currency'] = 'EUR'
    data['language'] = 'en'
    data['SHASign'] = Ogone.sign(data)

    context = {}
    context['form'] = Ogone.get_form(data)
    context['action'] = Ogone.get_action()

    return render_to_response('shop/checkout/form.html', context)


def order_status_update(request):
    '''
    Updates the order status with ogone data.
    There are two ways of reaching this flow

    - payment redirect (user gets redirected through this flow)
    - ogone server side call (in case of problems ogone will post to our server
    with an updated version ofo the payment status)

    For testing order flow updates
    http://localhost:8080/order_status_update/?orderID=12&currency=EUR&amount=680.44&PM=CreditCard&ACCEPTANCE=test123&STATUS=5&CARDNO=XXXXXXXXXXXX1111&ED=0114&CN=thierry&TRXDATE=09/21/10&PAYID=8254874&NCERROR=0&BRAND=VISA&IPCTY=NL&CCCTY=US&ECI=12&CVCCheck=NO&AAVCheck=NO&VC=NO&IP=85.145.6.230&SHASIGN=B02C883D4D31D9665305EA05CC81D3DED7726C68F18C870A8C8F3119DC1B460D9103944692B6E44D47EEA402630770A8122F6D1B7028CC5FD58847DC43D7C082
    Accented characters with sha1
    http://127.0.0.1:8000/order_status_update/?orderID=44&currency=CHF&amount=10&PM=CreditCard&ACCEPTANCE=test123&STATUS=5&CARDNO=XXXXXXXXXXXX1111&ED=0115&CN=S%E9bastien+Fievet&TRXDATE=11%2F02%2F10&PAYID=8580040&NCERROR=0&BRAND=VISA&IPCTY=CH&CCCTY=US&ECI=7&CVCCheck=NO&AAVCheck=NO&VC=NO&IP=188%2E62%2E236%2E12&SHASIGN=861D83EAC408746F5A7CFA3F5BDD3C7C6C145817
    '''
    # Workaround because Ogone deals with latin1 characters and we want
    # our website to use another ``DEFAULT_CHARSET`` (default: utf8).
    from django.http import QueryDict
    params = QueryDict(request.META['QUERY_STRING'], encoding='latin1')
    # --//--
    ogone = Ogone(params)

    if ogone.is_valid():
        #update the order data, different for each site
        #need the ogone data and custom logic, use signals for this
        ogone_signals.ogone_update_order.send(sender=Ogone, ogone=ogone)

        #redirect to the appropriate view
        order_id = ogone.get_order_id()
        url = reverse('tracking', args=[order_id])

        return HttpResponseRedirect(url)


ogone_signals.ogone_update_order.connect(models.Transaction.objects.update_order)
