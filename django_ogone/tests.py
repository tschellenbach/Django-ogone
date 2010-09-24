import unittest
import doctest

from django_ogone import security, ogone

# class FooTestCase(unittest.TestCase):
#     def testFoo(self):
#         self.assertEquals('foo', 'bar')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(security))
    suite.addTest(doctest.DocTestSuite(ogone))
    #suite.addTest(unittest.TestLoader().loadTestsFromTestCase(FooTestCase))
    return suite
