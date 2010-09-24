import unittest
import doctest

from django_ogone import security


class OgoneTestCase(unittest.TestCase):
    def setUp(self):
        from django_ogone import Ogone
        
        self.ogone = Ogone
        
    def testValidHash(self):
        params = {u'ORDERID': u'13', u'STATUS': u'9', u'CARDNO': u'XXXXXXXXXXXX1111', u'VC': u'NO', u'PAYID': u'8285812', u'CN': u'Kaast Achternaam', u'NCERROR': u'0', u'IP': u'82.139.114.10', u'IPCTY': u'NL', u'CURRENCY': u'EUR', u'CCCTY': u'US', u'SHASIGN': u'D90EFA06285DA1344F4CC7E5EF1887C2B2F28AAF35A5E2BE8666C0C6FCC41710B77D1662FC86A030AC8B032A2C819AC6B8E3DD36D80E2ED1A0947B4B83DD1C99', u'AAVCHECK': u'NO', u'BRAND': u'VISA', u'ACCEPTANCE': u'test123', u'ECI': u'7', u'TRXDATE': u'09/24/10', u'AMOUNT': u'6794.81', u'CVCCHECK': u'NO', u'ED': u'0111', u'PM': u'CreditCard'}
        
        o = self.ogone(params)
        self.assert_(o.is_valid())

    def testInvalidHash(self):
        params = {u'ORDERID': u'12', u'STATUS': u'9', u'CARDNO': u'XXXXXXXXXXXX1111', u'VC': u'NO', u'PAYID': u'8285812', u'CN': u'Kaast Achternaam', u'NCERROR': u'0', u'IP': u'82.139.114.10', u'IPCTY': u'NL', u'CURRENCY': u'EUR', u'CCCTY': u'US', u'SHASIGN': u'D90EFA06285DA1344F4CC7E5EF1887C2B2F28AAF35A5E2BE8666C0C6FCC41710B77D1662FC86A030AC8B032A2C819AC6B8E3DD36D80E2ED1A0947B4B83DD1C99', u'AAVCHECK': u'NO', u'BRAND': u'VISA', u'ACCEPTANCE': u'test123', u'ECI': u'7', u'TRXDATE': u'09/24/10', u'AMOUNT': u'6794.81', u'CVCCHECK': u'NO', u'ED': u'0111', u'PM': u'CreditCard'}
        
        o = self.ogone(params)
        self.assertFalse(o.is_valid())
    
    def testParseParams(self):
        params = {u'ORDERID': u'13', u'STATUS': u'9', u'CARDNO': u'XXXXXXXXXXXX1111', u'VC': u'NO', u'PAYID': u'8285812', u'CN': u'Kaast Achternaam', u'NCERROR': u'0', u'IP': u'82.139.114.10', u'IPCTY': u'NL', u'CURRENCY': u'EUR', u'CCCTY': u'US', u'SHASIGN': u'D90EFA06285DA1344F4CC7E5EF1887C2B2F28AAF35A5E2BE8666C0C6FCC41710B77D1662FC86A030AC8B032A2C819AC6B8E3DD36D80E2ED1A0947B4B83DD1C99', u'AAVCHECK': u'NO', u'BRAND': u'VISA', u'ACCEPTANCE': u'test123', u'ECI': u'7', u'TRXDATE': u'09/24/10', u'AMOUNT': u'6794.81', u'CVCCHECK': u'NO', u'ED': u'0111', u'PM': u'CreditCard'}
        
        o = self.ogone(params)
        o.parse_params()
        
        self.assertEqual(o.get_orderid(), 13)
        self.assertEqual(o.get_status(), 9)
        self.assertEqual(o.get_status_description(), 'Payment requested')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(security))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(OgoneTestCase))
    return suite
