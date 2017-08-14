import sys

def fmt_ndcs(filename):
    f = open(filename)
    ndcs = []
    for line in f:
        ndcs.append(format_ndc(line))
    return ndcs

def format_ndc(ndc_raw):
    NDC = ''
    ndc_raw = ndc_raw.strip()

    if ndc_raw.count('-') != 2: pass
    elif len(ndc_raw.replace('-','')) < 10 : pass
    elif len(ndc_raw.replace('-','')) == 11:
        NDC = ndc_raw.replace('-','')
    elif is442(ndc_raw):
        NDC = '0' + ndc_raw.replace('-','')
    elif is532(ndc_raw):
        NDC = (ndc_raw[:6] + '0' + ndc_raw[6:]).replace('-','')
    elif is541(ndc_raw):
        NDC = (ndc_raw[:10] + '0' + ndc_raw[10:]).replace('-','')

    return NDC.strip()

def is442(ndc):
    return isndcfmt(ndc,[4,4,2])

def is532(ndc):
    return isndcfmt(ndc,[5,3,2])

def is541(ndc):
    return isndcfmt(ndc,[5,4,1])

def isndcfmt(ndc,pat):
    """
    4444-4444-22
        4    9
    """
    return ndc[pat[0]] == '-' and ndc[(pat[2]+1)*-1]


def main(filename):
    ndcs = fmt_ndcs(filename)
    print '\n'.join(ndcs)

if __name__ == "__main__":
    main(sys.argv[1])
