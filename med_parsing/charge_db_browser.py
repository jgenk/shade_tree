from psql_utils import DBHelper
from collections import OrderedDict
DB_NAME = 'shadetree'
USER = 'postgres'
PASSWORD = '123'

class ChargeColumns(object):
    ITEM_DESC='Item Description'
    NDC='NDC'
    DATE='Order Date'
    UNIT_CNT='Items per Package'
    QTY='Number of Packages'
    TOT_ITEMS='Total Items in Order'
    UNIT_PRICE='Price per Unit'
    PKG_PRICE='Price per Package'
    TOT_COST= 'Total Order Cost'
    AVG_PILL_CHG= 'Pills per Clinic (by charge)'
    AVG_PILL_ALL= 'Pills per Clinic (all charges)'



class ChargeDBHelper(DBHelper):
    def __init__(self):
        DBHelper.__init__(self,'shadetree','postgres','123','charges')

    def get_all_charge_bundles(self):
        charge_bundles = []

        for rxcui,ingredient,strength,may_treat,ndc in self.all_rxnorm_rows():
            bundle = ChargeBundle(rxcui,ingredient,strength,may_treat)
            for item_desc,ndc,date,unit_cnt,qty,pkg_price,total_price in self.charges_for_rxcui(bundle.rxcui):
                bundle.add_charge(item_desc,ndc,date,unit_cnt,qty,pkg_price,total_price)
            charge_bundles.append(bundle)

        return charge_bundles

    def get_days_spanned(self):
        columns ='max(cred_dt)-min(cred_dt)'
        db= 'all_charges'
        return self.simple_select(columns,db)[0][0]

    def all_rxnorm_rows(self):
        return self.simple_select('*','rxnorm_data')


    def charges_for_rxcui(self,rxcui):
        columns = ['item_desc','ndc','cred_dt','unit_cnt','qty_net','invoice_pkg','invoice_ext_price']
        table = 'all_charges'
        where = 'rxcui=' + str(rxcui)
        return self.simple_select(columns,table,where)

class ChargeBundle(object):

    def __init__(self,rxcui,ingredient,strength,may_treat):
        self.rxcui = rxcui
        self.ingredient = ingredient
        self.strength = strength
        self.may_treat = may_treat
        self.charges = []

    def add_charge(self,item_desc,ndc,date,unit_cnt,qty,pkg_price,total_price):
        new_charge = OrderedDict([(ChargeColumns.ITEM_DESC, item_desc),
                                 (ChargeColumns.NDC,ndc),
                                 (ChargeColumns.DATE,date),
                                 (ChargeColumns.UNIT_CNT,unit_cnt),
                                 (ChargeColumns.QTY,qty),
                                 (ChargeColumns.TOT_ITEMS,qty*unit_cnt),
                                 (ChargeColumns.UNIT_PRICE, '${0}'.format(round(float(pkg_price[1:])/float(unit_cnt),3))),
                                 (ChargeColumns.PKG_PRICE,pkg_price),
                                 (ChargeColumns.TOT_COST,total_price)])
        self.charges.append(new_charge)

        self.charges.sort(key=lambda charge: charge[ChargeColumns.DATE])
        return new_charge

    def calculate_order_limit_avg(self,clinic_count):
        # Order limit by average = sum (units per pkg*#pkg)/clinic count

        total_items = sum([charge[ChargeColumns.UNIT_CNT]*charge[ChargeColumns.QTY] for charge in self.charges])
        return int(total_items/clinic_count)

    def calculate_order_limit_max(self):
        item_per_clinic = get_item_per_clinic_list(self,Trum)

        if len(item_per_clinic) == 0: return -1

        return int(max(item_per_clinic))

    def get_item_per_clinic_list(self,sum_same_day=False):
        item_per_clinic = []
        same_date_list = []
        extra_count=0
        for i in range(0,len(self.charges)-1):
            charge1=self.charges[i]
            charge2=self.charges[i+1]
            same_date_list.append(charge1)
            if is_same_date(charge1,charge2): continue
            if sum_same_day:
                extra_count = 0
                for i in range(0,len(same_date_list)-1):
                    extra_count += get_avg_item_used(same_date_list[i],charge2)
                item_per_clinic.append(get_avg_item_used(charge1,charge2,extra_count))
            else:
                for cur_charge in same_date_list: item_per_clinic.append(get_avg_item_used(cur_charge,charge2))
            same_date_list = []

        if len(self.charges) != 0:
            item_per_clinic.append(-1)
            if not sum_same_day: item_per_clinic.extend([-1]*(len(same_date_list)))
        return item_per_clinic

    def get_first_order_date(self):
        return self.charges[0][ChargeColumns.DATE]

    def get_last_order_date(self):
        return self.charges[-1][ChargeColumns.DATE]

    def charge_cnt(self):
        return len(self.charges)

    def largest_order_info(self):

        max_charge = max(self.charges, key=lambda charge: charge[ChargeColumns.UNIT_CNT])

        max_order_size=max_charge[ChargeColumns.QTY]*max_charge[ChargeColumns.UNIT_CNT]
        max_order_dates=[charge[ChargeColumns.DATE] for charge in self.charges if charge[ChargeColumns.QTY]*charge[ChargeColumns.UNIT_CNT] == max_order_size]

        return max_order_size,max_order_dates,

    def cheapest_NDC(self):
        min_charge = min(self.charges, key=lambda charge: float(charge[ChargeColumns.PKG_PRICE][1:])/charge[ChargeColumns.UNIT_CNT])
        return min_charge[ChargeColumns.NDC]

    def __str__(self):
        return '{cb.rxcui}, {cb.ingredient} {cb.strength}\nTreats:{cb.may_treat}\n{charges}'.format(cb=self,
                                                                                                    charges='\n'.join(map(str,self.charges)))



