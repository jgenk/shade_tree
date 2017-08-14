import pandas as pd
from collections import OrderedDict
import psycopg2 as p2
import rxnorm
import charge_parser as cp
import numpy as np
from sys import stdout


DB_NAME = 'shadetree'
USER = 'postgres'
PASSWORD = '123'
CHARGES_SCHEMA = 'charges'
RX_NORM_TABLE = CHARGES_SCHEMA + '.rxnorm_data'
CHARGES_TABLE = CHARGES_SCHEMA + '.all_charges'
UNIT_CNT_COL = 'unit_cnt'
RXCUI_COL = 'rxcui'
NDC_COL = 'ndc'
UPC_COL = 'upc'
ITEM_DESC_COL = 'item_desc'
CONFIG_DELIM = ';'
DEFINITION_DELIM = '|'
IGNORE_CHAR = '#'

class DatabaseBuilder(object):

    def __init__(self, config_file):
        self.config_file = config_file

    def reset_db(self):
        set_charge_config(self.config_file)
        create_rxnorm_table(self.config_file)

    def add_charge_sheet_to_db(self, filename):
        df = pd.read_excel(filename)
        df = df.dropna(how='all')

        conn = p2.connect("dbname=" + DB_NAME + " user=" + USER + " password=" + PASSWORD)
        cur = conn.cursor()

        count = len(df.index)

        for index,row in df.iterrows():
            self.add_xls_line_to_table(cur, row, CHARGES_TABLE)
            percent = int((index+1)*100.0/count)
            stdout.write('\r{filename}: {perc}%'.format(filename=filename,perc=percent))

        stdout.write('\r{filename}: DONE'.format(filename=filename,perc=percent))

        conn.commit()
        cur.close()
        conn.close()
        return

    def add_xls_line_to_table(self, cur, line, table_name):
        col2xls = get_col_map(self.config_file, table_name)
        value_map = OrderedDict()

        #get all values and put them into value map
        for col,xls_syn_list in col2xls.iteritems():
            value = np.nan
            for xls_syn in xls_syn_list:
                value = line.get(xls_syn, np.nan)
                if not pd.isnull(value):
                    if isinstance(value, basestring): value = value.strip()
                    break
            value_map[col]=value

        item_desc = value_map.get(ITEM_DESC_COL, np.nan)

        if pd.isnull(item_desc): return False
        #get rxcui and formatted ndc:
        NDC_raw = value_map.get(NDC_COL, np.nan)
        ndc,rxcui = None,None
        if not pd.isnull(NDC_raw):
            NDC_str = str(NDC_raw).strip()
            if len(NDC_str) > 0: ndc,rxcui = fmt_NDC_and_get_rxcui(cur, NDC_raw)

        #if rxcui came back as none based on NDC, lets see if we can get an rxcui from string
        if rxcui is None and not is_exception(item_desc) :
            rxcui = get_rxcui_id_for_desc(cur, item_desc)

            if rxcui is None: pass
            elif not get_user_approval(rxcui, item_desc):
                rxcui = get_user_rec_rxcui()
                if rxcui == '': rxcui = None

        #set values that are not found in spreadsheet
        for col,value in value_map.iteritems():
            if col == NDC_COL:
                value_map[col]= ndc
            elif col == RXCUI_COL:
                value_map[col]= rxcui
            elif col == UNIT_CNT_COL:
                value_map[col] = cp.get_num_pills(item_desc)


        #add row to postgres table
        insert = generate_insert_command(table_name, len(value_map.keys()))
        cur.execute(insert, tuple(value_map.values()))

        #as long as all goes well, lets update rxnorm table
        self.add_to_rxnorm(cur,rxcui,ndc)
        return

    def add_to_rxnorm(self,cur,rxcui,ndc):
        if rxcui is None: return False
        #(rxcui, ndc[])
        rxcui_info = get_rxnorm_row(cur,rxcui,','.join([RXCUI_COL,NDC_COL]))
        if rxcui_info is None:
            rxcui_info = self.init_row_in_rxnorm(cur, rxcui)
        return add_ndc_to_rxcui(cur,rxcui_info[0],rxcui_info[1],ndc)

    def init_row_in_rxnorm(self, cur, rxcui):
        #get all rxnorm data first
        data = self.get_data_for_rxnorm_row(rxcui)

        column_names = get_column_names(self.config_file,RX_NORM_TABLE)
        insert = generate_insert_command(RX_NORM_TABLE,len(column_names))

        cur.execute(insert, tuple(data))
        return (rxcui,[])

    def get_data_for_rxnorm_row(self, rxcui):
        function_map = get_col_map(self.config_file,RX_NORM_TABLE)
        return get_rxnorm_data(rxcui, function_map)


def add_ndc_to_rxcui(cur,rxcui,ndc_list,ndc):
    if (not ndc is None) and (not ndc in ndc_list): ndc_list.append(ndc)
    else : return False
    return set_ndc_for_rxcui(cur,rxcui,ndc_list)

def set_ndc_for_rxcui(cur,rxcui,ndc_list):
    ndc_string = '{\"' + '\",\"'.join(ndc_list) + '\"}'
    cur.execute("UPDATE {0} SET {1} = \'{2}\' WHERE rxcui={3}".format(RX_NORM_TABLE,
                                                                      NDC_COL,
                                                                      ndc_string,
                                                                      rxcui))
    return True


def get_rxnorm_data(rxcui,function_map):
    data_list = []
    for col,func in function_map.iteritems():
        if col.startswith(RXCUI_COL):
            data = rxcui
        elif col.startswith(NDC_COL):
            data = []
        else:
            func = getattr(rxnorm, func[0])
            data = func(rxcui)
        data_list.append(data) #add empty list for ndc
    return data_list

