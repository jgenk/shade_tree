import med_parser
import data_dump_parser
import sys
from datetime import datetime, date, time

def allPtWithIneligibleMeds(patients):
# given a list of patients, returns a dictionary where:
#		k = list of patient objects with at least one PAP ineligible med
#		v = the list of PAP ineligible medication objects from the patient key

    ineligibles = {}
    for patient in patients :
        ineligibleMeds = getPAPIneligibleMeds(patient)
        if len(ineligibleMeds) > 0 : ineligibles[patient] = ineligibleMeds
    return ineligibles
        

def getPAPIneligibleMeds(patient):
# creates a list of PAP ineligible medications from the medications associated with this patient object
    ineligibleMeds = []
    for med in patient.medList :
        if isPAPineligible(med) : ineligibleMeds.append(med)
    return ineligibleMeds

def getAllPtNeedPAPRenewal(patients,date):
# given a list of patients, returns a dictionary where:
#		k = list of patient objects with at least one PAP medication in need of renewel by DATE
#		v = the list of PAP medication objects in need of renewl by DATE from the patient key

    needsRenewals = {}
    for patient in patients :
        expiringMeds = getPAPRenewalNeededMeds(patient, date)
        if len(expiringMeds) > 0 : needsRenewals[patient] = expiringMeds
    return needsRenewals

def getPAPRenewalNeededMeds(patient, date):
# creates a list of PAP medications in needed of renewel by DATE from the medications associated with this patient object
   needRenwelMeds = []
    for med in patient.medList :
        if not isPAPapproved(med) : continue
        if needsPAPRenewal(med,date) : needRenwelMeds.append(med)
    return needRenwelMeds

def needsPAPRenewal(med, date):
    #assumes med is PAP approved
    return med.PAPexpirationDate < date
    
def isPAPapproved(medication):
    return medication.PAPstatus == med_parser.PAP_APPROVED

def isPAPineligible(medication):
    return medication.PAPstatus == med_parser.PAP_INELIGIBLE

def getNameOfPatient (patient) :
    return patient.get_attribute(data_dump_parser.PTNAME_TAG)[0]

def csvPtWithIneligiblePAP(filename):
    patient_list = data_dump_parser.buildPatientList(filename)
    patientDict = allPtWithIneligibleMeds(patient_list)
    for (patient, meds) in patientDict.items():
        for med in meds :
            print patient.mrn + "," + getNameOfPatient(patient) + "," + med.name + "," + med.medText


def csvPtNeedingPAPRenewal(expirebydate):
    patient_list = data_dump_parser.buildPatientList(filename)
    patientDict = getAllPtNeedPAPRenewal(patient_list,expirebydate)
    for (patient, meds) in patientDict.items():
        for med in meds :
            print patient.mrn + "," + getNameOfPatient(patient) + "," + med.name + "," + str(med.PAPexpirationDate) + ","  + med.medText
 
def getFilename(filename) :
    if len(filename)== 0 : filename = raw_input("Enter filename of csv containing medication data dump: ")
    return filename
        
# if __name__ == '__main__':
    # patient_list = data_dump_parser.buildPatientList(getFilename(sys.argv[1]))
    # for patient in patient_list: 
        # print patient
        
# if __name__ == '__main__':
    # filename = sys.argv[1]
    # if len(filename)== 0 : filename = raw_input("Enter filename of csv containing medication data dump: ")
    # patient_list = data_dump_parser.buildPatientList(filename)
    # csvPtWithIneligiblePAP(patient_list)
    
# if __name__ == '__main__':

    # if len(sys.argv) > 2: date = date = datetime.strptime(sys.argv[2], '%m/%y')
    # else : date = datetime.now()
    # date format must be MM/YY
    # csvPtNeedingPAPRenewal(patient_list, date)

