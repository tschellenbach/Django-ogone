import logging

from django.core.mail import mail_admins
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

