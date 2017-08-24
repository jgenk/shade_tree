import re
import pandas as pd
import sys

def isPPline(line):
    return 'MCKESSON' in line

def extract_NDC(line):
    return re.search('[0-9]{11}',line).group(0)

def extract_pp_info(line):
    ndc = extract_NDC(line)
    parts = line.strip().split(ndc)
    description = parts[0]
    data = parts[1].strip().split()[1:]
    return [description,ndc] + data[:3]

def get_data(line):
    ndc = extract_NDC(line)
    parts = line.strip().split(ndc)
    numbers = parts[1].split()
    return [parts[0],ndc] + numbers


def run(fname):
    f = open(fname)
    qoh_sum = 0

    columns = []
    PPs = []

    for line in f.readlines():
        if isPPline(line):
            PPs.append(extract_pp_info(line))
        else:
            columns.append(get_data(line) + [line])

    df_pp = pd.DataFrame(PPs,columns=['description','ndc','reorder_units','pkg_size','reorder_pkg'])
    df_pp = df_pp.apply(pd.to_numeric,errors='ignore')
    df_all_prod = pd.DataFrame(columns,columns=['description','ndc','gcsn','pkg_size','qoh','qoo','full_line'])
    df_all_prod = df_all_prod.apply(pd.to_numeric,errors='ignore')

    df_pp = df_pp.merge(df_all_prod[['ndc','gcsn','qoh']],on='ndc',how='left')

    gcsn_sum = df_all_prod.groupby('gcsn')['qoh'].sum()
    gcsn_sum.name = 'total_qoh'
    df_gcsn_sum = gcsn_sum.reset_index()

    df_pp = df_pp.merge(df_gcsn_sum,on='gcsn', how='left')

    df_pp['new_inv_lvl'] = df_pp.qoh + df_pp.reorder_units


    df_pp['ndc'] = df_pp.ndc.apply(lambda ndc: '="{}"'.format(str(ndc).zfill(11)))
    df_all_prod['ndc'] = df_all_prod.ndc.apply(lambda ndc: '="{}"'.format(str(ndc).zfill(11)))

    ew = pd.ExcelWriter('po_parsed.xlsx')
    df_pp.to_excel(ew,'preferred_products')
    df_all_prod.to_excel(ew,'all_products')
    ew.close()
    return df_pp

if __name__ == "__main__":
   df_pp = run(sys.argv[1])
   print df_pp
