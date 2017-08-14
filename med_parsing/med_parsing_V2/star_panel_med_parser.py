from med_parser import TokenType, PAPstatus, MedParser
import re

class StarPanelMedParser(MedParser):

    def tokenize(self, presc_text):
        """
        Generates an ordered list of (string, TokenType) tuples based on the prescription text.
        return
        List[(string, TokenType)]
        ErrorMessage string
        """
        string_tokens = split_by_parentheses(presc_text.lower())
        token_list = []
        for string in string_tokens:
            if has_paren(string):
                if is_PAP_info(string):
                    token_list.append(parse_PAP_tokens(string[1:-1]))
                elif is_dispensed_as(string):
                    token_list.append((string[1:-1], TokenType.DISPENSED_AS))
                elif is_dispensed_info(string):
                    token_list.append(parse_dispensed_tokens(string[1:-1]))
                elif is_brand_name(string):
                    token_list.append((string, TokenType.BRAND_NAME))
                else: token_list.append((string, TokenType.UNKNOWN))
            else: token_list.append((string, TokenType.DRUG_INFO))

        return token_list

def is_PAP_info(string):
    return string.find('pap',) > -1


def get_PAP_status(string):
    if len(string) == 0 : return PAPstatus.PAP_UNCERTAIN

    #PAP ineligible cases
    if re.search('ineligible', PAPtext, re.IGNORECASE) : return PAPstatus.PAP_INELIGIBLE
    if re.search('not.+eligible',PAPtext, re.IGNORECASE) : return PAPstatus.PAP_INELIGIBLE
    if re.search('approved', PAPtext, re.IGNORECASE) : return PAPstatus.PAP_APPROVED
    return PAP_UNCERTAIN

def is_dispensed_as(string):
    return string.find('dispensed as') > -1

def is_dispensed_info(string):
    return string.find('dispensed for') > -1

def is_brand_name(string):
    return (string.find('also known as') > -1) or (len(string.split()) <= 2)

def parse_PAP_tokens(string):
    PAP_status = get_PAP_status(string)
    if PAP_status == PAPstatus.APPROVED:
        PAP_date = find_datetime(PAPtext)
    else: PAP_date = None

    return [(PAP_status, TokenType.PAP_STATUS),
            (PAP_date, TokenType.PAP_APPROVED_DT),
            (string, TokenType.PAP_INFO)]

def parse_dispensed_tokens(string):
    disp_dur = parseDispensedDuration(string)
    disp_date = find_datetime(string)
    return [(disp_dur, TokenType.DISPENSED_FOR),
            (disp_date, TokenType.DISPENSED_WHEN),
            (string, TokenType.DISPENSED_INFO)]

def parseDispensedDuration(string):
    match = re.search("for ([0-9]+) days", string)
    if not match : return None
    return match.group(1)

def has_paren(token):
    return token[0] == '(' and token[-1] ==')'

def split_by_parentheses(text):
    """
    Splits text into parenthesized statements (outermost parentheses) and
    unparenthesized statements
    return
        List of split strings without parentheses
    """

    split = []
    cur_str =''
    paren_cnt = 0
    for i in range(0,len(text)):
        next_char = text[i]
        if next_char == '(':
            paren_cnt +=1
            if len(cur_str) > 0 and paren_cnt == 1:
                split.append(cur_str)
                cur_str = ''
        cur_str += next_char
        if next_char == ')':
            paren_cnt -= 1
            if len(cur_str) > 0 and paren_cnt == 0:
                split.append(cur_str)
                cur_str = ''
    if len(cur_str) > 0:
        if paren_cnt == 0 or len(cur_str) == 1: split.append(cur_str)
        else :
            split[-1] += cur_str[0]
            split += split_by_parentheses(cur_str[1:])
    return split


def find_datetime(string):
    match = re.findall("((\d+)[/](\d+)([/]\d+)?)", string)
    if not match : return None

    return match[-1][0]
