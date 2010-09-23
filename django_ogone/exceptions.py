
class InvalidSignatureException(Exception):
    pass
    
class InvalidParamsException(Exception):
    pass

class UnknownStatusException(Exception):
   def __init__(self, status):
       self.status = status
   
   def __unicode__(self):
       return u'Ogone returned an unkown status code \'%s\'' % self.status

   def __str__(self):
       return repr(self.parameter)