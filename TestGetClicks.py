import unittest

import GetClicks as gc


class MyTestCase(unittest.TestCase):

    def test_read_number_from_key(self):
        test_string = ("are finished.\n\n\n\"\",\"\"value\"\":[{\"\"x\"\":73.41880798339844,"
                       "\"\"y\"\":159.14012145996094,\"\"tool\"\":5,\"\"frame\"\":0,\"\"deta")

        number, next_key = gc.read_number_from_key(test_string, gc.X_PREFIX)
        self.assertEqual(73.41880798339844, float(number))  # add assertion here
        self.assertEqual(54, next_key)  # add assertion here
        number, next_key = gc.read_number_from_key(test_string, gc.Y_PREFIX, 54)
        self.assertEqual(159.14012145996094, float(number))  # add assertion here
        self.assertEqual(79, next_key)  # add assertion here
        number, next_key = gc.read_number_from_key(test_string, gc.TOOL_PREFIX, 79)
        self.assertEqual(5, int(number))  # add assertion here
        self.assertEqual(90, next_key)  # add assertion here


if __name__ == '__main__':
    unittest.main()
