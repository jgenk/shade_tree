import re
import datetime 

PAP_APPROVED = "APPROVED"
PAP_UNCERTAIN = "uncertain"
PAP_INELIGIBLE = "ineligible"

class Medication:
    def __init__(self, name, strength, medText=""): 
        self.name = name
        self.strength = strength
        self.medText = medText
        self.dispensedDate = None
        
    def setPAPStatus(self, PAPstatus, PAPexpirationDate) :
        self.PAPstatus = PAPstatus
        if PAPexpirationDate is not None :
            splitDate = PAPexpirationDate.split("/")
            month = int(splitDate[0])
            year = int(splitDate[len(splitDate)-1])
            if len(splitDate)>2 : day = int(splitDate[1])
            else : day = 1
            self.PAPexpirationDate = datetime.datetime(year, month, day)
    
    def setDispensedInfo(self, dispensedDate, dispensedDuration):
        if dispensedDate is not None :
            splitDate = dispensedDate.split("/")
            month = int(splitDate[0])
            year = int(splitDate[len(splitDate)-1])
            if len(splitDate)>2 : day = int(splitDate[1])
            else : day = 1
            self.dispensedDate = datetime.datetime(year, month, day)
        self.dispensedDuration = dispensedDuration
    
    def __str__(self):
        output = self.shortString() + "\n"
        if  self.dispensedDate is not None:
            output = output + "\t" + "Dispensed on " + str(self.dispensedDate)
            if self.dispensedDuration is not None : 
                output = output + " for " + self.dispensedDuration + " days"
            output = output + "\n"
        else : output = output + "\tNot dispensed at Shade Tree.\n"
        output = output + "\t" + "PAP status: " + self.PAPstatus 
        if self.PAPstatus == PAP_APPROVED : 
            output = output + " until " + str(self.PAPexpirationDate)
        return output
    
    def shortString(self):
        return self.name + ", " + self.strength


def parseMedication(medText):
    name = parseMedName(medText)
    strength = parseMedStrength(medText)
    newMed = Medication(name, strength, medText)
    
    setDispensedStatus(newMed, medText)
    setPAPStatus(newMed, medText)

    return newMed

def parseMedName(medText):
    
    medName = medText.split()[0]
    
    return medName


def parseMedStrength(medText) :
    
    split = medText.split()
    if len(split) == 1 : return ""
    medStrength = medText.split()[1]
    
    return medStrength
    

def setDispensedStatus(newMed, medText) :
    
    dispensedText = getDispensedText(medText)
    dispensedDate = parseDispensedDate(medText, dispensedText)
    dispensedDuration = parseDispensedDuration(medText, dispensedText)
        
    newMed.setDispensedInfo(dispensedDate, dispensedDuration)
    
    return newMed
 
def getDispensedText(medText) :
    match = re.search("\([Dd]ispensed.*\)",medText)
    if not match : return ""
    return match.group()
    
def parseDispensedDate(medText, dispensedText=""):
    if len(dispensedText) == 0: dispensedText = getDispensedText(medText)
    match = re.search("[0-9]+/[0-9]+/[0-9]+", dispensedText)
    if not match : return None
    return match.group()
    

def parseDispensedDuration(medText, dispensedText=""):
    if len(dispensedText) == 0: dispensedText = getDispensedText(medText)
    match = re.search("for ([0-9]+) days", getDispensedText(medText))
    if not match : return None
    return match.group(1)
    
def setPAPStatus (newMed, medText):
    
    PAPtext = getPAPtext(medText)
    PAPstatus = getPAPStatus(medText,PAPtext)
    if PAPstatus == PAP_APPROVED :
        PAPexpirationDate = getPAPexpirationDate(medText, PAPtext, PAP_APPROVED)
    else : PAPexpirationDate = None
    
    newMed.setPAPStatus(PAPstatus, PAPexpirationDate)
    
    return newMed

def getPAPtext(medText, PAPtext="") :
    match = re.search("\(.*PAP.*?\)",medText)
    if not match : return ""
    return match.group()

def getPAPStatus(medText, PAPtext="") :
    if len(PAPtext) == 0 : PAPtext= getPAPtext(medText)
    if len(PAPtext) == 0 : return PAP_UNCERTAIN
    
    #PAP ineligible cases
    if re.search(PAP_INELIGIBLE, PAPtext, re.IGNORECASE) : return PAP_INELIGIBLE
    if re.search("not.+eligible",PAPtext, re.IGNORECASE) : return PAP_INELIGIBLE
    if re.search(PAP_APPROVED, PAPtext, re.IGNORECASE) : return PAP_APPROVED
    return PAP_UNCERTAIN

def getPAPexpirationDate(medText, PAPtext="", PAPstatus="") :

    if len(PAPtext) == 0 : PAPtext=getPAPtext(medText)
    if len(PAPtext) == 0 : return None
    
    if PAPstatus=="" : PAPstatus = getPAPStatus(medText)
    if PAPstatus != PAP_APPROVED : return None
    
    match = re.search("[0-9]+/([0-9]+/)?[0-9]+", PAPtext)
    if not match : return None
    return match.group()
    
    
    
