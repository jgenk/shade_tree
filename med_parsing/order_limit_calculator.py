import med_parsing_V2.rxnorm as rxnorm
import charge_parsing.charge_parser as cp
import pandas as pd
import sys
from os import listdir

class MedicationChargeBundle(object):

    def __init__(self, medication):
        self.medication = medication

    def matches_charge(self, chrg):
        return self.ing

class ChargeCollection(object):

    def __init__(self):
        self.charge_dict = {}
        self.rawNDC_to_NDC = {}
        self.NDC_to_rxcui = {}

    def import_charges(self, xls, meds_only=True):
        sheet = pd.read_excel(xls)

        for index,row in sheet.iterrows():
            if index > 10: break
            print row
            #Get NDC, skip if no NDC
            rawNDC = row[cp.ColumnName.NDC]
            if meds_only and rawNDC is None: continue

            # Get properly formatted NDC
            NDC = rawNDC_to_NDC.get(rawNDC, None)
            if NDC is None:
                NDC,rxcui = fmt_NDC_and_get_rxcui(NDC)
            if rxcui is None:
                rxcui = get_rxcui_for_NDC(NDC)

            NDC_to_rxcui[NDC]=rxcui

            print row
            print NDC
            print rxcui



            #Get Item Description => extract package size

            #Get Ordered Qty, net quantity => get lowest > 0 of the two

            #Invoiced Price

            # Information to get from RxNorm:
                # Ingredients
                # strength
                # VA classification(s)


    return


    
# class Medication(object):
#
#     def __init__():


def main(directory):

    charge_coll = ChargeCollection()

    for filename in listdir(directory):
        charge_coll.import_charges(directory + filename)


# class Charge(object):

if __name__ == "__main__":
    main(sys.argv[1])
