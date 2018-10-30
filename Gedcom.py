# design classes
# global names
from datetime import timedelta, date

import prettytable

INFO_TAGS = {'NAME': 'Name', 'SEX': 'Gender'}
FAM_TAGS = {'FAMC': 'Child', 'FAMS': 'Spouse'}
DATE_TAGS = {'BIRT': 'Birthday', 'DEAT': 'Death'}
FAM_DATE_TAGS = {'MARR': 'Married', 'DIV': 'Divorced'}
RELATION_TAGS = {'HUSB': 'Husband_ID', 'WIFE': 'Wife_ID'}
CHILD = {'CHIL': 'Children'}
MONTHS = {
    'JAN': 1,
    'FEB': 2,
    'MAR': 3,
    'APR': 4,
    'MAY': 5,
    'JUN': 6,
    'JUL': 7,
    'AUG': 8,
    'SEP': 9,
    'OCT': 10,
    'NOV': 11,
    'DEC': 12}
INDIVIDUAL = 'INDI'
FAMILY = 'FAM'
ZERO_LEVEL_TRIVIAL_LINE_SEGMENTS_LENGTH = 2

# supporting functions
def families(gedcom):
    return list(gedcom.get_families().values())

def individuals(gedcom):
    return list(gedcom.get_individuals().values())

def divorce_date(family):
    return family.get_divorce_date()

def marriage_date(family):
    return family.get_marriage_date()

def id_(Instance):
    # this instance can either be family or individual
    return Instance.get_id()

def wife(family):
    return family.get_wife_id()

def husband(family):
    return family.get_husband_id()

