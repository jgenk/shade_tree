import rxnorm

def run_rxnorm_io():
    while True:
        med_text = raw_input('Input medication text: ')
        if len(med_text) == 0 : break
        rxcui, name = do_rxnorm(med_text)
        output_rxnorm(rxcui,name)
    return

def do_rxnorm(med_text):
    rxcui = rxnorm.get_rxcui_id_for_string(med_text)
    name = rxnorm.get_name_for_rxcui_id(rxcui)
    return rxcui, name

def output_rxnorm(rxcui, name):
    print "RXCUI ID: ", rxcui
    print "Drug Name: ", name
    pass

if __name__ == '__main__':
    run_rxnorm_io()
    
