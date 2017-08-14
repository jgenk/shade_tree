""" Written by: Pedro Teixeira  support@ pedro.l.teixeira@vanderbilt.edu
	Additional functionality added by Ryan Adams  ryan.c.adams@vanderbilt.edu
    Last Modified: September 3, 2016 by Saad Rehman
    
This program takes in a .txt file of shade tree patients with their drug
lists for the day and outputs a .csv file with each patient separated onto one
line with the MRN NAME DOB and then all their drugs in each of the subsequent
cells.  Each patient is output on a new line in the .csv file.

"""

#!python2

#These set up the necessary libraries
import csv
import re
import sys
import datetime
import time
import os

# Replace function to get rid of ';' which seem to cause weird problems
def replace_all(text, dic) :
    for i, j in dic.iteritems() :
        text = text.replace(i, j)
    return text

# Dictionary to be used for find and replace
dictionary = {';':','}

# Open up infile and create/open outfile
os.chdir(os.path.dirname(__file__))
infile = open('meds.txt')
outfile = open('meds.csv','wb',buffering=0)

# Read in all raw data into list of strings
rawdatalist = infile.readlines()

# Filter incoming data to get rid of pesky ';' characters
count = 0
for count in range(len(rawdatalist)) :
    rawdatalist[count] = replace_all(rawdatalist[count],dictionary)

# Create csv writer
outputWriter = csv.writer(outfile)

# Write the headers to the .csv file, with default number MAXMEDS of
# medications
MAXMEDS = 11
header = ["MRN"]
header.append("Name")
header.append("DOB")
header.append("Page Number")
for x in range(MAXMEDS):
    header.append("Medication "+str(x+1))
for x in range(MAXMEDS):
    header.append("Medication time "+str(x+1))

outputWriter.writerow(header)

# Go through line by line, deteremine if MRN is present, if so start new row
# and populate with medications
x = 0
while  x < len(rawdatalist):
    tempheaderlist = []
    tempmedlist = []
    temprowlist = []
    pagecount = 1
    temppagelist = []
    if re.search('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]',rawdatalist[x]):
        tempMRN = ''
        tempname = ''
        tempDOB = ''
        splitname = rawdatalist[x].split(" ")
# Filter the splitname of non-characters
        splitname = [elem for elem in splitname if elem != ""]
# Keep going and adding to the name until you reach the DOB
        namecounter = 1
        while not re.search('^\([0-9]',splitname[namecounter]):
            tempname = tempname + ' ' + splitname[namecounter]
            namecounter = namecounter + 1
# Assign all values including newly constructed name
        tempMRN = splitname[0]
        tempDOB = splitname[namecounter][1:]
        tempname = tempname[1:]
        tempheaderlist.append(tempMRN)
        tempheaderlist.append(tempname)
        tempheaderlist.append(tempDOB)
# Go to next line after MRN line
        x = x + 1
        while not(bool(re.search('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]',rawdatalist[x])) or bool(re.search('^Medications[:]',rawdatalist[x]))):
            x = x + 1
        if re.search('^Medications[:]',rawdatalist[x]):
            x = x + 1
            if re.search('^[*][*][*]',rawdatalist[x]):
                x = x + 1
# Iterate and add to tempmedlist until non-medication lines that start with
# "***", "Nutrition (", and all lines after these markers until
# one arrives at a line with a MRN
            while not(bool(re.search('^[*][*][*]',rawdatalist[x])) or bool(re.search('^Nutrition \(',rawdatalist[x]))) :
# Removes ending spaces and newlines using
                tempmedlist.append(rawdatalist[x].strip())
                x = x+1
                tempmedtimelist = []
                for i in tempmedlist:
					match = re.search('for [0-9]* days', i)
					if match:
						numDaysMatch = re.search('[0-9]+', match.group())
						if numDaysMatch:
#							print numDaysMatch.group()
							numDaysFloat = float(numDaysMatch.group())
#							print numDaysFloat
						else:
							numDaysFloat = "0"
					else:
						numDaysFloat = -9999999999999999999999999999999
					match2 = re.search('on [0-9]+/[0-9]+/[0-9]+', i)
					if match2:
#						print match2.group()
						date = match2.group()
						date = date.replace("2003","03")
						date = date.replace("2004","04")
						date = date.replace("2005","05")
						date = date.replace("2006","06")
						date = date.replace("2007","07")
						date = date.replace("2008","08")
						date = date.replace("2009","09")
						date = date.replace("2010","10")
						date = date.replace("2011","11")
						date = date.replace("2012","12")
						date = date.replace("2013","13")
						date = date.replace("2014","14")
						date = date.replace("2015","15")
						date = date.replace("2016","16")
						date = date.replace("2017","17")
						date = date.replace("2018","18")
						date = date.replace("2019","19")
						date = date.replace("2020","20")
						date = date.replace("2021","21")
						date = date.replace("2022","22")
						date = date.replace("2023","23")
						date = date.replace("2024","24")
						date = date.replace("2025","25")
						date = date.replace("2026","26")
						date = date.replace("2027","27")
						date = date.replace("2028","28")
						date = date.replace("2029","29")
						date = date.replace("2030","30")
#						print date
						dateStripped = time.strptime(date,"on %m/%d/%y")
						dateNow = time.localtime()
						dateDif = (time.mktime(dateNow) - time.mktime(dateStripped))/60/60/24
						timeLeft = numDaysFloat - dateDif
						timeLeft = round(timeLeft)
						if timeLeft > 0:
							timeLeft = timeLeft
						elif timeLeft < 0 and timeLeft > -999999:
 							timeLeft = "0"
#						print dateStripped
#						print dateNow
#						print dateDif
#						print timeLeft
					else:
						timeLeft = "N/A"
					if timeLeft <= -9999999:
						timeLeft = "PC"
					tempmedtimelist.append(timeLeft)
            totalpages = int(round((.5 + (len(tempmedlist)/MAXMEDS)),0))
            if len(tempmedlist) > MAXMEDS:
                while len(tempmedlist) > MAXMEDS:
                    temppagelist.append('Page ' + str(pagecount) + ' of ' + str(totalpages))
                    pagecount = pagecount + 1
                    temprowlist = tempheaderlist + temppagelist + tempmedlist[0:MAXMEDS] + tempmedtimelist[0:MAXMEDS]
                    outputWriter.writerow(temprowlist)
                    tempmedlist = tempmedlist[MAXMEDS:]
                    tempmedtimelist = tempmedtimelist[MAXMEDS:]
                    temppagelist = []
                    temprowlist = []
        while len(tempmedlist) < MAXMEDS:
			c = MAXMEDS - len(tempmedlist)
			while c > 0:
				tempmedlist.append(" ")
				c = c - 1
        temppagelist.append('Page ' + str(pagecount) + ' of ' + str(totalpages))
        temprowlist = tempheaderlist + temppagelist + tempmedlist + tempmedtimelist
        outputWriter.writerow(temprowlist)
        tempmedlist = []
        temprowlist = []
        try:
            while not (bool(re.search('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]',rawdatalist[x])) or x >= len(rawdatalist)):
                x = x + 1
        except:
            pass
    else:
        x = x + 1

print("Done!  Med list output to file named: "+outfile.name)

# Close files and connections and exit
infile.close()
outfile.close()
sys.exit()
