# coding=utf-8
# 

import unittest2
from os.path import join
import random
from tradefeed_cmbhk.mysql import findOrCreateIdFromHash



class TestMySQL(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestMySQL, self).__init__(*args, **kwargs)


    @classmethod
    def setUp(cls):
        random.seed()


    def testFindOrCreateIdFromHash(self):
        x = str(random.randint(0, 1000000000))
        id1 = findOrCreateIdFromHash('test', x)
        self.assertTrue(id1 != None)

        id2 = findOrCreateIdFromHash('test', x)
        self.assertEqual(id1, id2)
