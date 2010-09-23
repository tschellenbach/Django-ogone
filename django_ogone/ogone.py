import logging

from django.core.mail import mail_admins
from django_ogone import exceptions as ogone_exceptions

from django_ogone import settings as ogone_settings
import hashlib

from django_ogone.alternative_signing import create_hash

class OgoneSignature(object):
    '''

    Signs the ogone parameters
    - all keys are in upper case
    - if no value is present the value is removed
    - parameters are sorted alphabetically
    - they limit the keys to a subsection of fields
      (not implemented in this api)
    - the secret is used between every parameter set and added to the end of
      the string

    >>> ogone = OgoneSignature(dict(d='a', a='b'), secret='c')
    >>> sorted_data = ogone._sort_data(ogone.data)
    >>> sorted_data
    [('A', 'b'), ('D', 'a')]
    >>> pre_sign_string = ogone._merge_data(sorted_data)
    >>> pre_sign_string
    'A=bcD=ac'
    >>> signed = ogone._sign_string(pre_sign_string)
    >>> signed
    'B499539D7E0B2B1FB5CCFE9FFDDBAD1EDF345757C094443ED795662F879FB250EEEB22CBB2D2F3C129E2CAE735044CDB7B08397502204B0683EA370F6D76FB6A'
    >>> ogone.signature()
    'B499539D7E0B2B1FB5CCFE9FFDDBAD1EDF345757C094443ED795662F879FB250EEEB22CBB2D2F3C129E2CAE735044CDB7B08397502204B0683EA370F6D76FB6A'

    This is based on ogones docs
    Example shaOUT from ECOM advanced implementation

    >>> data = dict(acceptance=1234, amount=15, brand='VISA',
    ...             cardno='xxxxxxxxxxxx1111', currency='EUR', NCERROR=0,
    ...             orderId=12, payid=32100123, pm='CreditCard', status=9)
    >>> ogone = OgoneSignature(data, secret='Mysecretsig1875!?',
    ...                        hash_method='sha1')
    >>> sd = ogone._sort_data(ogone.data)
    >>> teststring = ogone._merge_data(sd)
    >>> signature = ogone._sign_string(teststring)
    >>> teststring
    'ACCEPTANCE=1234Mysecretsig1875!?AMOUNT=15Mysecretsig1875!?BRAND=VISAMysecretsig1875!?CARDNO=xxxxxxxxxxxx1111Mysecretsig1875!?CURRENCY=EURMysecretsig1875!?NCERROR=0Mysecretsig1875!?ORDERID=12Mysecretsig1875!?PAYID=32100123Mysecretsig1875!?PM=CreditCardMysecretsig1875!?STATUS=9Mysecretsig1875!?'
    >>> signature
    'B209960D5703DD1047F95A0F97655FFE5AC8BD52'

    This is based on ogones docs
    Example shaIn from ECOM advanced implementation
    >>> data = dict(amount=1500, currency='EUR', operation='RES',
    ...             orderID=1234, PSPID='MyPSPID')
    >>> ogone = OgoneSignature(data, secret='Mysecretsig1875!?',
    ...                        hash_method='sha1')
    >>> sd = ogone._sort_data(ogone.data)
    >>> teststring = ogone._merge_data(sd)
    >>> signature = ogone._sign_string(teststring)
    >>> teststring
    'AMOUNT=1500Mysecretsig1875!?CURRENCY=EURMysecretsig1875!?OPERATION=RESMysecretsig1875!?ORDERID=1234Mysecretsig1875!?PSPID=MyPSPIDMysecretsig1875!?'
    >>> signature
    'EB52902BCC4B50DC1250E5A7C1068ECF97751256'

    '''

    def __init__(self, data, hash_method = ogone_settings.HASH_METHOD,
                 secret=ogone_settings.SHA_PRE_SECRET):
        self.data = data.copy()
        self.hash_method = hash_method
        self.secret = secret

    def _sort_data(self, data):
        # This code uppercases two times and is not well readable
        sorted_data = [(k.upper(), v) for k, v in data.items() \
                       if self._filter_data(k.upper(), v)]
        sorted_data.sort(key=lambda x: x, reverse=False)
        return sorted_data

    def _filter_data(self, k, v):
        valid = True
        if v == '':
            valid = False
        if k == 'SHASIGN':
            valid = False
        return valid

    def _merge_data(self, data):
        pairs = ['%s=%s' % (k, v) for k,v in data]
        pre_sign_string = self.secret.join(pairs) + self.secret
        return pre_sign_string

    def _sign_string(self, pre_sign_string):
        hashmethod = getattr(hashlib, self.hash_method)
        signed = hashmethod(pre_sign_string).hexdigest().upper()
        return signed

    def signature(self):
        logging.debug('Making signature for data: %s', self.data)
        
        sorted_data = self._sort_data(self.data)
        logging.debug('Sorted data: %s', sorted_data)
        
        pre_sign_string = self._merge_data(sorted_data)
        logging.debug('String to sign: %s', pre_sign_string)
        
        signed = self._sign_string(pre_sign_string)
        logging.debug('Signed data: %s', signed)
        
        assert create_hash(self.data, self.secret, getattr(hashlib, self.hash_method)) == signed
        
        return signed

    def __unicode__(self):
        return self.signature()


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
        return OgoneSignature(data, hash_method, secret).signature()

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

    def get_status_category(self):
        '''
        Maps the status param to a category
        '''
        from django.conf import settings

        status = int(self.params.get('STATUS', None))
        status_category = 'not_processed'

        if status == 9:
            status_category = 'accepted'
            # send ogone_payment_accepted signal with amount converted to Decimal and cents
            #signals.ogone_payment_accepted.send(sender=OrderStatus, order_id=order_id,
            #    amount=Decimal(amount) * 100, currency=currency)
        elif status == 1:
            status_category = 'cancelled'
        elif status in [0,2,4,41,5,51,52,59,6,61,62,63,7,71,72,73,74,75,
            8,81,82,83,84,85,91,92,93,94,95,97,98,99]:
            status_category = 'not_processed'
        else:
            # It is better to raise an exception here which will be emailed
            # or caught otherwise by a well-configured Django instance.

            # Ie. No need to do this ourselves.

            # mail_admins
            request = self.request
            if request:
                subject = 'Error (%s IP): %s' % \
                    ((request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS and 'internal' or 'EXTERNAL'), request.path)
            else:
                subject = 'Unknown status code'
            try:
                request_repr = repr(request)
            except:
                request_repr = "Request repr() unavailable"
            message = "Unknown ogone status code: %s\n\n%s" % (status, request_repr)
            mail_admins(subject, message, fail_silently=True)
        return status_category

