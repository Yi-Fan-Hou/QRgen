import numpy as np 
from stopper import stopper

class encoder():
    def __init__(self,version,mode): 
        self.version = version 
        self.mode = mode

    def encode(self,data):
        bit_string = ''
        bit_string += self.mode_indicator(self.mode)
        bit_string += self.character_count_indicator(len(data),self.version,self.mode)
        if self.mode.casefold() == 'numeric':
            bit_string += self.encode_numeric(data)
        
        return bit_string
        # self.debug()

    def debug(self):
        data = '01234567'
        bit_string = ''
        bit_string += self.mode_indicator('numeric')
        print(bit_string)
        bit_string += self.character_count_indicator(len(data),indicator_length=10)
        print(bit_string)
        bit_string += self.encode_numeric(data)
        print(bit_string)

    def encode_numeric(self,data):
        nchar = len(data)
        nfields = nchar // 3
        nremainder = nchar % 3
        bit_string = ''
        for ifield in range(nfields):
            field = data[3*ifield:3*(ifield+1)]
            if field[0] == '0':
                if field[1] == '0':
                    field = field[2]
                else:
                    field = field[1:]
            string = bin(eval(field))[2:]
            bit_string += '0'*(10-len(string))+string
        if nremainder == 1:
            field = data[3*nfields:]
            string = bin(eval(field))[2:]
            bit_string += '0'*(4-len(string))+string 
        elif nremainder == 2:
            field = data[3*nfields:]
            string = bin(eval(field))[2:]
            if field[0] == '0':
                field = field[1]
            bit_string += '0'*(7-len(string))+string 
        return bit_string
    
    # Table 2
    def mode_indicator(self,mode):
        if mode.casefold() == 'numeric'.casefold():
            indicator = '0001'
        elif mode.casefold() == 'alphanumeric'.casefold():
            indicator = '0010'
        elif mode.casefold() == 'byte'.casefold():
            indicator = '0100'
        elif mode.casefold() == 'kanji'.casefold():
            indicator = '1000'
        else:
            stopper(f'Unrecognized mode {mode} in mode_indicator')

        return indicator 
    
    def character_count_indicator(self,count,version,mode):
        indicator_length = self.get_character_count_indicator_length(version,mode)
        indicator = bin(count)[2:]
        indicator = '0'*(indicator_length-len(indicator)) + indicator 
        return indicator

    # Table 3
    def get_character_count_indicator_length(self,version,mode):
        if mode.casefold() == 'numeric'.casefold():
            if version <= 9:
                length = 10
            elif version <= 26:
                length = 12
            else:
                length = 14
        elif mode.casefold() == 'alphanumeric'.casefold():
            if version <= 9:
                length = 9
            elif version <= 26:
                length = 11
            else:
                length = 13
        elif mode.casefold() == 'byte'.casefold():
            if version <= 9:
                length = 8
            elif version <= 26:
                length = 16
            else:
                length = 16
        elif mode.casefold() == 'kanji'.casefold():
            if version <= 9:
                length = 8
            elif version <= 26:
                length = 10
            else:
                length = 12
        else:
            stopper(f'Unrecognized mode {mode} in get_character_count_indicator_length')
        return length 
    

if __name__ == '__main__':
    encoder()