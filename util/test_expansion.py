import unittest
from qvvars import *
class TestExpand(unittest.TestCase):

    # def setUp(self):
    #     self.seq = range(10)

    def test_readerDummmy(self):
        reader = QvVarFileReader({})
        reader.parse_content('')


    #     # should raise an exception for an immutable sequence
    #     self.assertRaises(TypeError, random.shuffle, (1,2,3))

    # def test_choice(self):
    #     element = random.choice(self.seq)
    #     self.assertTrue(element in self.seq)

    # def test_sample(self):
    #     with self.assertRaises(ValueError):
    #         random.sample(self.seq, 20)
    #     for element in random.sample(self.seq, 5):
    #         self.assertTrue(element in self.seq)

def testExpansion(content):
    reader = QvVarFileReader({})
    reader.parsedContent(content)
    


if __name__ == '__main__':
    unittest.main()