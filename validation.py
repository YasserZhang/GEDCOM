import re
import argparse
VADLID_TAGS = set(['INDI', 'NAME', 'SEX', 'BIRT', 'DEAT', 'FAMC', 'FAMS', 'FAM', 'MARR', 'HUSB', 'WIFE', 'CHIL', 'DIV', 'DATE', 'HEAD', 'TRLR', 'NOTE'])
EXCEPTIONAL_TAGS = set(['FAM', 'INDI'])
def print_line(line):
    items = re.split('[ ]', line.strip(), 2)
    items_to_print = ['<--', items[0]]
    last_item = items[2].strip()
    if items[1] not in VADLID_TAGS:
        if items[2].strip() in EXCEPTIONAL_TAGS:
            items_to_print.append(items[2].strip())
            items_to_print.append('Y')
            last_item = items[1]
        else:
            items_to_print.append(items[1])
            items_to_print.append('N')
    else:
        items_to_print.append(items[1])
        items_to_print.append('Y')
    items_to_print.append(last_item)
    print(' '.join(items_to_print))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add GEDCOM file')
    parser.add_argument('-f', action="store", dest='filename', required=True)
    args = parser.parse_args()
    filename = args.filename
    with open(filename, 'r') as f:
        for line in f.readlines():
            print('-->', line)
            print(line)


