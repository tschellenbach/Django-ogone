
class OgoneException(Exception):
    pass

class InvalidSignatureException(OgoneException):
    pass

class InvalidParamsException(OgoneException):
    pass

class UnknownStatusException(OgoneException):
    def __init__(self, status):
        assert isinstance(status, int)

        self.status = status

    def __unicode__(self):
        from django_ogone.ogone import Ogone

        try:
            description = Ogone.get_status_description(self.status)
            return u'Ogone returned unknown status: %s (%d)' % \
                (description, self.status)
        except:
            return u'Ogone returned unknown status: %d' % self.status

    def __str__(self):
        return repr(self.parameter)

