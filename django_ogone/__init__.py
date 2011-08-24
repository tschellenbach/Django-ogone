__version__ = '1.1.0'
__maintainer__ = 'Thierry Schellenbach'
__email__ = 'thierryschellenbach at googles great mail service'

# Be careful here, otherwise setup.py won't work
try:
    from django_ogone.ogone import Ogone, OgoneDirectLink
    __ALL__ = (Ogone, OgoneDirectLink)
except ImportError:
    pass
