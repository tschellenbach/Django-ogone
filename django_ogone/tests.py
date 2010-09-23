import unittest
import doctest

from django_ogone import ogone

# class FooTestCase(unittest.TestCase):
#     def testFoo(self):
#         self.assertEquals('foo', 'bar')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(ogone))
    #suite.addTest(unittest.TestLoader().loadTestsFromTestCase(FooTestCase))
    return suite
