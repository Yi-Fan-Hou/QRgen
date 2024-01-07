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
            28:(0,168,223,200,104,224,234,108,
                180,110,190,195,147,205,27,
                232,201,21,43,245,87,42,
                195,212,119,242,37,9,123),
            30:(0,41,173,145,152,216,31,179,
                182,50,48,110,86,239,96,
                222,125,42,173,226,193,224,
                130,156,37,251,216,238,40,192,
                180),
            32:(0,10,6,106,190,249,167,4,67,
                209,138,138,32,242,123,89,
                27,120,185,80,156,38,69,
                171,60,28,222,80,52,254,185,
                220,241),
            34:(0,111,77,146,94,26,21,108,
                19,105,94,113,193,86,140,
                163,125,58,158,229,239,218,
                103,56,70,114,61,183,129,
                167,13,98,62,129,51),
            36:(0,200,183,98,16,172,31,246,
                234,60,152,115,0,167,152,
                113,248,238,107,18,63,218,
                37,87,201,105,177,120,74,
                121,196,117,251,113,233,30,120),
            40:(0,59,183,98,16,172,31,246,
                234,60,152,115,0,167,152,
                113,248,238,107,18,63,218,
                37,87,210,105,177,120,74,
                121,196,117,251,113,233,30,120),
            42:(0,250,103,221,230,25,18,137,
                231,0,3,58,242,221,191,110,
                84,230,8,188,106,96,147,15,
                131,139,34,101,223,39,101,213,
                199,237,254,201,123,171,162,194,
                117,50,96),
            44:(0,190,7,61,121,71,246,69,55,
                168,188,89,243,191,25,72,123,
                9,145,14,247,1,238,44,78,
                143,62,224,126,118,114,68,163,
                52,194,217,147,204,169,37,130,
                113,102,73,181),
            46:(0,112,94,88,112,253,224,202,115,
                187,99,89,5,54,113,129,44,
                58,16,135,216,169,211,36,1,
                4,96,60,241,73,104,234,8,
                249,245,119,174,52,25,157,224,
                43,22,223,19,82,15),
            48:(0,228,25,196,130,211,146,60,24,
                251,90,39,102,240,61,178,63,
                46,123,115,18,221,111,135,160,
                182,205,107,206,95,150,120,184,
                91,21,247,156,140,238,191,11,
                94,227,84,50,163,39,34,108),
            50:(0,232,125,157,161,164,9,118,46,
                209,99,203,193,35,3,209,111,
                195,242,203,225,46,13,32,160,
                126,209,130,160,242,215,242,75,
                77,42,189,32,113,65,124,69,
                228,114,235,175,124,170,215,232,
                133,205),
            52:(0,116,50,83,186,50,220,251,89,
                192,46,86,127,124,19,184,233,
                151,215,22,14,59,145,37,242,
                203,134,254,89,190,94,59,65,
                124,113,100,233,235,121,22,76,
                86,97,39,242,200,220,101,33,
                239,254,116,51),
            54:(0,183,26,201,87,210,221,113,21,
                46,65,45,50,238,184,249,225,
                102,58,209,218,109,165,26,95,
                184,192,52,245,35,254,238,175,
                172,79,123,25,122,43,120,108,
                215,80,128,201,235,8,153,59,
                101,31,198,76,31,156),
            56:(0,106,120,107,157,164,216,112,
                116,2,91,248,163,36,201,202,
                229,6,144,254,155,135,208,170,
                209,12,139,127,142,182,249,177,
                174,190,28,10,85,239,184,101,
                124,152,206,96,23,163,61,27,
                196,247,151,154,202,207,20,61,10),
            58:(0,82,116,26,247,66,27,62,107,
                252,182,200,185,235,55,251,242,
                210,144,154,237,176,141,192,248,
                152,249,206,85,253,142,65,165,
                125,23,24,30,122,240,214,6,
                129,218,29,145,127,134,206,245,
                117,29,41,63,159,142,233,125,148,
                123),
            60:(0,107,140,26,12,9,141,243,197,
                226,197,219,45,211,101,219,120,
                28,181,127,6,100,247,2,205,
                198,57,115,219,101,109,160,82,
                37,38,238,49,160,209,121,86,
                11,124,30,181,84,25,194,87,
                65,102,190,220,70,27,209,16,89,
                7,33,240),
            62:(0,65,202,113,98,71,223,248,118,
                214,94,0,122,37,23,2,228,
                58,121,7,105,135,78,243,118,
                70,76,223,89,72,50,70,111,
                194,17,212,126,181,35,221,117,
                235,11,229,149,147,123,213,40,
                115,6,200,100,26,246,182,218,
                127,215,36,186,110,106),
            64:(0,45,51,175,9,7,158,159,49,
                68,119,92,123,177,204,187,254,
                200,78,141,149,119,26,127,53,
                160,93,199,212,29,24,145,156,
                208,150,218,209,4,216,91,47,
                184,146,47,140,195,195,125,242,
                238,63,99,108,140,230,242,31,
                204,11,178,243,217,156,213,231),
            66:(0,5,118,222,180,136,136,162,51,
                466,117,13,215,81,17,139,247,
                197,171,95,173,65,137,178,68,
                111,95,101,41,72,214,169,197,
                95,7,44,154,77,111,236,40,
                121,143,63,87,80,253,240,126,
                217,77,34,232,106,50,167,82,
                76,146,67,106,171,25,132,93,
                45,105),
            68:(0,247,159,223,33,224,93,77,70,
                90,160,32,254,43,150,84,101,
                190,205,133,52,60,202,165,220,
                203,151,93,84,15,84,253,173,
                160,89,227,52,199,97,95,231,
                52,177,41,125,137,241,166,225,
                118,2,54,32,82,215,175,198,
                43,238,235,27,101,184,127,3,
                5,8,163,238),
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