import re

MSRMT_ABRRV = ['GM','OZ','ML']

def get_num_pills(item_dsc):
    search_result = re.findall(r'([0-9]+[X]?[0-9]*)([A-Z]*)@?$',item_dsc)
    result = 1
    # elif is_msrmt(search_result[0][1]):
    if len(search_result) > 0:
        cnt = search_result[0][0]
        if cnt.find('X') > -1:
            split = cnt.split('X')
            result = int(split[0])*int(split[1])
        elif int(cnt) > 1000:
            result = int(re.findall(r'[1-9]0*$', cnt)[0])
        else:
            result=int(cnt)

    return result

def is_msrmt(text):
    for abbrv in MSRMT_ABRRV:
        if text.upper().find(abbrv) > -1: return True
    return False
