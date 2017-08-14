from lxml import html
import requests
import string
import sys
import re

def open_page(address):
    page = requests.get(address)
    return html.fromstring(page.content)
    
#list of lists [Brand name, Generic name, route/descriptor]
def scrape_PAP_meds():
    
    print "Scraping together PAP medication list..."
    sys.stdout.write("Completed: ")
    meds = []
    for letter in string.uppercase :
        tree = open_page('http://www.needymeds.org/brand-drug/list/' + letter)
        line=0
        while True:
            line+=1
            medtext = get_xpathText(tree, '//*[@id="subblock-content"]/div[7]/a[' + str(line) + ']')
            
            if len(medtext) == 0: break
            #list of lists [Brand name, Generic name, route/descriptor]
            meds.append([part.strip() for part in re.split("[\(\)]+", medtext)])
            
        sys.stdout.write(letter)
    print '\n','Total PAP meds:', len(meds)

def get_xpathText(tree,xpath):
    node = tree.xpath(xpath)
    if len(node) == 0: return ""
    return html.tostring(node[0], method='text').strip()
  
#Using local copy of file from http://www.emedexpert.com/lists/bg.php
#list of lists [Brand name, Generic name, route/descriptor]

def scrape_all_meds():
    
    meds = []
   
   
    f = open('data/alldrugs.html')
    page = f.read()
    tree = html.fromstring(page)
   
    print "Scraping together ALL medication list..."
    sys.stdout.write("Completed: ")
    tr=2 #start at 2, first line is header
    
    while True:
        brand_name = get_xpathText(tree, '//table[@class="bgtable"]/tr['+str(tr)+']/td[1]')
        generic_name = get_xpathText(tree, '//table[@class="bgtable"]/tr['+str(tr)+']/td[2]')
        route = ''
        if generic_name.find("(") >= 0 : 
            split = generic_name.split("(")
            generic_name = split[0].strip()
            route = split[1][:len(split[1])-1]
        
        if len(brand_name + generic_name) == 0: break
        
        meds.append([brand_name,generic_name, route])
        tr+=1
        sys.stdout.write('\rCompleted: %d' % tr)
        sys.stdout.flush()
        
        if tr > 30: break
        
    print '\n','Total meds:', len(meds)
    print meds
    
if __name__ == '__main__':
    
    scrape_all_meds()
    