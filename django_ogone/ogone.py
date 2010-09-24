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
    """

    def __init__(self, params=None, request=None):
        assert request or params, \
            'Please specify either a request or a set of parameters'

        if not params:
            params = request.GET or request.POST

        if not params:
            raise ogone_exceptions.InvalidParamsException("No parameters found.")

        # We allways want our data to be normalized
        self.params = self._normalize_params(params)
        
        # We haven't parsed anything yet
        self.parsed = False

    @classmethod
    def _normalize_params(cls, params):
        """ Make sure all the dictionary keys are upper case. """
        
        return dict([(k.upper(), v) for k, v in params.items()])
    
    @classmethod
    def _parse_orderid(cls, params):
        params.update({'ORDERID': int(params.get('ORDERID'))})
        
        return params
    
    @classmethod
    def _parse_status(cls, params):
        params.update({'STATUS': int(params.get('STATUS'))})
        
        return params
    
    @classmethod
    def _parse_trxdate(cls, params):
        v = params.get('TRXDATE')

        import datetime
        
        month, day, year = map(int, v.split('/'))
        v = datetime.date(day, month, year)
        
        params.update({'TRXDATE': v})
        
        return params

    def compute_signature(self, *args, **kwargs):
        """ Compute a signature for the current parameters. """
        
        return Ogone.sign(self.params, *args, **kwargs)

    def parse_params(self):
        """ Validate and convert the eligible elements to 
            native Python types. """
        
        assert self.params
        
        # We're not gonna work on an invalid form
        if not self.is_valid():
            raise ogone_exceptions.InvalidSignatureException("ogone_signature (%s) != \nsignature (%s)" % (ogone_signature, signature))

        # This first one creates a copy of our params dict
        self.parsed_params = self._normalize_params(self.params)
        
        # These update the dict in-place
        self._parse_trxdate(self.parsed_params)
        self._parse_status(self.parsed_params)
        self._parse_orderid(self.parsed_params)
        
        # Mark ourselves as parsed
        self.parsed = True
        
        return self.parsed_params
    
    def get_orderid(self):
        self.parsed or self.parse_params()
        
        return self.parsed_params['ORDERID']
    
    def get_status(self):
        self.parsed or self.parse_params()
        
        return self.parsed_params['STATUS']
    
    def get_signature(self):
        self.parsed or self.parse_params()

    @classmethod
    def sign(self, data, hash_method=ogone_settings.HASH_METHOD,
             secret=ogone_settings.SHA_PRE_SECRET, out=False):
        """ Sign the given data. """
        
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
        """ Verify the signature for the current parameters. Used in Ogone
            OUT flow. Returns either True or False
        """

        ogone_signature = self.get_ogone_signature()
        signature = self.compute_signature(out=True)

        return signature == ogone_signature

    def get_ogone_signature(self):
        assert 'SHASIGN' in self.params, \
            'No signature found. Are you sure this is coming from Ogone?'
        
        return self.params.get('SHASIGN')

    def get_status_description(self):
        return status_codes.get_status_description(self.get_status())
    
    def get_status_category(self):
        return status_codes.get_status_category(self.get_status())
        
