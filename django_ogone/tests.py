import unittest
import doctest

from django_ogone import security

# class FooTestCase(unittest.TestCase):
#     def testFoo(self):
#         self.assertEquals('foo', 'bar')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(security))
    #suite.addTest(unittest.TestLoader().loadTestsFromTestCase(FooTestCase))
    return suite
