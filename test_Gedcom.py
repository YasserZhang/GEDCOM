# unit testing gedcom parser
import unittest
from Gedcom import Gedcom
import json

class TestGedcomParser(unittest.TestCase):

    def _check_ground_truth(self, checked_results, ground_truth_file_path):
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in checked_results)
            self.assertEqual(ground_truths[key], checked_results[key])

    # US04 marriage before divorce
    def test_marriage_before_divorce(self,
                                     file_path='test_files/Family.ged',
                                     ground_truth_file_path='test_files/gf.json'):
        ged = Gedcom()
        ged.parse(file_path)
        checked_results = ged.check_marriage_before_divorce()
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in checked_results)
            self.assertEqual(ground_truths[key], str(checked_results[key]))
        #print("check_marriage_before_divorce test on {f} passed.".format(f=file_path))

    # US06 divorce before death
    def test_divorce_before_death(self, 
                    file_path='test_files/Family.ged', 
                    ground_truth_file_path='test_files/divorce_before_death.json'):
        ged = Gedcom()
        ged.parse(file_path)
        checked_results = ged.check_divorce_before_death()
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in checked_results)
            self.assertEqual(ground_truths[key], checked_results[key])
        #print("check_divorce_before_death test on {f} passed.".format(f=file_path))

    # testcase for user story 03:
    def test_birth_before_death(self,
                                file_path='test_files/Family.ged',
                                ground_truth_file_path='test_files/testcase_03.json'):
        ged = Gedcom()
        ged.parse(file_path)
        ged.print_individuals()
        ged.print_families()
        check_results = ged.check_birth_before_death()
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in check_results)
            #print(ground_truths[key])
            self.assertEqual(ground_truths[key], check_results[key])
        #print("Check_Birth_Before_Death test passed on {f}".format(f=file_path))

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
            self.assertEqual(ground_truths[key], check_results[key])
        #print("Check_ChildBirth_Before_ParentsMariage test passed on {f}".format(f=file_path))

    # US05 marriage before death
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
        #print("check_marriage_before_death test on {f} passed.".format(f=file_path))

    # US10 marriage after 14
    def test_marriage_after_fourteen(self, file_path='test_files/Family.ged', ground_truth_file_path='test_files/marriage_before_fourteen.json'):
        ged = Gedcom()
        ged.parse(file_path)
        checked_results = ged.check_marriage_after_fourteen()
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in checked_results)
            self.assertEqual(ground_truths[key], checked_results[key])
        #print("check_marriage_after_fourteen test on {f} passed.".format(f=file_path))

    # testcase for user story 02:
    def test_birth_before_marriage(self,
                                file_path='test_files/Family.ged',
                                ground_truth_file_path='test_files/testcase_02.json'):
        ged = Gedcom()
        ged.parse(file_path)
        check_results = ged.check_birth_before_marriage()
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in check_results)
            self.assertEqual(ground_truths[key], check_results[key])
        #print("Check_Birth_Before_Marriage test passed on {f}".format(f=file_path))

    # testcase for user story 07:
    def test_age_lessthan_150(self,
                                file_path='test_files/Family.ged',
                                ground_truth_file_path='test_files/testcase_07.json'):
        ged = Gedcom()
        ged.parse(file_path)
        check_results = ged.check_age_lessthan_150()
        with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in check_results)
            self.assertEqual(ground_truths[key], check_results[key])
        #print("Check_Age_LessThan_150 test passed on {f}".format(f=file_path))

    # Sprint 2
    # test US16
    def test_male_last_names(self, file_path='test_files/Family.ged', ground_truth_file_path='test_files/male_last_names.json'):
        ged = Gedcom()
        ged.parse(file_path)
        checked_results = ged.check_male_last_names()
        self._check_ground_truth(checked_results, ground_truth_file_path)

    # testcase US 09
    def test_old_parents(self,
                    file_path='test_files/Family.ged',
                    ground_truth_file_path='test_files/testcase_09.json'):
        ged = Gedcom()
        ged.parse(file_path)
        check_results = ged.check_old_parents()
        with open(ground_truth_file_path, 'r') as f:
                ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in check_results)
            self.assertEqual(ground_truths[key], check_results[key])
        #print("Check_old_parents test passed on {f}.".format(f=file_path))

    # testcase US 12
    def test_birth_before_death_of_parents(self,
                    file_path='test_files/Family.ged',
                    ground_truth_file_path='test_files/testcase_12.json'):
    	ged = Gedcom()
    	ged.parse(file_path)
    	check_results = ged.check_birth_before_death_of_parents()
    	with open(ground_truth_file_path, 'r') as f:
            ground_truths = json.load(f)
    	for key in ground_truths:
            #print(ground_truths[key])
            self.assertTrue(key in check_results)
            self.assertEqual(ground_truths[key], check_results[key])
    	#print("Check_birth_before_death_of_parents test passed on {f}".format(f=file_path))

    # testcase US 17
    def test_marry_descendants(self,file_path='test_files/Family.ged'):
        ged = Gedcom()
        ged.parse(file_path)
        check_results=ged.check_marry_descendants()
        return check_results

    # Testcase US 14
    def test_check_multiple_births(self, file_path='test_files/Family.ged',
                                    ground_truth_file_path='test_files/testcase_14.json'):
        ged = Gedcom()
        ged.parse(file_path)
        checked_results = ged.check_multiple_births()
        self._check_ground_truth(checked_results, ground_truth_file_path)

    # Testcase US 15
    def test_check_siblings_count(self, file_path='test_files/Family.ged',
                                  ground_truth_file_path='test_files/testcase_15.json'):
        ged = Gedcom()
        ged.parse(file_path)
        checked_results = ged.check_siblings_count()
        self._check_ground_truth(checked_results, ground_truth_file_path)

if __name__ == "__main__":
    unittest.main() 
