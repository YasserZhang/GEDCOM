
# coding: utf-8

# In[1]:


# Check if the birth date is before the death date

class Gedcom:

    # user story 03
    def check_birth_before_death(self):
        individuals = self.get_individuals()
        check_results = {}
        for indi_key in individuals:
            individual = individuals[indi_key]
            birth_date = individual.get_birth()
            death_date = individual.get_death()
            indi_id = individual.get_id()
            if death_date:
                if birth_date > death_date:
                    check_results[indi_id] = "Error"
                else:
                    check_results[indi_id] = "N/A"
            else:
                check_results[indi_id] = "N/A"
        return check_results

    # user story 08
    def check_childbirth_before_parents_marriage(self):
        families = self.get_families()
        check_results = {}
        for key in families:
            family = families[key]
            fam_id = family.get_id()
            fam_marriage_date = family.get_marriage_date()
            fam_children = family.list_children_ids()
            for key in fam_children:
                child = self.get_individual_by_id(key)
                child_birthday = child.get_birth()
                if fam_marriage_date < child_birthday:
                    check_results[fam_id + "-" + child.get_id()] = "no"
                else:
                    check_results[fam_id + "-" + child.get_id()] = "yes"
        return check_results

