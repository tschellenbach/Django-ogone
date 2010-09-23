from django.conf import settings


'''
The following settings should be defined in your global settings

SHA_PRE and SHA_POST_SECRET have to be set in the ogone admin
Can be any random value. Its just something secret both us and ogone need to know.

Note that the default hash method is set to sha512
Change this in your ogone admin interface

'''


#These four you probably want to change
PSPID = getattr(settings, 'OGONE_PSPID')
SHA_PRE_SECRET = getattr(settings, 'OGONE_SHA_PRE_SECRET')
SHA_POST_SECRET = getattr(settings, 'OGONE_SHA_POST_SECRET')
CURRENCY = getattr(settings, 'OGONE_CURRENCY', 'EUR')

#only touch these if you know whats happening :P
HASH_METHOD = getattr(settings, 'OGONE_HASH_METHOD', 'sha512')
#for other hashmethods see http://docs.python.org/library/hashlib.html
#ogone default is sha1
PRODUCTION = not getattr(settings, 'DEBUG', True)

# Standard URLs. We might want to override these in the future for some
# reason.
TEST_URL = getattr(settings, "OGONE_TEST_URL", 
    "https://secure.ogone.com/ncol/test/orderstandard.asp")
PROD_URL = getattr(settings, "OGONE_PROD_URL", 
    "https://secure.ogone.com/ncol/prod/orderstandard.asp")
