import rxnorm
import rxnorm_io
import sys
import med_parsing_V2.star_panel_med_parser as spmp
import charge_db_builder as cdbb
import charge_db_browser as browser

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

def preprocess(data):
    i = data.rfind('mg')
    if i > -1 :
        data = data[0:i+2]
    return data


if __name__ == '__main__':

    if sys.argv[1].find('p') > -1:
        assert spmp.split_by_parentheses('aab(aa)') == ['aab', '(aa)']
        assert spmp.split_by_parentheses('aab(aa)a') == ['aab', '(aa)','a']
        assert spmp.split_by_parentheses('aab(a(xx)a)') == ['aab', '(a(xx)a)']
        assert spmp.split_by_parentheses('aab(a(xx)(xy)a)') == ['aab', '(a(xx)(xy)a)']
        assert spmp.split_by_parentheses('aab(a(xx)(xy)a)(xxy)') == ['aab', '(a(xx)(xy)a)','(xxy)']
        assert spmp.split_by_parentheses('aab(a(xx)(xy)a()(xxy))') == ['aab', '(a(xx)(xy)a()(xxy))']
        assert spmp.split_by_parentheses('aab(a(xx)(xy)a()(xxy)') == ['aab(', 'a', '(xx)', '(xy)', 'a', '()', '(xxy)']
        assert spmp.split_by_parentheses('aaba(xx)(xy)a()(xxy))') == ['aaba', '(xx)', '(xy)', 'a', '()', '(xxy)', ')']
        print "Parentheses Tests Passed!!"

        for data in create_test_data(bool(int(sys.argv[2]))):
            print data
            print spmp.split_by_parentheses(data), '\n'
            print spmp.StarPanelMedParser().tokenize(data)

    if sys.argv[1].find('r') > -1:
        test_data = create_test_data(bool(int(sys.argv[2])))
        for data in test_data:
            print data
            data = preprocess(data)
            rxcui, name = rxnorm_io.do_rxnorm(data)
            rxnorm_io.output_rxnorm(rxcui,name)
            print ''
    if sys.argv[1].find('n') > -1:
        builder = cdbb.DatabaseBuilder(sys.argv[2])
        print builder.get_data_for_rxnorm_row(259255)

    if sys.argv[1].find('c') > -1:
        helper = browser.ChargeDBHelper()
        for raw_ndc in ['1671444602','781148610', '6050501571', '1657150050']:
            print raw_ndc,cdbb.fmt_NDC_and_get_rxcui(helper.cur, raw_ndc)
