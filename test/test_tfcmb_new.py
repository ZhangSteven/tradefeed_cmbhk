# coding=utf-8
# 

import unittest2
from os.path import join
from tradefeed_cmbhk.utility import getCurrentDir
from tradefeed_cmbhk.tfcmb import readHolding, cmbPosition
from functools import partial
from xlrd import open_workbook


class TestTFCmbNew(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTFCmbNew, self).__init__(*args, **kwargs)

    def testReadHolding(self):
        inputFile = join(getCurrentDir(), 'samples', 'TD_40017_new.xlsx')
        date, holding = (lambda x: (x[0], list(x[1])))(readHolding(inputFile))
        self.assertEqual('09Jul2021', date)
        self.assertEqual(2, len(holding))

    def testCmbPosition(self):
        inputFile = join(getCurrentDir(), 'samples', 'TD_40017_new.xlsx')
        holding = list(map(partial(cmbPosition, 'test'), readHolding(inputFile)[1]))
        self.verifyCmbHolding(holding[0])

    def verifyCmbHolding(self, record):
        self.assertEqual('20190519052401	', record['CLIENT A/C NO.'])
        self.assertEqual('11', record['SEC ID TYPE'])
        self.assertEqual('XS2016010881', record['SEC ID'])
        self.assertEqual('SELL', record['TRAN TYPE'])
        self.assertEqual('09072021', record['TRADE DATE'])
        self.assertEqual('13072021', record['SETT DATE'])
        self.assertEqual(500000, record['QTY/NOMINAL'])
        self.assertEqual('USD', record['SEC CCY'])
        self.assertEqual('USD', record['SETT CCY'])
        self.assertEqual(103, record['PRICE'])
        self.assertEqual(515000, record['GROSS AMT'])
        self.assertEqual('USD', record['FEE CCY'])
        self.assertEqual(8458.33, record['ACCRUED INT'])
        self.assertEqual(523458.33, record['NET AMT'])
        self.assertEqual(523458.33, record['NET AMT BASE'])