# Gedcom is a tree including families and individuals
class Gedcom:
    def __init__(self):
        self.__individual_dict = {}
        self.__family_dict = {}

    def parse(self, file_path):
        # read in file line by line
        # create individuals, storing in the __individual_dict
        # create families, storing in the __family_dict
        with open(file_path, 'r') as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                segments = lines[i].strip().split()
                if segments[0] == '0' and len(segments) > ZERO_LEVEL_TRIVIAL_LINE_SEGMENTS_LENGTH:
                    row_dict = {'id': segments[1]}
                    if segments[2] == INDIVIDUAL:
                        row_dict, i = self.__generate_individual_dict(lines, i+1, row_dict)
                        indi = Individual()
                        indi.read_in(row_dict)
                        self.__add_an_individual(indi)
                    elif segments[2] == FAMILY:
                        row_dict, i = self.__generate_family_dict(lines, i+1, row_dict)
                        fam = Family()
                        fam.read_in(row_dict)
                        self.__add_a_family(fam)
                    else:
                        i += 1
                else:
                    #print("Warning: This line may contain incorrect format or be skipped.")
                    #print(lines[i])
                    i += 1
        self.__connect()
        self.__update_derivative_attributes()
        #self.print_individuals()
        #self.print_families()

    def __generate_individual_dict(self, lines, start_index, indi_row):
        while start_index < len(lines):
            line = lines[start_index].strip()
            if line.startswith('1'):
                segments = line.split()
                if segments[1] in INFO_TAGS:
                    indi_row[INFO_TAGS[segments[1]]] = ' '.join(segments[2:])
                elif segments[1] in DATE_TAGS:
                    start_index += 1
                    new_line = lines[start_index].strip()
                    date_ = self.__get_date(new_line)
                    indi_row[DATE_TAGS[segments[1]]] = date_
                elif segments[1] in FAM_TAGS:
                    indi_row[FAM_TAGS[segments[1]]] = indi_row.get(FAM_TAGS[segments[1]], {})
                    indi_row[FAM_TAGS[segments[1]]].update({segments[2]: None})
            elif line.startswith('0'):
                break
            else:
                raise ValueError("{} breaks the file format, check its validity.".format(line))
            start_index += 1
        # deal with derivative rows, age and alive
        if 'Birthday' not in indi_row:
            raise("Birthday is not found for the individual {id_}".format(id_=indi_row['id']))
        if 'Death' in indi_row:
            indi_row['Age'] = indi_row['Death'].year - indi_row['Birthday'].year
            indi_row['Alive'] = False
        else:
            indi_row['Age'] = date.today().year - indi_row['Birthday'].year
            indi_row['Alive'] = True
            indi_row['Death'] = None
        return indi_row, start_index

    def __generate_family_dict(self, lines, start_index, fam_row):
        while start_index < len(lines):
            line = lines[start_index].strip()
            if line.startswith('1'):
                segments = line.split()
                if segments[1] in RELATION_TAGS:
                    fam_row[RELATION_TAGS[segments[1]]] = segments[2]
                elif segments[1] in CHILD:
                    fam_row[CHILD[segments[1]]] = fam_row.get(CHILD[segments[1]], {})
                    fam_row[CHILD[segments[1]]].update({segments[2]: None})
                elif segments[1] in FAM_DATE_TAGS:
                    start_index += 1
                    new_line = lines[start_index].strip()
                    date_ = self.__get_date(new_line)
                    fam_row[FAM_DATE_TAGS[segments[1]]] = date_
            elif line.startswith('0'):
                break
            else:
                raise ValueError("{} breaks the file format, check its validity.".format(line))
            start_index += 1
        return fam_row, start_index

    @staticmethod
    def __get_date(line):
        segments = line.split()
        # check if this line's tag is DATE
        if segments[1] != 'DATE':
            raise ValueError("This line does not include the tag of DATE.")
        try:
            day, month, year = int(segments[2]), MONTHS[segments[3]], int(segments[4])
        except Exception as e:
            print("marriage date format is invalid.")
            raise e
        return date(year, month, day)

    def __connect(self):
        for key in self.__individual_dict:
            indi = self.__individual_dict[key]
            for fam_child_key in indi.list_parents_families_ids():
                fam = self.__family_dict[fam_child_key]
                indi.set_parent_family_by_id(fam_child_key, fam)
            for fam_spouse_key in indi.list_own_families_ids():
                fam = self.__family_dict[fam_spouse_key]
                indi.set_own_family_by_id(fam_spouse_key, fam)
        for key in self.__family_dict:
            fam = self.__family_dict[key]
            for child_key in fam.list_children_ids():
                child = self.__individual_dict[child_key]
                fam.set_child_by_id(child_key, child)

    def __update_derivative_attributes(self):
        for key in self.__family_dict:
            fam = self.__family_dict[key]
            try:
                wife = self.__individual_dict[fam.get_wife_id()]
                fam.set_wife_name(wife.get_name())
            except KeyError:
                print("wife of family {fam_id} is not found.".format(fam_id=key))
            try:
                husband = self.__individual_dict[fam.get_husband_id()]
                fam.set_husband_name(husband.get_name())
            except KeyError:
                print("Husband of family {fam_id} is not found.".format(fam_id=key))

    def __add_an_individual(self, indi):
        self.__individual_dict[indi.get_id()] = indi

    def __add_a_family(self, fam):
        self.__family_dict[fam.get_id()] = fam

    def print_families(self):
        family_table = prettytable.PrettyTable()
        family_table.field_names = ["ID",
                                    "Married",
                                    "Divorced",
                                    "Husband_ID",
                                    "Husband Name",
                                    "Wife Id",
                                    "Wife Name",
                                    "Children"]
        for key in self.__family_dict:
            fam = self.__family_dict[key]
            family_row = fam.get_family()
            family_row = ["NA" if x is None else x for x in family_row]
            family_table.add_row(family_row)
        print(family_table)

    def print_individuals(self):
        individual_table = prettytable.PrettyTable()
        individual_table.field_names = ['ID',
                                        'Name',
                                        'Gender',
                                        'Birthday',
                                        'Age',
                                        'Alive',
                                        'Death',
                                        'Spouse',
                                        'Child']
        for key in self.__individual_dict:
            individual = self.__individual_dict[key]
            individual_row = individual.get_individual()
            individual_row = ["NA" if x is None else x for x in individual_row]
            individual_table.add_row(individual_row)
        print(individual_table)

    def get_families(self):
        return self.__family_dict

    def get_individuals(self):
        return self.__individual_dict

    def get_individual_by_id(self, id_):
        return self.__individual_dict[id_]

    # US04 Marriage before Divorce
    def check_marriage_before_divorce(self):
        results = {}
        for family in families(self):
            result = self.__compare_marriage_divorce(family)
            results[id_(family)] = result
        return results

    @staticmethod
    def __compare_marriage_divorce(family):
        if marriage_date(family) and divorce_date(family):
            if marriage_date(family) > divorce_date(family):
                print("ERROR in US04: Family {id_}'s marriage Date({m_t}) is later than the divorce date ({d_t}).".format(
                    id_=family.get_id(), m_t=marriage_date(family), d_t=divorce_date(family)))
                return False
        elif marriage_date(family) is None:
            if divorce_date(family):
                print("ERROR in US04: Family {id_} has divorce date ({d_t}) but no marriage date.".format(
                    id_=id_(family), d_t=divorce_date(family)))
                return False
            else:
                print("ERROR in US04: Family {id_} does not have marriage date".format(id_=id_(family)))
                return False
        return True

    # US06 Divorce before death
    def check_divorce_before_death(self):
        individuals = self.get_individuals()
        checked_results = {}
        for indi_key in individuals:
            individual = individuals[indi_key]
            death_date = individual.get_death()
            indi_id = individual.get_id()
            own_families = individual.get_own_families()
            if death_date is None or len(own_families) == 0:
                checked_results[indi_id] = "NA"
                continue
            for fam_key in own_families:
                own_family = own_families[fam_key]
                fam_id = own_family.get_id()
                divorce_date = own_family.get_divorce_date()
                result = self.__compare_divorce_death(divorce_date, death_date, indi_id, fam_id, checked_results)
                checked_results[indi_id] = result
        return checked_results

    @staticmethod
    def __compare_divorce_death(divorce_date, death_date, indi_id, fam_id, checked_results):
        if divorce_date:
            if divorce_date > death_date:
                print("ERROR US06: Individual {i_id} of Family {f_id} has a divorce date {div_d} after the date of death {d_d}.".format(
                    i_id=indi_id,
                    f_id = fam_id,
                    div_d=divorce_date.strftime("%Y-%m-%d"),
                    d_d=death_date.strftime("%Y-%m-%d")))
                return "No"
            else:
                return "Yes"
        else:
            if indi_id in checked_results:
                return checked_results[indi_id]
            return "Yes"

    # US05 Marriage before Death
    def check_marriage_before_death(self):
        individuals = self.get_individuals()
        checked_results = {}
        for indi_key in individuals:
            individual = individuals[indi_key]
            death_date = individual.get_death()
            indi_id = individual.get_id()
            own_families = individual.get_own_families()
            if death_date is None or len(own_families) == 0:
                checked_results[indi_id] = "NA"
                continue
            for fam_key in own_families:
                own_family = own_families[fam_key]
                marriage_date = own_family.get_marriage_date()
                result = self.__compare_marriage_death(marriage_date, death_date, indi_id)
                checked_results[indi_id] = result
        return checked_results

    @staticmethod
    def __compare_marriage_death(marriage_date, death_date, indi_id):
        if marriage_date:
            if marriage_date > death_date:
                print("ERROR US05: Individual {i_id} has a marriage date {div_d} after the date of death {d_d}.".format(
                    i_id=indi_id,
                    div_d=marriage_date.strftime("%Y-%m-%d"),
                    d_d=death_date.strftime("%Y-%m-%d")))
                return "No"
            else:
                return "Yes"
        else:
            return "Yes"

    # US10 Marriage after age fourteen
    def check_marriage_after_fourteen(self):
        individuals = self.get_individuals()
        checked_results = {}
        for indi_key in individuals:
            individual = individuals[indi_key]
            birth_date = individual.get_birth()
            indi_id = individual.get_id()
            own_families = individual.get_own_families()
            for fam_key in own_families:
                own_family = own_families[fam_key]
                marriage_date = own_family.get_marriage_date()
                result = self.__compare_marriage_age(marriage_date, birth_date, indi_id)
                checked_results[indi_id] = result
        return checked_results

    @staticmethod
    def __compare_marriage_age(marriage_date, birth_date, indi_id):
        if marriage_date:
            diff = abs(marriage_date.year - birth_date.year)
            if diff < 14:
                print("ERROR US10: Individual {i_id} has a marriage date {div_d} before the age of fourteen.".format(
                    i_id=indi_id,
                    div_d=marriage_date.strftime("%Y-%m-%d")))
                return "No"
            else:
                return "Yes"
        else:
            return "Yes"

    # US 03 Individual birth after death
    def check_birth_before_death(self):
        individuals = self.get_individuals()
        check_results = {}
        for indi_key in individuals:
            individual = individuals[indi_key]
            birth_date = individual.get_birth()
            death_date = individual.get_death()
            indi_id = individual.get_id()
            if death_date is not None and birth_date is not None:
                if birth_date > death_date:
                    check_results[indi_id] = "error"
                    print("ERROR in US03: Individual {i_id} has birth date after death date".format(i_id=indi_id))
                else:
                    check_results[indi_id] = "N/A"
            else:
                check_results[indi_id] = "N/A"
        return check_results

    # US 08 Child birth before Parents Marriage
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
                if fam_marriage_date is not None and child_birthday is not None:
                    if fam_marriage_date < child_birthday:
                        check_results[fam_id + "-" + child.get_id()] = "no"
                    else:
                        check_results[fam_id + "-" + child.get_id()] = "yes"
                        print("ERROR in US08: Found a child {c_id}'s birthday {c_birth} before the marriage date {m_d} of {c_id}'s parent family {f_id}.".format(
                            c_id=child.get_id(), m_d=fam_marriage_date, c_birth=child_birthday, f_id=fam_id))
        return check_results

    #US 02 Birth before Marriage
    def check_birth_before_marriage(self):
        individuals = self.get_individuals()
        checked_results = {}
        for indi_key in individuals:
            individual = individuals[indi_key]
            birth_date = individual.get_birth()
            indi_id = individual.get_id()
            own_families = individual.get_own_families()
            for fam_key in own_families:
                own_family = own_families[fam_key]
                marriage_date = own_family.get_marriage_date()
                result = self.__compare_marriage_birth(marriage_date, birth_date, indi_id)
                checked_results[indi_id] = result
        return checked_results

    @staticmethod
    def __compare_marriage_birth(marriage_date, birth_date, indi_id):
        if marriage_date:
            if marriage_date < birth_date:
                print("ERROR in US02: Individual {i_id} has a marriage date {div_d} before the individual is born.".format(
                    i_id=indi_id,
                    div_d=marriage_date.strftime("%Y-%m-%d")))
                return "No"
            else:
                return "Yes"
        else:
            return "N/A"

    #US 07 Less than 150 years old
    def check_age_lessthan_150(self):
        individuals = self.get_individuals()
        check_results = {}
        for indi_key in individuals:
            individual = individuals[indi_key]
            birth_date = individual.get_birth()
            death_date = individual.get_death()
            indi_id = individual.get_id()
            present_date = date.today()
            limit = timedelta(days=150*365)
            if death_date:
                if death_date - birth_date >= limit:
                    check_results[indi_id] = "Error"
                    print("ERROR in US07: Individual {i_id} age is more than 150 which is not possible".format(i_id=indi_id))
                else:
                    check_results[indi_id] = "Yes"
            else:
                if present_date - birth_date >= limit:
                    check_results[indi_id] = "Error"
                    print("ERROR in US07: Individual {i_id} age is more than 150 which is not possible".format(i_id=indi_id))
                else:
                    check_results[indi_id] = "Yes"
        return check_results

    # Sprint 2
    # US16 Male last names
    def check_male_last_names(self):
        families = self.get_families()
        checked_results = {}
        for fam_key in families:
            family = families[fam_key]
            fam_id = family.get_id()
            husband = self.__individual_dict[family.get_husband_id()]
            last_name = husband.get_name().split(" ")[1].strip()
            wife = self.__individual_dict[family.get_wife_id()]
            wife_last_name = wife.get_name().split(" ")[1].strip()
            if wife_last_name != last_name:
                print("ERROR in US16: Individual {i_id}'s last name {i_ln} does not match family {f_id}'s name {f_n}.".format(
                    i_id=wife.get_id(),i_ln=wife_last_name,f_id=fam_id,f_n=last_name))
                checked_results[fam_id] = "No"
            children = family.get_children()
            for _, child in children.items():
                child_last_name = child.get_name().split(" ")[1].strip()
                if child_last_name != last_name:
                    print("ERROR in US16: Individual {i_id}'s last name {i_ln} does not match family {f_id}'s name {f_n}.".format(
                                    i_id=child.get_id(),
                                    i_ln=child_last_name,
                                    f_id=fam_id,
                                    f_n=last_name))
                    checked_results[fam_id] = "No"
            if fam_id not in checked_results:
                checked_results[fam_id] = "Yes"
        return checked_results

    # US17 No marriages to descendants
    def check_marry_descendants(self):
        results = {}
        for individual in individuals(self):
            # get all descendants ids
            children_ids = set(individual.find_all_descendants())
            spouse_ids = individual.find_spouse_ids()
            spouse_is_a_descendant = False
            for spouse_id in spouse_ids:
                if spouse_id in children_ids:
                    print("ERROR in US17: Individual {i_id} married descendant {s_id}.".format(i_id=id_(individual), s_id=spouse_id))
                    results[id_(individual)] = "Error"
                    spouse_is_a_descendant = True
            if not spouse_is_a_descendant:
                results[id_(individual)] = "Correct"
        return results

    #US 13 Siblings spacing
    #def check_siblings_spacing(self):
    #   individuals = self.get_individuals()

    # US 09 Check for old parents
    def check_old_parents(self):
        families = self.get_families()
        check_results = {}
        for key in families:
            family = families[key]
            fam_id = family.get_id()
            husband_id = family.get_husband_id()
            wife_id = family.get_wife_id()

            husb = self.get_individual_by_id(husband_id)
            wife = self.get_individual_by_id(wife_id)

            husb_birth = husb.get_birth()
            wife_birth = wife.get_birth()

            if(husb_birth and wife_birth):
                if(date.today().year - husb_birth.year > 100 or date.today().year - wife_birth.year > 100):
                    check_results[fam_id] = "yes"
                    print("ERROR in US12: The husband or the wife or both in family {f} are too old".format(f=fam_id))
                else:
                    check_results[fam_id] = "no"
            else:
                check_results[fam_id] = "no"
                print("ERROR in US12: The birth date of husband or wife is missing!")
        return check_results

    # US 12 Check birth before death of parents
    def check_birth_before_death_of_parents(self):
        families = self.get_families()
        check_results = {}
        for key in families:
            family = families[key]
            fam_id = family.get_id()
            husband_id = family.get_husband_id()
            wife_id = family.get_wife_id()

            husb = self.get_individual_by_id(husband_id)
            wife = self.get_individual_by_id(wife_id)

            husb_birth = husb.get_birth()
            husb_death = husb.get_death()
            wife_birth = wife.get_birth()
            wife_death = wife.get_death()

            if(husb_death is not None):
                if(husb_birth.year < husb_death.year):
                    #print("1. ",husb_birth,"\t\t",husb_death)
                    check_results[fam_id] = "yes"
                else:
                    #print("2. ",husb_birth,"\t\t",husb_death)
                    check_results[fam_id] = "no"
                    print("ERROR in US09: In family {f_id}, the Father with {h_id} has a death date before birth".format(f_id=fam_id,h_id=husband_id))
            elif(wife_death is not None):
                if(wife_birth.year < wife_death.year):
                    #print("1. ",husb_birth,"\t\t",husb_death)
                    check_results[fam_id] = "yes"
                else:
                    #print("2. ",husb_birth,"\t\t",husb_death)
                    check_results[fam_id] = "no"
                    print("ERROR in US09: In family {f_id}, the Mother with {w_id} has a death date before birth".format(f_id=fam_id,w_id=wife_id))
            else:
                #print("3. ",husb_birth,"\t\t",husb_death)
                check_results[fam_id] = "yes"
        return check_results

    # US 14: Multiple births <= 5
    def check_multiple_births(self):
        families = self.get_families()
        check_results = {}
        flag = 0
        for key in families:
            family = families[key]
            fam_id = family.get_id()
            fam_children = family.list_children_ids()

            for ids, key in zip(range(len(fam_children)-1), fam_children):
                if len(fam_children) > 1:
                    fam_list = list(fam_children)
                    if self.get_individual_by_id(fam_list[ids]).get_birth() == \
                            self.get_individual_by_id(fam_list[ids+1]).get_birth():
                        flag += 1
                    else:
                        flag = 0
                else:
                    check_results[fam_id] = 'Yes'

            if flag >= 5:
                check_results[fam_id] = "No"
                print("ERROR in US14: Found multiple births at the same time greater than five in family {f}".format(f=fam_id))
            else:
                check_results[fam_id] = "Yes"
        return check_results

    # US 15: Fewer than 15 siblings
    def check_siblings_count(self):
        families = self.get_families()
        check_results = {}
        for key in families:
            family = families[key]
            fam_id = family.get_id()
            fam_children = family.list_children_ids()

            if len(fam_children) >= 15:
                check_results[fam_id] = "No"
                print("ERROR in US15: More than 15 siblings in in family {f}".format(f=fam_id))
            else:
                check_results[fam_id] = "Yes"

        return check_results

    # US21 Correct gender for role
    def check_Correct_gender(self): 
        families = self.get_families()
        check_results = {}
        for key in families:
            family = families[key]
            fam_id = family.get_id()
            husband_id = family.get_husband_id()
            wife_id = family.get_wife_id()

            husb = self.get_individual_by_id(husband_id)
            wife = self.get_individual_by_id(wife_id)

            husb_gender = husb.get_gender()
            wife_gender = wife.get_gender()

            if(husb_gender != 'M'):
                check_results[husband_id] = "Error"
                print("ERROR in US21: The husband {h} in the family {f} violates correct gender".format(h=husband_id, f=fam_id))
            else:
                check_results[husband_id] = "Yes"

            if(wife_gender != 'F'):
                check_results[wife_id] = "Error"
                print("ERROR in US21: The Wife {w} in the family {f} violates correct gender".format(w=wife_id, f=fam_id))
            else:
                check_results[wife_id] = "Yes"
        
        return check_results
    
    #Siblings Spacing US 13
    def check_sibling_spacing(self):
        families = self.get_families()
        #individuals = self.get_individuals()
        check_results = {}
        for key in families:
            family = families[key]
            fam_id = family.get_id()
            fam_children = family.list_children_ids()
            #print("list of children", fam_children)
            children_birth = []
            if len(list(fam_children)) < 2:
                #print("US 13: There are no childs or one child in family {f}".format(f=fam_id))
                check_results[fam_id] = "N/A" 
            else:
                for key in fam_children:
                    child = self.get_individual_by_id(key)
                    children_birth.append(child.get_birth())
                    children_birth = sorted(children_birth, reverse=False)
                    for x, y in zip(children_birth[::],children_birth[1::]):
                        #print ("for loop", x, y, fam_id)  
                        diff = y - x
                        if (diff > timedelta(days=2) and diff < timedelta(days=243)):
                            print("ERROR in US 13: Difference in sibling age is not possible in family {f}".format(f=fam_id))
                            check_results[fam_id] = "Error"
                        else: 
                            check_results[fam_id] = "Yes"
        #print(check_results)
        return check_results

    # Sprint 3

    # US 28 Order siblings by age
    def order_siblings_by_age(self):
        families = self.get_families()
        check_results = {}
        for key in families:
            family = families[key]
            fam_id = family.get_id()
            fam_children = family.list_children_ids()
            children_birth = []
            if len(list(fam_children)) < 2:
                print("ERROR in US 28: There are not enough children to sort in family {f}".format(f=fam_id))
                check_results[fam_id] = "No" # indicates that there is only 1 child
            else:
                check_results[fam_id] = "Yes"
                for key in fam_children:
                    child = self.get_individual_by_id(key)
                    children_birth.append(child.get_birth().year)
                    children_birth = sorted(children_birth, reverse=True)
        #print(children_birth)
        return check_results

    # US 34 large age difference between couple when married
    def large_age_difference(self):
        families = self.get_families()
        check_results = {}
        for key in families:
            family = families[key]
            fam_id = family.get_id()
            fam_marriage_date = family.get_marriage_date()

            if fam_marriage_date is not None:
                fam_marriage_date = fam_marriage_date.year
                subtract = date.today().year - fam_marriage_date # to find the #of years to be subtracted to get the age when married

                husband_id = family.get_husband_id()
                wife_id = family.get_wife_id()

                husb = self.get_individual_by_id(husband_id)
                wife = self.get_individual_by_id(wife_id)

                husb_age = date.today().year - husb.get_birth().year
                husb_age_when_married = husb_age - subtract

                wife_age = date.today().year - wife.get_birth().year
                wife_age_when_married = wife_age - subtract

                if(husb_age_when_married >= wife_age_when_married*2 or wife_age_when_married >= husb_age_when_married*2):
                    check_results[fam_id] = 'Yes'
                    print("ERROR in US 34: Either the Husband or the wife in family {f} had an age twice or more than the other".format(f=fam_id))
                else:
                    check_results[fam_id] = 'No'
            else:
                check_results[fam_id] = 'No'
        return check_results

    #US35 List recent births
    def check_recent_births(self):
        individuals = self.get_individuals()
        check_results = {}
        for indi_key in individuals:
            individual = individuals[indi_key]
            birth_date = individual.get_birth()
            #print("birth", birth_date)
            indi_id = individual.get_id()
            present_date = date.today()
            limit = timedelta(days=30)
            #print(present_date - birth_date, indi_id)
            if birth_date > present_date:
                print("Error in US35: The person {i} birth date is invalid".format(i=indi_id))
                check_results[indi_id] = "Error"
            elif present_date - birth_date <= limit:
                check_results[indi_id] = "Yes"
            else:
                check_results[indi_id] = "No" 
        #print(check_results)
        return check_results
    
    #US36 List recent deaths
    def check_recent_deaths(self):
        individuals = self.get_individuals()
        check_results = {}
        for indi_key in individuals:
            individual = individuals[indi_key]
            death_date = individual.get_death()
            #print("birth", birth_date)
            indi_id = individual.get_id()
            present_date = date.today()
            limit = timedelta(days=30)
            #print(present_date - birth_date, indi_id)
            if death_date:
                if death_date > present_date:
                    print("Error in US36: The person {i} death date is invalid".format(i=indi_id))
                    check_results[indi_id] = "Error"
                elif present_date - death_date <= limit:
                    check_results[indi_id] = "Yes"
                else:
                    check_results[indi_id] = "No"     
            else: 
                check_results[indi_id] = "N/A"
                #print("Error in US36: The person {i} is still alive".format(i=indi_id))
        #print(check_results)
        return check_results


