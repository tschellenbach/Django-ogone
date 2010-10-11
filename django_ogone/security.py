import hashlib, logging

log = logging.getLogger('django_ogone')

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

    >>> ogone = OgoneSignature(dict(d='a', a='b'), hash_method='sha512', secret='c')
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

    def __init__(self, data, hash_method, secret):
        assert hash_method in ['sha1', 'sha256', 'sha512']
        assert str(secret)

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
        if v == '' or v is None:
            valid = False
        if k == 'SHASIGN':
            valid = False
        return valid

    def _merge_data(self, data):
        pairs = ['%s=%s' % (k, v) for k, v in data]
        pre_sign_string = self.secret.join(pairs) + self.secret
        return pre_sign_string

    def _sign_string(self, pre_sign_string):
        hashmethod = getattr(hashlib, self.hash_method)
        signed = hashmethod(pre_sign_string).hexdigest().upper()
        return signed

    def signature(self):
        log.debug('Making signature for data: %s', self.data)
        
        sorted_data = self._sort_data(self.data)
        log.debug('Sorted data: %s', sorted_data)
        
        pre_sign_string = self._merge_data(sorted_data)
        log.debug('String to sign: (normal) %s', pre_sign_string)
        
        signed = self._sign_string(pre_sign_string)
        log.debug('Signed data: %s', signed)
                
        return signed

    def __unicode__(self):
        return self.signature()


