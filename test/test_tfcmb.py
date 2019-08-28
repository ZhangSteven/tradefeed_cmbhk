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
        holding = list(readHolding(open_workbook(inputFile).sheet_by_index(0), 3))
        self.assertEqual(3, len(holding))
        self.verifyHolding(holding[0])



    def verifyHolding(self, record):
        """
        First trade
        """
        self.assertEqual(len(record), 19)
        self.assertEqual('US912828YB05', record['ISIN'])
        self.assertEqual(1.625, record['Coupon'])
        self.assertEqual('B', record['B/S'])
        self.assertEqual('08082019', record['As of Dt'])
        self.assertEqual('08152019', record['Stl Date'])
        self.assertEqual(1000000, record['Amount Pennies'])
        self.assertAlmostEqual(99.15234375, record['Price'])
        self.assertAlmostEqual(991523.44, record['Settle Amount'])


