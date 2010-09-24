import logging

log = logging.getLogger('djanongo_ogone')

from hashlib import sha1, sha512

def create_hash(params, secret, hashfunc=sha512):
    """ Ogone's hashing algorithm - using the safer SHA512 digest by default.
    
    This is the hash from the documentation example:
    
    >>> pars = {'amount': 1500,
    ...         'currency': 'EUR',
    ...         'Operation': 'RES',
    ...         'orderID': '1234',
    ...         'PSPID': 'MyPSPID'}
    >>> secret = 'Mysecretsig1875!?'
    >>> create_hash(pars, secret, hashfunc=sha1)
    'EB52902BCC4B50DC1250E5A7C1068ECF97751256'
    
    """
    
    log.debug('Creating hash using algorith %s', hashfunc)
    
    # First, sort out the keys
    keys = params.keys()
    keys.sort(key=lambda x: x.upper())
    
    log.debug('Sorted keys: %s', keys)
    
    signstring = ''
    for key in keys:
        if params[key] and not key.upper() in ['SHASIGN', ]:
            # If not empty, add KEY=valuesecret to signelements
            signstring += '%s=%s%s' % (key.upper(), params[key], secret)
    
    log.debug('String to sign: (alternative) %s', signstring)
    
    # Join the string
    signstring = ''.join(signstring)
    
    # Hash the string
    signhash = hashfunc(signstring).hexdigest()
    
    # Uppercase the hash
    signhashupper = signhash.upper()
    
    log.debug('Signed data: (alternative) %s', signhashupper)
    
    return signhashupper

if __name__ == "__main__":
    import doctest
    doctest.testmod()
 
