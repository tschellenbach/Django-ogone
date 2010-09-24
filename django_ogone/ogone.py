import logging

from django.core.mail import mail_admins

from django_ogone import status_codes

from django_ogone import exceptions as ogone_exceptions
from django_ogone import settings as ogone_settings
from django_ogone import security as ogone_security

class Ogone(object):
    '''
    Generic functionality for signing and verifying ogone
    requests

    Used for signing the out flow

    And handling the update functionality
    '''

    def __init__(self, params=None, request=None):
        self.request = request
        self.params = self._normalize_params(params) or {}

    def _normalize_params(self, params):
        return dict([(k.upper(), v) for k, v in params.items()])

    def compute_signature(self, *args, **kwargs):
        return Ogone.sign(self.params, *args, **kwargs)

    def parse_params(self):
        '''return the ogone params with some pre parsing'''
        parsed_params = self.params.copy()
        import datetime
        for k, v in parsed_params.items():
            if k == 'TRXDATE' and v:
                month, day, year = map(int, v.split('/'))
                v = datetime.date(day, month, year)
                parsed_params[k] = v
        return parsed_params

    @classmethod
    def sign(self, data, hash_method = ogone_settings.HASH_METHOD,
             secret=ogone_settings.SHA_PRE_SECRET, out=False):
        if secret == ogone_settings.SHA_PRE_SECRET and out:
            secret = ogone_settings.SHA_POST_SECRET
        return ogone_security.OgoneSignature(data,
                    hash_method=ogone_settings.HASH_METHOD,
                    secret=ogone_settings.SHA_PRE_SECRET).signature()

    @classmethod
    def get_action(self, production=ogone_settings.PRODUCTION):
        """ Get the relevant action parameter from the settings. """

        if production:
            return ogone_settings.PROD.URL
        else:
            return ogone_settings.TEST_URL

    def is_valid(self):
        '''
        Is valid functionality for the ogone OUT flow
        compares provided signature to our own computation
        '''
        if not self.params:
            raise ogone_exceptions.InvalidParamsException("no parameters in the request")
        ogone_signature = self.get_ogone_signature()
        signature = self.compute_signature(out=True)

        if signature != ogone_signature:
            raise ogone_exceptions.InvalidSignatureException("ogone_signature (%s) != \nsignature (%s)" % (ogone_signature, signature))

        return signature

    def get_ogone_signature(self):
        return self.params.get('SHASIGN')

    def get_order_id(self):
        return int(self.params.get('ORDERID'))

    # REWORK THIS CODE
    # def get_status_category(self):
    #     '''
    #     Maps the status param to a category
    #     '''
    #     from django.conf import settings
    # 
    #     logging.debug('Processing status message from Ogone. Params: %s', self.params)
    #     status = int(self.params.get('STATUS', None))
    # 
    #     if status in status_codes.SUCCESS:            
    #         signals.ogone_payment_accepted.send(order_id=order_id,
    #                 amount=Decimal(self.params.get('AMOUNT'))/100, 
    #                 currency=Decimal(self.params.get('CURRENCY')))
    # 
    #         return status_codes.SUCCESS
    #     
    #     if status in status_codes.CANCELLED:
    #         return status_codes.CANCELLED
    #         
    #     if status in status_codes.NOT_PROCESSED:
    #         return status_codes.NOT_PROCESSED
    #         
    #     raise UnknownStatusException(status)
    # 