def get_rxnorm_row(cur,rxcui,columns='*'):
    cur.execute('SELECT {cols} FROM {table} WHERE rxcui={value}'.format(cols=columns, table=RX_NORM_TABLE, value=rxcui))
    return cur.fetchone()

def get_user_rec_rxcui():
    rxcui = raw_input("Input desired RXCUI: ")
    if len(rxcui) == 0 : return None
    return int(rxcui)

def get_user_approval(rxcui, item_desc):
    rxnorm_name = rxnorm.get_name_for_rxcui_id(rxcui)
    print "\nInput Description: ", item_desc
    print "RXCUI Description #",rxcui,": ", rxnorm_name
    approval = raw_input("Do you approve of this RXCUI assignment (Y/N)? ")
    return approval.upper().startswith('Y')

def is_exception(item_desc):
    if item_desc.find('CENTOR') > -1: return True
    return False


"""
The function accepts 10 digit NDC forms of 4-4-2 (example: 0781-1506-10),
5-3-2 (example: 60429-324-77) and 5-4-1 (example: 11523-7020-1) and the
CMS 11-digit NDC derivative (example: 16571043111). It does not accept partial
forms or NDC notation containing asterisks.
"""
def fmt_NDC_and_get_rxcui(cur, NDC_raw):
    NDC_raw = str(int(NDC_raw))
    NDC_length = len(NDC_raw)
    goal_length = 11
    NDC = None
    rxcui = None

    #Case 1: NDC is 11 digits
    if len(NDC_raw) == 11:
        rxcui = get_rxcui_for_NDC(cur, NDC_raw)
        if rxcui is None: #if 11 digit doesnt work, try 10 digit
            NDC_raw=NDC_raw[1:]
        else:
            NDC = NDC_raw
    if len(NDC_raw) == 10:
        NDC_test442 = '0' + NDC_raw
        NDC_test532 = NDC_raw[:5] +'0'+ NDC_raw[5:]
        NDC_test541 = NDC_raw[:9] + '0' + NDC_raw[9:10]
        for test_NDC in [NDC_test442,NDC_test532, NDC_test541]:
            rxcui = get_rxcui_for_NDC(cur, test_NDC)
            if not rxcui is None:
                NDC = test_NDC
                break

    if len(NDC_raw) < 10:
        NDC ='0'*(11-len(NDC_raw)) + NDC_raw
        rxcui = get_rxcui_for_NDC(cur, NDC)

    return NDC,rxcui

def get_rxcui_for_NDC(cur, NDC):
    rxcui = get_rxcui_from_DB(cur,NDC)
    if rxcui is None: rxcui = rxnorm.get_rxcui_for_NDC(NDC)
    return rxcui

def get_rxcui_id_for_desc(cur, item_desc):
    cur.execute('SELECT rxcui FROM {table} WHERE item_desc={value}'.format(table=CHARGES_TABLE, value="'"+item_desc+"'"))
    selected = cur.fetchone()
    if not selected is None:
        return selected[0]
    return rxnorm.get_rxcui_id_for_string(item_desc)

"""
SELECT rxcui from charges.all_charges where ndc='NDC'
"""
def get_rxcui_from_DB(cur, NDC):
    cur.execute('SELECT rxcui FROM {table} WHERE ndc={value}'.format(table=CHARGES_TABLE, value="'"+NDC+"'"))
    selected = cur.fetchone()
    if not selected is None:
        return selected[0]
    return None


def generate_insert_command(table_name, col_cnt):
    return 'INSERT INTO {table} VALUES ({cols})'.format(table=table_name, cols=','.join(['%s']*col_cnt))




"""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
CONFIGURATION AND TABLE INITIALIZATION
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"""


def set_charge_config(config_file):
    init_table(DB_NAME, CHARGES_TABLE, get_column_names(config_file, CHARGES_TABLE))
    return True

def get_column_names(config_file,table_name):
    columns = []
    for line in get_configlines_for_table(config_file,table_name):
        col = line.split('=')[0]
        parts = col.split(DEFINITION_DELIM)
        if len(parts) > 1:
            columns.append(' '.join(parts))
        else :
            columns.append(col + ' text')
    return columns

def get_configlines_for_table(config_file, table_name):
    f = open(config_file)
    while f.readline().strip().lower() != table_name.lower(): continue
    lines = []
    line = f.readline().strip()
    while line != table_name:
        if not line.startswith(IGNORE_CHAR):
            lines.append(line)
        line = f.readline().strip()

    return lines

def get_col_map(config_file, table_name):
    col_map = OrderedDict()
    for line in get_configlines_for_table(config_file,table_name):
        column = line.split('=')[0].split(DEFINITION_DELIM)[0]
        args = line.split('=')[1].split(CONFIG_DELIM)
        col_map[column] = args
    return col_map

def create_rxnorm_table(config_file):
    init_table(DB_NAME, RX_NORM_TABLE, get_column_names(config_file,RX_NORM_TABLE))
    return

"""
@@@@@@@@@@@@@@
POSTGRES UTILS
@@@@@@@@@@@@@@
"""

def init_table(db,table_name, columns, user='postgres',pwd='123'):
    conn = p2.connect("dbname=" + db + " user=" + user + " password=" + pwd)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS " + table_name + ";")
    cur.execute('CREATE TABLE {name} ({fields});'.format(name=table_name, fields=','.join(columns)))

    conn.commit()
    cur.close()
    conn.close()
