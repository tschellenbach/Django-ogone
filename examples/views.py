
from django_ogone.ogone import Ogone
from django_ogone.forms import ogone_forms        
from django_ogone import ogone_settings        
'''
The implementation of these examples differs strongly per site
Understand the example and consult the ogone docs to roll your own
'''


def checkout(request):
    data = {}
    #transaction data
    data['orderID'] = '1'
    data['amount'] = '500'
    data['currency'] = 'EUR'
    data['language'] = 'en'
    data['SHASign'] = Ogone.sign(data)
    
    context = {}
    context['form'] = ogone_forms.OgoneForm(data)
    
    if ogone_settings.PRODUCTION:
        request.context['action'] = 'https://secure.ogone.com/ncol/test/orderstandard.asp'
    else:
        request.context['action'] = 'https://secure.ogone.com/ncol/prod/orderstandard.asp'
    





def order_status_update(request):
    '''
    Updates the order status with ogone data.
    There are two ways of reaching this flow
    
    - payment redirect (user gets redirected through this flow)
    - ogone server side call (in case of problems ogone will post to our server
    with an updated version ofo the payment status)
    
    For testing order flow updates
    http://localhost:8080/order_status_update/?orderID=12&currency=EUR&amount=680.44&PM=CreditCard&ACCEPTANCE=test123&STATUS=5&CARDNO=XXXXXXXXXXXX1111&ED=0114&CN=thierry&TRXDATE=09/21/10&PAYID=8254874&NCERROR=0&BRAND=VISA&IPCTY=NL&CCCTY=US&ECI=12&CVCCheck=NO&AAVCheck=NO&VC=NO&IP=85.145.6.230&SHASIGN=B02C883D4D31D9665305EA05CC81D3DED7726C68F18C870A8C8F3119DC1B460D9103944692B6E44D47EEA402630770A8122F6D1B7028CC5FD58847DC43D7C082
    '''
    params = request.POST or request.GET
    ogone = Ogone(params)
    
    if ogone.is_valid():
        #update the order data, different for each site
        #need the ogone data and custom logic, use signals for this
        ogone_signals.ogone_update_order.send(sender=Ogone, ogone=ogone)
        
        #redirect to the appropriate view
        order_id = ogone.get_order_id()
        url = '%s?transaction_id=%s' % (reverse('checkout'), order_id)
        
        return HttpResponseRedirect(url)


ogone_signals.ogone_update_order.connect(models.Transaction.objects.update_order)
