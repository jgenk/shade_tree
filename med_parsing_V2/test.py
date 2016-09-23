import rxnorm

def create_test_data(hard_only=False):
        test_data = []
        if not hard_only:
            test_data += [ 'Premarin apply three times a week prn',
                    'cyclobenzaprine 10 mg qhs',
                    'gabapentin 1200 mg dispensed as 300mg pills: 1 in the morning, 1 at noon, 2 at night',
                    'Fish Oil 1000mg cap qday',
                    'Astepro 0.15 SPR 1 spray in each nostril each morning',
                    'Flonase nasal spray 2 sprays per nostril QD',
                    'hydrocortisone cream 1% apply to face prn',
                    'triamcinolone acetonide 0.1 % Ointment Apply a thin layer to affected area twice a day.',
                    'sulfamethoxazole 800 mg-trimethoprim 160 mg tablet (Also Known As Bactrim DS) 1 tablet by mouth twice a day for 7 days',
                    'nitroglycerin 0.4 mg under the tongue every 5 minutes as needed for chest pain, maximum of 3 tablets',
                    'Depo-Provera given at STC on 06/11/16',
                    'Mapap (acetaminophen) 325 mg 2 tabs every 4-6 hrs prn, no more than 6 tabs per day'
            ]
        test_data += [
                        'isosorbide mononitrate 30 mg ER QD',
                        'albuterol [Ventolin] 2 puffs q4-6h prn',
                        'Advair Diskus 100/50 1 puff 2 times a day',
                        'fluticasone furoate (Veramyst) two sprays in each nostril qday',
                        'Veramyst (fluticasone furoate) two sprays in each nostril qday',
                        'carvedilol 50mg BID after eating',
                        'carvedilol phosphate (Coreg)',
                        'carvedilol phosphate 80mg'
                        ]
        return test_data



if __name__ == '__main__':
    test_data = create_test_data(False)
    print "RxNorm Version: ", rxnorm.get_rxnorm_version()
    for data in test_data:
        print data

        #preprocessing of string before getting rxcui
        i = data.rfind('mg')
        if i > -1 :
            data = data[0:i+2]
            # print data

        # word = data.split(' ')[0]
        # print "\tSuggestion List: ", rxnorm.suggested_spelling(word)
        # print "\tGet Approx Tags: ", len(rxnorm.get_approx_term(word))
        rxcui = rxnorm.get_rxcui_id_for_string(data)
        # print "\tBest Rxcui: ", rxcui
        # print "\tName: ", rxnorm.get_name_for_rxcui_id(rxcui)
        print rxnorm.get_name_for_rxcui_id(rxcui)
