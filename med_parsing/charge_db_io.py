import sys
import charge_db_builder as builder
import charge_db_browser as browser
import csv

from os import listdir
from os.path import isfile, join

MENU_OPTIONS = [('Reset Config File','set_config_file'),
                ('Add Charge Speadsheet', 'add_charge_sheet'),
                ('Add Charge sheets in directory', 'add_all_charge_sheets'),
                ('Make Order Limit CSV', 'make_order_limit_csv'),
                ('All Charges Ouput CSV', 'make_all_charges_output_csv')]

class ChargeDBIO(object):

    def __init__(self, config_file=None):
        self.set_config_file(config_file)

    def set_config_file(self,config_file=None):
        if config_file is None :
            config_file = raw_input("Enter new config file: ")
        if len(config_file) == 0: return

        self.db_builder = builder.DatabaseBuilder(config_file)

        print "Config file set to: ", config_file

        should_clear = raw_input("Do you want to clear the charge DB (Y/N)? ")
        if checkYN(should_clear):
            self.db_builder.reset_db()

    def add_charge_sheet(self,filename=''):
        if len(filename) == 0:
            filename=raw_input("Enter path to spreadsheet you want to add: ")
        print '\n'
        self.db_builder.add_charge_sheet_to_db(filename)
        return

    def add_all_charge_sheets(self,directory=''):
        if len(directory) == 0:
            directory=raw_input("Enter path to directory you want to add: ")
        for f in listdir(directory):
            filepath = join(directory, f)
            if not isfile(filepath): continue
            self.add_charge_sheet(filepath)
        return

    def make_order_limit_csv(self,filename=''):
        if len(filename) == 0:
            filename=raw_input("Enter destination filename: ")

        write_csv(browser.get_order_limit_data(),filename)
        return


    def make_all_charges_output_csv(self,filename=''):
        if len(filename) == 0:
            filename=raw_input("Enter destination filename: ")
        write_csv(browser.get_all_charges_output(),filename)
        return

def write_csv(data,filename):
    headers = data[0].keys()

    row_count = len(data)

    with open(filename, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in data:
            newline = {key : row[key] for key in headers}
            writer.writerow(newline)
    return



def checkYN(user_input):
    return user_input.upper().startswith('Y')


def domenu(db_io):


    print '\n',menu_text()
    choice=get_menu_choice()

    if choice == len(MENU_OPTIONS): return False

    func = getattr(db_io,MENU_OPTIONS[choice][1])
    func()
    return True

def menu_text():
    output = ''
    for i in range(0,len(MENU_OPTIONS)):
        output += '{num}. {text}\n'.format(num=i,text=MENU_OPTIONS[i][0])
    output += str(len(MENU_OPTIONS)) + '. Exit\n'
    return output

def get_menu_choice():
    user_choice = raw_input("ENTER #: ")[:1]
    if len(user_choice) == 0: return len(MENU_OPTIONS)
    return int(user_choice)


def main(args):
    config_file=None
    if len(args) > 1:
        config_file=args[1]

    db_io = ChargeDBIO(config_file)

    while domenu(db_io): continue
    return


if __name__ == "__main__":
    main(sys.argv)


"""
PSQL QUERIES

SET search_path TO charges;

--Get order limit data--
SELECT all_charges.rxcui, all_charges.item_desc, rxnorm_data.ingredient, rxnorm_data.strength,all_charges.ndc, all_charges.unit_cnt, all_charges.invoice_pkg, all_charges.cred_dt
    FROM all_charges INNER JOIN rxnorm_data ON (allcharges.rxcui = rxnorm.data.rxcui)
    ORDER BY rxnorm.ingredient, all_charges.rxcui, all_charges.cred_dt;

--Get total clinics occuring in data--
SELECT min(cred_dt), max(cred_dt), (max(cred_dt)-min(cred_dt))*2/7 as total_clinics
    FROM all_charges
    LIMIT 10;

--Get total #pills,tubes, etc. ordered for each RXCUI, inner join with RXCUI info


SELECT rxnorm_data.rxcui, rxnorm_data.ingredient, rxnorm_data.strength, counts.rxcui_cnt as num_charges, counts.total_ordered, counts.total_ordered/86 as order_limit, rxnorm_data.ndc
FROM rxnorm_data
INNER JOIN (
    SELECT rxcui,count(*) as rxcui_cnt,sum(qty_net*unit_cnt) as total_ordered
        FROM all_charges
        GROUP BY rxcui
    ) AS counts
ON (rxnorm_data.rxcui = counts.rxcui)
ORDER BY rxnorm_data.ingredient DESC, rxnorm_data.rxcui ASC



\copy (SELECT rxnorm_data.rxcui, rxnorm_data.ingredient, rxnorm_data.strength, counts.rxcui_cnt as num_charges, counts.total_ordered, counts.total_ordered/86 as order_limit, rxnorm_data.ndc FROM rxnorm_data INNER JOIN ( SELECT rxcui,count(*) as rxcui_cnt,sum(qty_net*unit_cnt) as total_ordered FROM all_charges GROUP BY rxcui) AS counts ON (rxnorm_data.rxcui = counts.rxcui) ORDER BY rxnorm_data.ingredient DESC, rxnorm_data.rxcui ASC) TO '~/ShadeTree/order_limits.csv' CSV HEADER;

psql  -c "SET search_path TO charges; COPY (SELECT charges.rxnorm_data.rxcui, rxnorm_data.ingredient, rxnorm_data.strength, counts.rxcui_cnt as num_charges, counts.total_ordered, counts.total_ordered/86 as order_limit, rxnorm_data.ndc FROM rxnorm_data INNER JOIN ( SELECT rxcui,count(*) as rxcui_cnt,sum(qty_net*unit_cnt) as total_ordered FROM all_charges GROUP BY rxcui) AS counts ON (rxnorm_data.rxcui = counts.rxcui) ORDER BY rxnorm_data.ingredient DESC, rxnorm_data.rxcui ASC) TO STDOUT WITH CSV HEADER " shadetree > ~/Desktop/order_limits.csv

--get


"""
