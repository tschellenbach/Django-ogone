Django Ogone
========

#### Django Ogone ####

By: Thierry Schellenbach (http://www.mellowmorning.com)

This project aims to provide an easy to use client interface in python to the Ogone payment interface.

It is Django specific in nature, but hopefully the clean seperation will allow for easy porting to other frameworks.

### Installation instructions ###

## Step 1 - settings ##

Look at the ogone settings file and define the required settings in your django settings file
- OGONE_PSPID
- OGONE_SHA_PRE_SECRET
- OGONE_SHA_POST_SECRET
The secrets are just for hashing purposes. Fill in the same random value here as in the ogone admin.
While you are in the ogone admin set the sha method to sha512.
Furthermore enable the send parameters option for the payment feedback.

## Step 2 - adding the form ##

The form needs to be integrated in your checkout page.
Ogone's manual explains this quite well.
Note though that you need to be able to sign the data in the form.
Therefore your form must be generated dynamically.
This project provides an easy dynamic form to help you with that.
Here an example implementation:

from django_ogone import forms as ogone_forms
from django_ogone.ogone import Ogone
from django_ogone import settings as ogone_settings  

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
        

This form enables you to send a secured payment request to ogone.
The Ogone.sign call is responsible for the hashing.
To support more form field requests to ogone simply add them to the data dict. 


## Step 3 - handling payments ##

After the user pays you he is redirected back to your page.
If you enabled the send parameters option in the ogone admin the payment status will be sent to your system.
Usually you would want to use this data to mark the transaction as payed.

Here an example implementation. Use this to roll your own.


from django_ogone.ogone import Ogone
def order_status_update(request):
    '''
    Updates the order status with ogone data.
    There are two ways of reaching this flow
    
    - payment redirect (user gets redirected through this flow)
    - ogone server side call (in case of problems ogone will post to our server
    with an updated version ofo the payment status)
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


You will probably want to adjust the redirection behaviour in this view.
Furthermore you should write a function to connect to the ogone_update_order signal.
This signal allows you to automatically update the payment information


### Resources ###

This one made my life easier.
[![Older implementation]](http://github.com/jsmits/django-payment-ogone)