#    #Sprint 4
#    #US22 Unique Id's
#    def check_unique_id(self):
#        families = self.get_families()
#        individuals = self.get_individuals()
#        check_results = {}
#        individual_list = []
#        family_list = []
#        for indi_key in individuals:
#            individual = individuals[indi_key]
#            indi_id = individual.get_id()
#            if indi_id in individual_list: 
#                print("---------", indi_id, individual_list)
#                print("Error in US22: Individual id {i} already exists".format(i=indi_id))
#                check_results[indi_id] = "Error"
#            else:
#                individual_list.append(indi_id)
#                #print("indlist", individual_list)
#                check_results[indi_id] = "Yes"
#        for fam_key in families:
#            family = families[fam_key]
#            fam_id = family.get_id()
#            if fam_id in family_list:
#                print("Error in US22: Family id {f} already exists".format(f=fam_id))
#                check_results[fam_id] = "Error"
#            else:
#                family_list.append(fam_id)
#                check_results[fam_id] = "Yes"
#        
#        print(check_results)
#        return check_results
#    
#    #US23 Same name and birth date
#    def check_same_name_dob(self):
#        individuals = self.get_individuals()
#        check_results = {}
#        for individual in individuals:
#             individual = individuals[individual]
#             indi_id = individual.get_id()
#             for compare_indiv in individuals:
#                compare_indiv = individuals[compare_indiv]
#                cmp_indi_id = individual.get_id()
#                if individual.get_name == compare_indiv.get_name:
#                    print("first if", individual.get_name, compare_indiv.get_name)
#                # same name, compare birthdate
#                    if compare_indiv.get_birth == individual.get_birth:
#                        print("Error in  US23")
#                        check_results[cmp_indi_id] = "Error"
#                    else:
#                        check_results[cmp_indi_id] = "Yes"
#                else:
#                    check_results[cmp_indi_id] = "Yes"
##        for indi_key in individuals: 
##            individual1 = individuals[indi_key]
##            indi_id = individual1.get_id()
##            birth_date1 = individual1.get_birth()
##            indi_name1 = individual1.get_name()
##            for ind_id in individuals:    
##                individual = individuals[indi_key]
##                indiv_id = individual.get_id()
##                birth_date = individual.get_birth()
##                indi_name = individual.get_name()
##                print("second for loop", birth_date, indi_name, birth_date1, indi_name1)
##                if(birth_date == birth_date1 and indi_name1 == indi_name and indiv_id != indi_id):
##                    print("Error in US23: Individual with {i} doesn't have unique birthdate".format(i=indiv_id))
##                    check_results[indiv_id] = "Error"
##                else:
##                    check_results[indiv_id] = "Yes"
#        print(check_results)
#        return check_results
#    
    
        
# Families
class Family:
    def __init__(self):
        self.__id = None
        self.__husband_id = None
        self.__husband_name = None
        self.__wife_id = None
        self.__wife_name = None
        self.__children = {}
        self.__married = None
        self.__divorced = None

    def read_in(self, fam_dict):
        if 'id' in fam_dict:
            self.__id = fam_dict['id']
        if 'Married' in fam_dict:
            self.__married = fam_dict['Married']
        if 'Divorced' in fam_dict:
            self.__divorced = fam_dict['Divorced']
        if 'Husband_ID' in fam_dict:
            self.__husband_id = fam_dict['Husband_ID']
        if 'Wife_ID' in fam_dict:
            self.__wife_id = fam_dict['Wife_ID']
        if 'Children' in fam_dict:
            self.__children = fam_dict['Children']

    def get_family(self):
        return [self.__id, self.__married,
                self.__divorced, self.__husband_id,
                self.__husband_name, self.__wife_id,
                self.__wife_name, set([key for key in self.__children])]

    def get_id(self):
        return self.__id

    def get_husband_id(self):
        return self.__husband_id

    def set_husband_name(self, name):
        self.__husband_name = name

    def get_wife_id(self):
        return self.__wife_id

    def set_wife_name(self, name):
        self.__wife_name = name

    def list_children_ids(self):
        return set([key for key in self.__children])

    def set_child_by_id(self, child_key, child):
        self.__children[child_key] = child

    def get_child_by_id(self, id_):
        return self.__children[id_]

    def get_children(self):
        return self.__children

    def get_marriage_date(self):
        return self.__married

    def get_divorce_date(self):
        return self.__divorced


