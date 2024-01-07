import numpy as np 
from stopper import stopper
from utils import *

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
        elif self.mode.casefold() == 'alphanumeric':
            bit_string += self.encode_alphanumeric(data)
        elif self.mode.casefold() == 'byte':
            bit_string += self.encode_byte(data)
        
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
    
    def encode_alphanumeric(self,data):
        nchar = len(data)
        nfields = nchar // 2
        nremainder = nchar % 2
        bit_string = ''
        for ifield in range(nfields):
            field = data[2*ifield:2*(ifield+1)]
            bit_string += to_bit_string(field[0]*45+field[1],length=11)
        if nremainder == 1:
            field = data[-1]
            bit_string += to_bit_string(field,length=6)
        return bit_string
    
    def encode_byte(self,data):
        bit_string = '' 
        for char in data:
            bit_string += to_bit_string(ord(char),length=8)
        return bit_string

    # Table 5
    def alphanumeric_table(self,char):
        char_dict = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,
                     '6':6,'7':7,'8':8,'9':9,'A':10,'B':11,
                     'C':12,'D':13,'E':14,'F':15,'G':16,'H':17,
                     'I':18,'J':19,'K':20,'L':21,'M':22,'N':23,
                     'O':24,'P':25,'Q':26,'R':27,'S':28,'T':29,
                     'U':30,'V':31,'W':32,'X':33,'Y':34,'Z':35,
                     ' ':36,'$':37,'%':38,'*':39,'+':40,'-':41,
                     '.':42,'/':43,':':44}
        return char_dict[char]


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