# design classes
# global names
from datetime import date
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
                    print("Warning: This line may contain incorrect format or be skipped.")
                    print(lines[i])
                    i += 1
        self.__connect()
        self.__update_derivative_attributes()
        self.list_individuals()
        self.list_families()

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
            indi_row['Alive'] = 'True'
        else:
            indi_row['Age'] = date.today().year - indi_row['Birthday'].year
            indi_row['Alive'] = 'False'
            indi_row['Death'] = 'NA'
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

    def list_families(self):
        for key in self.__family_dict:
            fam = self.__family_dict[key]
            print(fam.get_family())

    def list_individuals(self):
        for key in self.__individual_dict:
            indi = self.__individual_dict[key]
            print(indi.get_individual())


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

    def get_child_by_id(self):
        pass

    def get_marriage_date(self):
        pass

    def get_divorce_date(self):
        pass


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
                self.__birth, self.__age, self.__alive,
                set([key for key in self.__parents_families]),
                set([key for key in self.__own_families])]

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
        pass

    def get_own_family_by_id(self, id_):
        pass

    def set_parent_family_by_id(self, fam_id, fam):
        self.__parents_families[fam_id] = fam

    def set_own_family_by_id(self, fam_id, fam):
        self.__own_families[fam_id] = fam
