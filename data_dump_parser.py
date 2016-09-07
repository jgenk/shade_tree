import csv
import med_parser
import sys

MED_LIST_TAG = "PrListMed"
PTNAME_TAG = "PtName"

class Patient:
    
    def __init__(self,mrn,attributes):
        
        self.mrn = mrn
        self.attributeList = attributes
        self.medList = []
        if self.attributeList.has_key(MED_LIST_TAG):
            for med in self.attributeList[MED_LIST_TAG] : 
                self.medList.append(med_parser.parseMedication(med)) 
            self.attributeList.pop(MED_LIST_TAG)
         
    def add_attribute (self, attr_name, attr_value):
        self.attributeList[attr_name] = attr_value
    
    def get_attribute(self, attr_name):
        return self.attributeList[attr_name]
    
    def getMedList(self):
        return self.medList
    
    def __str__(self):
        output = "MRN: " + self.mrn + "\n"
        
        for key in self.attributeList.keys():
            output = output + key + ": " + ''.join(self.attributeList[key]) +"\n"
        output = output + "Med List:\n"
        for med in self.medList :
            output = output + str(med) + "\n"
        return output

        
def getData(filename):
    
    return data

def buildPatientList(filename):
    # Retrieves all data from the CSV and returns a reader object
    data = []
    with open(filename, 'rb') as file :
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    
    # Make list of patient objects
    patient_list = []
    current_pt = data[0][0]
    pt_data = []
    for row in data:
        if current_pt != row[0]:
            patient_list.append(createPatient(current_pt, pt_data))
            pt_data = []
            current_pt = row[0]
        pt_data.append(row)
    if len(pt_data) > 0 : patient_list.append(createPatient(current_pt, pt_data))
    return patient_list
    
def createPatient(mrn, data):
    pt_dict = buildPatientDict(data)
    
    patient = Patient(mrn,pt_dict)
    
    
    return patient
    
def buildPatientDict(data):
    pt_dict = {}
    
    for entry in data:
        key = entry[3]
        if not pt_dict.has_key(key): pt_dict[key] = []
        pt_dict[key].append(entry[4])
    return pt_dict
    

