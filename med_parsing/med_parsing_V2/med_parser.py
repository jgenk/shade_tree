import abc

class TokenType:
    UNKNOWN = 'UNKNOWN'
    DRUG_INFO = 'DRUG INFO'
    DRUG_NAME = 'NAME'
    BRAND_NAME = 'BRAND NAME'
    DRUG_STR = 'STRENGTH'
    DRUG_ROUTE = 'ROUTE'
    DRUG_FREQ = 'FREQUENCY'
    DISPENSED_AS = 'DISPENSED AS'
    DISPENSED_FOR = 'DISPENSED FOR'
    DISPENSED_WHEN = 'DISPENSED WHEN'
    DISPENSED_INGO = 'DISPENSED INFO'
    PAP_INFO = 'PAP INFO'
    PAP_STATUS = 'PAP STATUS'
    PAP_APPROVED_DT = 'PAP APPROVED UNTIL'

class PAPstatus:
    APPROVED = 'APPROVED'
    INELIGIBLE = 'INELIGIBLE'
    UNCERTAIN = 'UNCERTAIN'

class MedParser(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.token_list = None
        self.presc_text = None

    def set_tokenized_presc(self, presc_text):
        """
        Sets the current state of this parser to the presc_text string, allows
        retrieval of tokens
        Returns
            (True, None)                if tokenized effictively
            (False, str ErrorMessage)   if tokenized fails
        """
        self.presc_text = presc_text
        self.token_list, error_msg = tokenize(presc_text)
        return (not error_msg is None), error_msg


    def get_med_info_tokens(self):
        if not has_active_presc(): return None
        return list_for_token(TokenType.DRUG_INFO)

    def get_dispensed_info_tokens(self):
        """Returns (Dispensed As, Dispensed For, Dispensed When)"""
        if not has_active_presc(): return None
        return (list_for_token(TokenType.DISPENSED_AS),
                list_for_token(TokenType.DISPENSED_FOR),
                list_for_token(TokenType.DISPENSED_WHEN))

    def get_PAP_tokens(self):
        if not has_active_presc(): return None
        return (list_for_token(TokenType.PAP_INFO),
                list_for_token(TokenType.PAP_STATUS),
                list_for_token(TokenType.PAP_APPROVED_DT))



    def get_prescription_parts(self):
        """Returns (Name, (Brand Name), Strength, Route, Frequency)"""
        if not has_active_presc(): return None
        return (list_for_token(TokenType.DRUG_NAME),
                list_for_token(TokenType.BRAND_NAME),
                list_for_token(TokenType.DRUG_STR),
                list_for_token(TokenType.DRUG_ROUTE),
                list_for_token(TokenType.DRUG_FREQ))


    def list_for_token(self, TokenType):
        token_list = []
        for string, TokenType in self.token_list:
            if TokenType == TokenType:
                token_list.append(string)
        return token_list

    def has_active_presc(self):
        return not self.presc_text is None

    @abc.abstractmethod
    def tokenize(self, presc_text):
        """
        Generates an ordered list of (string, TokenType) tuples based on the prescription text.
        return
        List[(string, TokenType)]
        ErrorMessage string
        """
        return
