
# coding: utf-8

# In[ ]:


import unittest
from Gedcom import Gedcom
import json


class TestBirthBeforeDeath(unittest.TestCase):

    # testcase for user story 03:
    def test_birth_before_death(self,
                                file_path='test_files/Family.ged',
                                ground_truth_file_path='test_files/ '):
        ged = Gedcom()
        ged.parse(file_path)
        check_results = ged.check_birth_before_death()
        with open(ground_truth_file, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.aseertTrue(key in check_results)
            self.assertEqual(ground_truths[key], check_results[key])
        print("Check_Birth_Before_Death test passed on {f} passed.".format(f=file_path))

    # testcase for user story 08:
    def test_childbirth_before_parentsMarriage(self,
                                              file_path='test_files/Family.ged',
                                              ground_truth_file_path='test_files/ '):
        ged = Gedcom()
        ged.parse(file_path)
        check_results = ged.check_childbirth_before_parents_marriage()
        with open(ground_truth_file, 'r') as f:
            ground_truths = json.load(f)
        for key in ground_truths:
            self.assertTrue(key in check_results)
            self.assertEqual(ground_truths[key], check_results[Key])
        print("Check_ChildBirth_Before_ParentsMariage test passed on {f} passed.".format(f=file_path))


