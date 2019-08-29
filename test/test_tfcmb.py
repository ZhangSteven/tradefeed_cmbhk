# coding=utf-8
# 

import unittest2
from os.path import join
from tradefeed_cmbhk.utility import getCurrentDir
from tradefeed_cmbhk.tfcmb import readHolding
from xlrd import open_workbook



class TestTFCmb(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTFCmb, self).__init__(*args, **kwargs)


    def testReadHolding(self):
        inputFile = join(getCurrentDir(), 'samples', 'TD08082019.xlsx')
        date, holding = (lambda x: (x[0], list(x[1])))(readHolding(inputFile))
        self.assertEqual('2019-08-08', date)
        self.assertEqual(3, len(holding))
        self.verifyHolding(holding[0])



    def testReadHolding2(self):
        inputFile = join(getCurrentDir(), 'samples', 'TD22082019.xlsx')
        date, holding = (lambda x: (x[0], list(x[1])))(readHolding(inputFile))
        self.assertEqual('2019-08-22', date)
        self.assertEqual(2, len(holding))
        self.verifyHolding2(holding[1])



    def verifyHolding(self, record):
        """
        First trade
        """
        self.assertEqual(len(record), 20)
        self.assertEqual('40017-B', record['Fund'])
        self.assertEqual('US912828YB05', record['ISIN'])
        self.assertEqual(1.625, record['Coupon'])
        self.assertEqual('B', record['B/S'])
        self.assertEqual('08082019', record['As of Dt'])
        self.assertEqual('15082019', record['Stl Date'])
        self.assertEqual(1000000, record['Amount Pennies'])
        self.assertAlmostEqual(99.15234375, record['Price'])
        self.assertAlmostEqual(991523.44, record['Settle Amount'])



    def verifyHolding2(self, record):
        self.assertEqual(len(record), 20)
        self.assertEqual('40017-B', record['Fund'])
        self.assertEqual('XS1627599142', record['ISIN'])
        self.assertEqual(6.25, record['Coupon'])
        self.assertEqual('S', record['B/S'])
        self.assertEqual('22082019', record['As of Dt'])
        self.assertEqual('26082019', record['Stl Date'])
        self.assertEqual(1000000, record['Amount Pennies'])
        self.assertEqual(93.625, record['Price'])
        self.assertAlmostEqual(946319.44, record['Settle Amount'])


