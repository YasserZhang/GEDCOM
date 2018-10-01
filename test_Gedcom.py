# unit testing gedcom parser
import unittest
from Gedcom import Gedcom
import json


class TestGedcomParser(unittest.TestCase):

    def test_marriage_before_divorce(self,
                                     file_path='test_files/Family.ged',
                                     ground_truth_file_path='test_files/gf.json'):
        ged = Gedcom()
        ged.parse(file_path)
        checked_results = ged.check_marriage_before_divorce()
        print(checked_results)
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        print(checked_results)
        for key in ground_truths:
            self.assertTrue(key in checked_results)
            self.assertEqual(ground_truths[key], str(checked_results[key]))
        print("check_marriage_before_divorce test on {f} passed.".format(f=file_path))

    def test_divorce_before_death(self, 
                    file_path='test_files/Family.ged', 
                    ground_truth_file_path='test_files/divorce_before_death.json'):
        ged = Gedcom()
        ged.parse(file_path)
        ged.print_individuals()
        ged.print_families()
        checked_results = ged.check_divorce_before_death()
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in checked_results)
            self.assertEqual(ground_truths[key], checked_results[key])
        print("check_divorce_before_death test on {f} passed.".format(f=file_path))

    # testcase for user story 03:
    def test_birth_before_death(self,
                                file_path='test_files/Family.ged',
                                ground_truth_file_path='test_files/testcase_03.json'):
        ged = Gedcom()
        ged.parse(file_path)
        check_results = ged.check_birth_before_death()
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in check_results)
            self.assertEqual(ground_truths[key], check_results[key])
        print("Check_Birth_Before_Death test passed on {f}".format(f=file_path))

    # testcase for user story 08:
    def test_childbirth_before_parentsMarriage(self,
                                              file_path='test_files/Family.ged',
                                              ground_truth_file_path='test_files/testcase_08.json'):
        ged = Gedcom()
        ged.parse(file_path)
        check_results = ged.check_childbirth_before_parents_marriage()
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in check_results)
            #print("This is ground", ground_truths[key])
            self.assertEqual(ground_truths[key], check_results[key])
        print("Check_ChildBirth_Before_ParentsMariage test passed on {f}".format(f=file_path))

    def test_marriage_before_death(self, 
                    file_path='test_files/Family.ged', 
                    ground_truth_file_path='test_files/marriage_before_death.json'):
        ged = Gedcom()
        ged.parse(file_path)
        checked_results = ged.check_marriage_before_death()
        # print(checked_results)
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in checked_results)
            self.assertEqual(ground_truths[key], checked_results[key])
        print("check_marriage_before_death test on {f} passed.".format(f=file_path))

    def test_marriage_after_fourteen(self, file_path='test_files/Family.ged', ground_truth_file_path='test_files/marriage_before_fourteen.json'):
        ged = Gedcom()
        ged.parse(file_path)
        checked_results = ged.check_marriage_after_fourteen()
        # print(checked_results)
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in checked_results)
            self.assertEqual(ground_truths[key], checked_results[key])
        print("check_marriage_after_fourteen test on {f} passed.".format(f=file_path))


if __name__ == "__main__":
    unittest.main()