def get_all_charges_output():
    """
    Returns a list of OrderedDict where keys = column names, values = row values
    """
    chargeDB = ChargeDBHelper()
    charge_list = []

    rxcui_bundles = chargeDB.get_all_charge_bundles()
    clinic_count = clinic_cnt_for_days(chargeDB.get_days_spanned())

    for bundle in rxcui_bundles:
        bundle_info = to_order_limit_row(bundle, clinic_count, False)
        bundle_size = len(bundle.charges)
        item_per_clinic = bundle.get_item_per_clinic_list()


        for i in range(bundle_size-1,-1,-1):
            charge_row_dict = OrderedDict()
            charge = bundle.charges[i]
            #add charge bundle info every charge
            for k,v in bundle_info.iteritems(): charge_row_dict[k]=v
            charge_row_dict[ChargeColumns.AVG_PILL_CHG]=item_per_clinic[i]
            #add charge-specific info for every charge
            for k,v in charge.iteritems(): charge_row_dict[k]=v
            charge_list.append(charge_row_dict)


    chargeDB.close()
    return charge_list

def get_order_limit_data():
    """
    Returns a list of OrderedDict where keys = column names, values = row values
    """

    chargeDB = ChargeDBHelper()
    order_limit_list = []

    rxcui_bundles = chargeDB.get_all_charge_bundles()
    clinic_count = clinic_cnt_for_days(chargeDB.get_days_spanned())
    for bundle in rxcui_bundles:
        order_limit_list.append(to_order_limit_row(bundle, clinic_count))



    chargeDB.close()
    return order_limit_list

def to_order_limit_row(bundle, clinic_count,summary=True):
    row = OrderedDict()
    row['RXCUI']=bundle.rxcui
    row['Ingredient']=bundle.ingredient
    row['Strength']=bundle.strength
    row['Treats']=bundle.may_treat
    if summary:
        row['First Ordered']=bundle.get_first_order_date()
        row['Last Ordered']=bundle.get_last_order_date()
        row['Order Count']=bundle.charge_cnt()
        row['Largest Order Size (pkg)'],row['Largest Order Date(s)']=bundle.largest_order_info()
        row['Order Limit (max)']=bundle.calculate_order_limit_max()
    row['Order Limit (avg)']=bundle.calculate_order_limit_avg(clinic_count)
    if summary:
        row['Cheapest NDC']=bundle.cheapest_NDC()
    return row

def clinic_cnt_for_days(days):
    return (days/7.0)*2

def get_avg_item_used(charge1, charge2,extra_count=0):
    clinics_lasted_for = clinic_cnt_for_days((charge2[ChargeColumns.DATE]-charge1[ChargeColumns.DATE]).days)
    total_count = charge1[ChargeColumns.UNIT_CNT]*charge1[ChargeColumns.QTY] + extra_count
    return total_count/clinics_lasted_for

def is_same_date(charge1, charge2):
    return (charge2[ChargeColumns.DATE]-charge1[ChargeColumns.DATE]).days == 0
