import requests
import xml.etree.ElementTree as etree
import re


"""
Useful for synonyms
    Related concepts: https://rxnav.nlm.nih.gov/RxNormAPIREST.html#uLink=RxNorm_REST_getAllRelatedInfo
    Spelling suggestions: https://rxnav.nlm.nih.gov/RxNormAPIs.html#uLink=RxNorm_REST_getSpellingSuggestions

Test Strings
    Premarin apply three times a week prn
    cyclobenzaprine 10 mg qhs
    albuterol [Ventolin] 2 puffs q4-6h prn
    Advair Diskus 100/50 1 puff 2 times a day
    gabapentin 1200 mg dispensed as 300mg pills: 1 in the morning, 1 at noon, 2 at night
    fluticasone furoate (Veramyst) two sprays in each nostril qday
    Fish Oil 1000mg cap qday
    Astepro 0.15 SPR 1 spray in each nostril each morning
    carvedilol 50mg BID after eating
    isosorbide mononitrate 30 mg ER QD
    Flonase nasal spray 2 sprays per nostril QD
    hydrocortisone cream 1% apply to face prn
    triamcinolone acetonide 0.1 % Ointment Apply a thin layer to affected area twice a day.
    sulfamethoxazole 800 mg-trimethoprim 160 mg tablet (Also Known As Bactrim DS) 1 tablet by mouth twice a day for 7 days
    nitroglycerin 0.4 mg under the tongue every 5 minutes as needed for chest pain, maximum of 3 tablets
    Depo-Provera given at STC on 06/11/16
    Mapap (acetaminophen) 325 mg 2 tabs every 4-6 hrs prn, no more than 6 tabs per day
"""

BASE_URL = 'https://rxnav.nlm.nih.gov/REST'
class Constants:
    name = 'name'
    rxcui = 'rxcui'

def get_rxnorm_version():
    return xml_tree_for_url('/version').findtext('version')

def suggested_spelling(search_term):
    tree = xml_tree_for_url('/spellingsuggestions.xml?name=' + search_term)
    return [etree.tostring(sugg, method='text') for sugg in tree.findall('./suggestionGroup/suggestionList/suggestion')]
# print xml.etree.ElementTree.tostring(tree, encoding='utf8', method='xml')

def get_approx_term(term, unique_rxcuid=False, max_return=3, options=1):
    tree = xml_tree_for_url('/approximateTerm?term={value}&maxEntries={max}&option={opt}'.format(value = term, max = max_return, opt=options))
    approx_terms = []
    seen = {}
    for candidate in tree.findall('./approximateGroup/candidate'):
        approx_dict = dict_from_tags(candidate, [Constants.rxcui, 'rxaui', 'score','rank'])
        rxcui = approx_dict[Constants.rxcui]
        if unique_rxcuid and seen.get(rxcui, False) : continue
        else : seen[rxcui] = True
        approx_terms.append(approx_dict)
    return approx_terms

def get_rxcui_id_for_string(presc_string, start_cnt=6, uniq_threshold=80, score_threshold=50):
    split = re.split('[\W]+',presc_string.lower())
    start_cnt = min(len(split),start_cnt)

    match_dict = {}

    for i in range(start_cnt,0,-1):
        approx_list = get_approx_term(' '.join(split[0:i]),True)

        rxcui_above_threshold = []


        for approx_dict in approx_list:
            rxcui = approx_dict[Constants.rxcui]
            #only want to score unique rxcui approximates from returns
            value = match_dict.get(rxcui, 0)
            new_val = int(approx_dict['score'])
            if new_val < score_threshold : continue
            if new_val > uniq_threshold : rxcui_above_threshold.append(rxcui)
            match_dict[rxcui] = value + new_val

        #if only 1 unique rxcui approximation score > uniq_threshold, then short circuit & use it!
        if  len(rxcui_above_threshold) == 1:
            match_dict = {}
            match_dict[rxcui_above_threshold[0]]=0
            break

    # if no matches within parameters, we need to figure something else out
    if len(match_dict) == 0 : return None
    # get best rxcui; if scores are the same, use lowest rxcui
    best_rxcui = None
    for rxcui in sorted(match_dict.keys(),key=int, reverse=True):

        if match_dict[rxcui] >= match_dict.get(best_rxcui,-1) :
            best_rxcui = rxcui

    # finally, look for brand name in split
    for (brand_nm,rxcui) in get_brand_names_for_rxcui(best_rxcui,True):
        if brand_nm.lower() in split :
            best_rxcui = rxcui
            break

    return best_rxcui

def get_brand_names_for_rxcui(ing_rxcui,ret_w_rxcui=False):
    tree = xml_tree_for_url('/brands?ingredientids={rxcui}'.format(rxcui = ing_rxcui))
    brand_nms = []
    for brand_node in tree.findall('./brandGroup/conceptProperties'):
        brand_nm = brand_node.findtext(Constants.name)
        if ret_w_rxcui: brand_nms.append((brand_nm,brand_node.findtext(Constants.rxcui)))
        else : brand_nms.append(brand_nm)
    return brand_nms

def get_name_for_rxcui_id(rxcui):
    return get_properties_for_rxcui(rxcui,[Constants.name])[Constants.name]

def get_properties_for_rxcui(rxcui,property_names):
    tree = xml_tree_for_url('/rxcui/{rxcuid}/properties'.format(rxcuid = rxcui))

    return dict_from_tags(tree.find('./properties'),property_names)



def dict_from_tags(tree, tags):
    tag_dict = {}
    for tag in tags:
        tag_dict[tag] = tree.findtext(tag)
    return tag_dict

def xml_tree_for_url(resource):
    url = BASE_URL + resource
    response = requests.get(url)
    return etree.fromstring(response.text)
