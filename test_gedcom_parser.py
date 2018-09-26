# unit testing gedcom parser
import unittest
from gedcom_parser import Gedcom


class TestGedcomParser(unittest.TestCase):
    def test_Gedcom_parse(self, file_path):
        ged = Gedcom()
        ged.parse(file_path)


if __name__ == "__main__":
    test = TestGedcomParser()
    test.test_Gedcom_parse('Family.ged')
