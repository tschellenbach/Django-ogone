__version__ = '1.0.1'
__maintainer__ = 'Thierry Schellenbach'
__email__ = 'thierryschellenbach at googles great mail service'

# Be careful here, otherwise setup.py won't work
try:
    from django_ogone.ogone import Ogone
    __ALL__ = (Ogone, )
except ImportError:
    pass
