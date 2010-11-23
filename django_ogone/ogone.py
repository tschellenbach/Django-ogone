import logging
import datetime
import urllib
import urllib2
import xml.dom.minidom

log = logging.getLogger('django_ogone')

from django_ogone import status_codes

from django_ogone import exceptions as ogone_exceptions
from django_ogone import settings as ogone_settings
from django_ogone import security as ogone_security
from django_ogone import forms as ogone_forms


class Ogone(object):
    """
    Generic functionality for signing and verifying ogone
    requests

    Used for signing the out flow

    And handling the update functionality
    """

    def __init__(self, params=None, request=None, settings=ogone_settings):
        # This allows us to override settings for the whole class
        self.settings = settings

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

    @staticmethod
    def get_action(production=None, settings=ogone_settings):
        """ Get the relevant action parameter from the settings. """

        PROD_URL = settings.PROD_URL
        TEST_URL = settings.TEST_URL

        assert isinstance(PROD_URL, unicode) or isinstance(PROD_URL, str)
        assert isinstance(TEST_URL, unicode) or isinstance(TEST_URL, str)

        if production is None:
            production = settings.PRODUCTION

        if production:
            log.debug('Returning production URL: %s', PROD_URL)
            return PROD_URL
        else:
            log.debug('Returning test URL: %s', TEST_URL)
            return TEST_URL

    @classmethod
    def get_data(cls, data, settings=ogone_settings):
        # Check for obligatory fields
        assert 'language' in data
        assert 'orderID' in data
        assert 'amount' in data
        # Make sure amount is an int
        assert isinstance(data['amount'], (int, long)) or data['amount'].isdigit()

        data['currency'] = data.get('currency') or settings.CURRENCY
        data['PSPID'] = settings.PSPID
        data['SHASign'] = cls.sign(data, settings=settings)

        return data

    @classmethod
    def get_form(cls, data, settings=ogone_settings):
        enriched_data = cls.get_data(data, settings)

        log.debug('Sending the following data to Ogone: %s', enriched_data)
        form = ogone_forms.OgoneForm(enriched_data)

        return form

    def is_valid(self):
        """ Verify the signature for the current parameters. Used in Ogone
            OUT flow. Returns either True or False
        """

        ogone_signature = self.get_ogone_signature()
        signature = self.compute_signature(out=True)

        return signature == ogone_signature

    @staticmethod
    def _normalize_params(params):
        """ Make sure all the dictionary keys are upper case. """

        return dict([(k.upper(), v) for k, v in params.items()])

    @staticmethod
    def _parse_orderid(params):
        params.update({'ORDERID': int(params.get('ORDERID'))})

        return params

    @staticmethod
    def _parse_status(params):
        params.update({'STATUS': int(params.get('STATUS'))})

        return params

    @staticmethod
    def _parse_trxdate(params):
        v = params.get('TRXDATE')

        if v:
            month, day, year = map(int, v.split('/'))
            # Ogone responds with a year coded on 2 digits. Add, the 2000
            # years delta.
            year += 2000
            # --//--
            v = datetime.date(year, month, day)

            params.update({'TRXDATE': v})

        return params

    @staticmethod
    def _parse_ed(params):
        v = params.get('ED')

        if v:
            month, year = int(v[:2]), int(v[-2:])
            # Ogone responds with a year coded on 2 digits. Add, the 2000
            # years delta.
            year += 2000
            # --//--
            v = datetime.date(year, month, 1)

            params.update({'ED': v})

        return params

    def compute_signature(self, *args, **kwargs):
        """ Compute a signature for the current parameters. """

        # Make sure we pass on settings
        if not 'settings' in kwargs:
            kwargs.update({'settings': self.settings})

        return self.sign(self.params, *args, **kwargs)

    def parse_params(self):
        """ Validate and convert the eligible elements to
            native Python types. """

        assert self.params

        # We're not gonna work on an invalid form
        if not self.is_valid():
            raise ogone_exceptions.InvalidSignatureException()

        # This first one creates a copy of our params dict
        self.parsed_params = self._normalize_params(self.params)

        # These update the dict in-place
        self._parse_trxdate(self.parsed_params)
        self._parse_ed(self.parsed_params)
        self._parse_status(self.parsed_params)
        self._parse_orderid(self.parsed_params)

        # Mark ourselves as parsed
        self.parsed = True

        return self.parsed_params

    def get_order_id(self):
        self.parsed or self.parse_params()

        return self.parsed_params['ORDERID']

    def get_status(self):
        self.parsed or self.parse_params()

        return self.parsed_params['STATUS']

    def get_transaction_date(self):
        self.parsed or self.parse_params()

        return self.parsed_params['TRXDATE']

    def get_expiry_date(self):
        self.parsed or self.parse_params()

        return self.parsed_params['ED']

    @staticmethod
    def sign(data, hash_method=None, secret=None, out=False,
             settings=ogone_settings):
        """ Sign the given data. """

        if not hash_method:
            hash_method = settings.HASH_METHOD

        if not secret:
            if out:
                secret = settings.SHA_POST_SECRET
            else:
                secret = settings.SHA_PRE_SECRET

        return ogone_security.OgoneSignature(data,
                    hash_method=hash_method,
                    secret=secret).signature()



    def get_ogone_signature(self):
        assert 'SHASIGN' in self.params, \
            'No signature found. Are you sure this is coming from Ogone?'

        return self.params.get('SHASIGN')

    def get_status_description(self):
        return status_codes.get_status_description(self.get_status())

    def get_status_category(self):
        return status_codes.get_status_category(self.get_status())


class OgoneDirectLink(Ogone):
    @staticmethod
    def get_action(production=None, settings=ogone_settings):
        """ Get the relevant action parameter from the settings. """

        PROD_URL = settings.DIRECT_LINK_PROD_URL
        TEST_URL = settings.DIRECT_LINK_TEST_URL

        assert isinstance(PROD_URL, unicode) or isinstance(PROD_URL, str)
        assert isinstance(TEST_URL, unicode) or isinstance(TEST_URL, str)

        if production is None:
            production = settings.PRODUCTION

        if production:
            log.debug('Returning production URL: %s', PROD_URL)
            return PROD_URL
        else:
            log.debug('Returning test URL: %s', TEST_URL)
            return TEST_URL

    @staticmethod
    def get_data(data, settings=ogone_settings):
        # Check required fields
        assert 'orderID' in data or 'PAYID' in data
        assert 'amount' in data
        # Make sure amount is an int
        assert isinstance(data['amount'], (int, long)) or data['amount'].isdigit()

        data['PSPID'] = settings.PSPID
        data['USERID'] = settings.USERID
        data['PSWD'] = settings.PSWD
        data['SHASign'] = Ogone.sign(data, settings=settings)

        return data

    @classmethod
    def request(cls, url, data, settings=ogone_settings):
        params = cls.get_data(data, settings)

        request = urllib2.Request(url)
        request.add_header("Content-type", "application/x-www-form-urlencoded")
        params = urllib.urlencode(params)
        response = urllib2.urlopen(request, params)

        xml_str = response.read()
        log.info('DirectLink response: %s', xml_str)

        doc = xml.dom.minidom.parseString(xml_str)
        attrs = doc.documentElement.attributes
        return dict([(attrs.item(i).name, attrs.item(i).value) \
                    for i in range(attrs.length)])

    # DirectLink doesn't return a signature, so, fake the signature coercion.
    def is_valid(self):
        return True
