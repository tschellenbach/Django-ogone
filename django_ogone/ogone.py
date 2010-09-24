import logging

from django.core.mail import mail_admins

from django_ogone import status_codes

from django_ogone import exceptions as ogone_exceptions
from django_ogone import settings as ogone_settings
from django_ogone import security as ogone_security

class Ogone(object):
    """
    Generic functionality for signing and verifying ogone
    requests

    Used for signing the out flow

    And handling the update functionality

    >>> from django_ogone import Ogone
    >>> params = {u'ORDERID': u'13', u'STATUS': u'9', u'CARDNO': u'XXXXXXXXXXXX1111', u'VC': u'NO', u'PAYID': u'8285812', u'CN': u'Kaast Achternaam', u'NCERROR': u'0', u'IP': u'82.139.114.10', u'IPCTY': u'NL', u'CURRENCY': u'EUR', u'CCCTY': u'US', u'SHASIGN': u'D90EFA06285DA1344F4CC7E5EF1887C2B2F28AAF35A5E2BE8666C0C6FCC41710B77D1662FC86A030AC8B032A2C819AC6B8E3DD36D80E2ED1A0947B4B83DD1C99', u'AAVCHECK': u'NO', u'BRAND': u'VISA', u'ACCEPTANCE': u'test123', u'ECI': u'7', u'TRXDATE': u'09/24/10', u'AMOUNT': u'6794.81', u'CVCCHECK': u'NO', u'ED': u'0111', u'PM': u'CreditCard'}
    >>> o = Ogone(params)
    >>> o.is_valid()
    'D90EFA06285DA1344F4CC7E5EF1887C2B2F28AAF35A5E2BE8666C0C6FCC41710B77D1662FC86A030AC8B032A2C819AC6B8E3DD36D80E2ED1A0947B4B83DD1C99'
    >>> o.get_status_category()
    'success'
    >>> o.get_status_description(9)
    'Payment requested'

    """

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

    @classmethod
    def get_status_description(cls, status):
        assert isinstance(status, int)
        
        return status_codes.STATUS_DESCRIPTIONS[status]
        
    def get_status_category(self):
        """ The Ogone API allows for four kind of results:
            - success
            - decline
            - exception
            - cancel 
            
            In this function we do mapping from the status
            number into one of these categories of results.
        """
        
        status = int(self.params.get('STATUS', 0))
        
        logging.debug('Processing status message %d', status)
        
        if status in status_codes.SUCCESS_CODES:
            return status_codes.SUCCESS_STATUS
        
        if status in status_codes.DECLINE_CODES:
            return status_codes.DECLINE_STATUS
        
        if status in status_codes.EXCEPTION_CODES:
            return status_codes.EXCEPTION_STATUS
        
        if status in status_codes.CANCEL_CODES:
            return status_codes.CANCEL_STATUS

        raise UnknownStatusException(status)
