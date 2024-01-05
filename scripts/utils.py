import numpy as np 
from stopper import stopper 
import galois

class BCH_code_string():
    '''
    A class that generate BCH code string.

    Arguments:
        nn (int): Total length of string.
        kk (int): Length of data.
    '''
    def __init__(self,nn: int,kk: int):
        self.nn = nn 
        self.kk = kk
        # Create a finite field
        self.GF = galois.GF(2,repr='poly')
        self.get_generator()

    def generate(self,data_string):
        '''
        Arguments:
            data_string (str): A sequence of 0 and 1.
        '''
        # Check data string length 
        if len(data_string) != self.kk:
            stopper(f"Data string length {len(data_string)} doesn't match k {self.kk}")        
        # Convert data string into a polynomial
        data = [eval(each) for each in data_string]
        data = galois.Poly(data+[0]*(self.nn-self.kk),field=self.GF)
        remainder = data%self.generator 
        sequence = data_string
        coefficients = remainder.coefficients()
        sequence += to_bit_string(np.array(coefficients),self.nn-self.kk)
        # sequence += '0'*(self.nn-self.kk-len(coefficients))
        # for each in coefficients:
        #     sequence += str(each)
        return sequence

    def get_generator(self):
        if self.nn - self.kk == 10:
            self.generator = galois.Poly([1,0,1,0,0,1,1,0,1,1,1])
        elif self.nn - self.kk == 12:
            self.generator = galois.Poly([1,1,1,1,1,0,0,1,0,0,1,0,1])
        else:
            stopper(f"nn - kk = {self.nn-self.kk} not implemented")

class RS_error_corection():
    def __init__(self,nn,kk):
        self.nn = nn 
        self.kk = kk
        self.GF = galois.GF(2**8,repr='int')
        self.alpha = self.GF.primitive_element
        self.get_generator(self.nn-self.kk) 

    def generate(self,data_codewords:list):
        if len(data_codewords) != self.kk:
            stopper(f"Data string length {len(data_codewords)} doesn't match k {self.kk}")   
        codewords = data_codewords.copy()
        data = galois.Poly(data_codewords+[0]*(self.nn-self.kk),field=self.GF)
        remainder = data%self.generator
        coefficients = np.array(remainder.coefficients())
        codewords += [0]*(self.nn-self.kk-len(coefficients))
        for each in coefficients:
            codewords.append(int(each))
        return codewords

    def get_generator(self,error_correction_codeword_length):
        generator_power_dict = {
            2:(0,25,1),
            5:(0,113,164,166,119,10),
            6:(0,166,0,134,5,176,15),
            7:(0,87,229,146,149,238,102,21),
            8:(0,175,238,208,249,215,252,196,28),
            10:(0,251,67,46,61,118,70,64,94,
                32,45),
            13:(0,74,152,176,100,86,100,106,104,
                130,218,206,140,78),
            14:(0,199,2449,155,48,190,124,218,
                137,216,87,207,59,22,91),
            15:(0,8,183,61,91,202,37,51,58,
                58,237,140,124,5,99,105),
            16:(0,120,104,107,109,102,161,76,
                3,91,191,147,169,182,194,225,120),
            17:(0,43,139,206,78,43,239,123,
                206,214,147,24,99,150,39,243,
                163,136),
            18:(0,215,234,158,94,184,97,118,
                170,79,187,152,148,252,179,5,
                98,96,153),
            20:(0,17,60,79,50,61,163,26,187,
                202,180,221,225,83,239,156,164,
                212,212,188,190),
            22:(0,210,171,247,242,93,230,14,
                109,221,53,200,74,8,172,98,
                80,219,134,160,105,165,231),
            24:(0,229,121,135,48,211,117,251,
                126,159,180,169,152,192,226,
                228,218,111,0,117,232,87,96,227,
                21),
            26:(0,173,125,158,2,103,182,118,
                17,145,201,111,28,165,53,
                161,21,245,142,13,102,48,227,
                153,145,218,70),
            28:(),
            30:(),
            32:(),
            34:(),
            36:(),
            40:(),
            42:(),
            44:(),
            46:(),
            48:(),
            50:(),
            52:(),
            54:(),
            56:(),
            58:(),
            60:(),
            62:(),
            64:(),
            66:(),
            68:(),

        
        }
        generator_power = generator_power_dict[error_correction_codeword_length]
        self.generator = galois.Poly([self.alpha**each for each in generator_power],field=self.GF)
        # for ii in range(error_correction_codeword_length):
        #     if ii==0:
        #     self.generator = galois.Poly([])

        

def xor_strings(str1,str2):
    result = ''
    for c1,c2 in zip(str1,str2):
        result += str(int(c1)^int(c2))
    return result

def to_bit_string(obj,length=None):
    bit_string = ''
    if isinstance(obj,list) or isinstance(obj,np.ndarray):
        if not length is None:
            bit_string += '0'*(length-len(obj))
        for each in obj:
            bit_string += str(each)
    elif isinstance(obj,int):
        bit_string += bin(obj)[2:]
        if not length is None:
            bit_string = '0'*(length-len(bit_string)) + bit_string 
    elif isinstance(obj,str):
        bit_string += bin(eval(obj))[2:]
        if not length is None:
            bit_string = '0'*(length-len(bit_string)) + bit_string 
    else:
        # Assuming input object is np.int
        bit_string += bin(obj)[2:]
        if not length is None:
            bit_string = '0'*(length-len(bit_string)) + bit_string 
    return bit_string

def bit_string_to_number(bit_string):
    return eval('0b'+bit_string)

def bit_string_to_codewords(bit_string):
    if len(bit_string) % 8 != 0:
        stopper(f'Unable to convert bit string to codewords: bit string length = {len(bit_string)}')
    codewords = []
    for ii in range(len(bit_string)//8):
        codewords.append(bit_string_to_number(bit_string[8*ii:8*(ii+1)]))
    return codewords

def bit_string_to_bit_list(bit_string):
    bit_list = [eval(each) for each in bit_string]
    return bit_list

if __name__ == '__main__':
    field = galois.GF(2**8,repr='poly')
    # rs = galois.ReedSolomon(n=33,k=11)
    # print(rs)
    # data = field.Poly([[67,85,70,134,87,38,85,194,119,50,6]])
    # print(type(rs.encode(data)))
    # rs = RS_error_corection(33,11)
    # print(rs.generate([67,85,70,134,87,38,85,194,119,50,6]))
    data = '00010000 00100000 00001100 01010110 01100001 10000000 11101100 00010001 11101100 00010001 11101100 00010001 11101100 00010001 11101100 00010001'
    data_codewords = [bit_string_to_number(each) for each in data.split()]
    print(data_codewords)
    rs = RS_error_corection(26,16)
    a = rs.generate(data_codewords)
    print(a)