# Individual
class Individual:
    def __init__(self):
        self.__id = None
        self.__name = None
        self.__gender = None
        self.__birth = None
        self.__death = None
        self.__age = None
        self.__alive = None
        self.__parents_families = {}  # families where the indi is a child
        self.__own_families = {}  # families where the indi is a spouse

    def read_in(self, indi_dict):
        if 'id' in indi_dict:
            self.__id = indi_dict['id']
        if 'Name' in indi_dict:
            self.__name = indi_dict['Name']
        if 'Gender' in indi_dict:
            self.__gender = indi_dict['Gender']
        if 'Birthday' in indi_dict:
            self.__birth = indi_dict['Birthday']
        if 'Age' in indi_dict:
            self.__age = indi_dict['Age']
        if 'Alive' in indi_dict:
            self.__alive = indi_dict['Alive']
        if 'Death' in indi_dict:
            self.__death = indi_dict['Death']
        if 'Child' in indi_dict:
            self.__parents_families = indi_dict['Child']
        if 'Spouse' in indi_dict:
            self.__own_families = indi_dict['Spouse']

    def get_individual(self):
        # list all information of the indi
        return [self.__id, self.__name, self.__gender,
                self.__birth, self.__age, self.__alive, self.__death,
                set([key for key in self.__own_families]),
                set([key for key in self.__parents_families])
                ]

    def get_name(self):
        return self.__name

    def get_id(self):
        return self.__id

    def get_gender(self):
        return self.__gender

    def get_birth(self):
        return self.__birth

    def get_death(self):
        return self.__death

    def list_parents_families_ids(self):
        return set([key for key in self.__parents_families])

    def list_own_families_ids(self):
        return set([key for key in self.__own_families])

    def get_parent_family_by_id(self, id_):
        return self.__parents_families[id_]

    def get_parent_families(self):
        return self.__parents_families

    def get_own_family_by_id(self, id_):
        return self.__own_families[id_]

    def get_own_families(self):
        return self.__own_families

    def set_parent_family_by_id(self, fam_id, fam):
        self.__parents_families[fam_id] = fam

    def set_own_family_by_id(self, fam_id, fam):
        self.__own_families[fam_id] = fam

    def find_all_descendants(self):
        results = []
        #dfs to fetch all descendant ids
        def helper(individual, results):
            if len(list(individual.get_own_families().values())) == 0:
                return
            for family in list(individual.get_own_families().values()):
                children = family.get_children()
                results += list(children.keys())
                for child in list(children.values()):
                    helper(child, results)

        helper(self, results)
        return results

    def find_spouse_ids(self):
        own_families = list(self.get_own_families().values())
        if self.get_gender() == "M":
            results = [fam.get_wife_id() for fam in own_families]
        else:
            results = [fam.get_husband_id() for fam in own_families]
        return results