from django.dispatch import Signal

ogone_payment_accepted = Signal(providing_args=['order_id', 
                                                'amount', 'currency'])
