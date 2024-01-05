import numpy as np 
import galois
from stopper import stopper
from utils import *

# Get the size of QR code
def get_qr_code_size(version):
    return version*4+17

# Table 1 
def get_number_of_remainder_bits(version):
    number_of_remainder_bits_dict = {
        1:0, 2:7, 3:7, 4:7, 5:7, 6:7, 7:0, 8:0, 9:0, 10:0,
        11:0,12:0,13:0,14:3,15:3,16:3,17:3,18:3,19:3,20:3,
        21:4,22:4,23:4,24:4,25:4,26:4,27:4,28:3,29:3,30:3,
        31:3,32:3,33:3,34:3,35:0,36:0,37:0,38:0,39:0,40:0
    }
    return number_of_remainder_bits_dict[version]

def get_remainder_bits(version):
    return get_number_of_remainder_bits(version)*'0'

# Table 7
def get_maximum_number_of_encoding_bits(version,error_correction_level):
    maximum_number_of_encoding_bits_dict = {
        1:[152,128,104,72],
        2:[272,224,176,128],
        3:[440,352,272,208],
        4:[640,512,384,288],
        5:[864,688,496,368],
        6:[1088,964,608,480],
        7:[1248,992,704,528],
        8:[1552,1232,880,688],
        9:[1856,1456,1056,800],
        10:[2192,1728,1232,976],
        11:[2592,2032,1440,1120],
        12:[2960,2320,1648,1264],
        13:[3424,2672,1952,1440],
        14:[3688,2920,2088,1576],
        15:[4184,3320,2360,1784],
        16:[4712,3624,2600,2024],
        17:[5176,4056,2936,2264],
        18:[5768,4504,3176,2504],
        19:[6360,5016,3560,2728],
        20:[6888,5352,3880,3080],
        21:[7456,5712,4096,3248],
        22:[8048,6256,4544,3536],
        23:[8752,6880,4912,3712],
        24:[9392,7312,5312,4112],
        25:[10208,8000,5744,4304],
        26:[10960,8496,6032,4768],
        27:[11744,9024,6464,5024],
        28:[12248,9544,6968,5288],
        29:[13048,10136,7288,5608],
        30:[13880,10984,7880,5960],
        31:[14744,11640,8264,6344],
        32:[15640,12328,8920,6760],
        33:[16568,13048,9368,7208],
        34:[17528,13800,9848,7688],
        35:[18448,14496,10288,7888],
        36:[19472,15312,10832,8432],
        37:[20528,15936,11408,8768],
        38:[21616,16816,12016,9136],
        39:[22496,17728,12656,9776],
        40:[23648,18672,13328,10208],
    }
    
    error_correction_level_to_index = {
        'L':0,
        'M':1,
        'Q':2,
        'H':3
    }
    
    return maximum_number_of_encoding_bits_dict[version][error_correction_level_to_index[error_correction_level]]

def get_terminator(data_len,version,error_correction_level):
    max_data_len = get_maximum_number_of_encoding_bits(version,error_correction_level)
    remaining_nbits = max_data_len - data_len 
    terminator = ''
    terminator_format = get_terminator_format()

    # Zero padding 
    if remaining_nbits <= len(terminator_format):
        terminator += terminator_format[:remaining_nbits]
    else:
        terminator += terminator_format
        a = (data_len + len(terminator_format)) % 8
        if a != 0:
            terminator += '0' * (8-a) 
    remaining_nbits -= len(terminator)

    # Padding 
    padding_byte1 = '11101100'
    padding_byte2 = '00010001'

    remaining_nbytes = remaining_nbits // 8
    for ibyte in range(remaining_nbytes):
        if ibyte % 2 == 0:
            terminator += padding_byte1
        elif ibyte % 2 == 1:
            terminator += padding_byte2
        else:
            print("ERROR")

    return terminator

# Table 2
def get_mode_indicator(mode):
    mode_indicator_dict = {
        'ECI'.casefold():'0111',
        'Numeric'.casefold():'0001',
        'Alphanumeric'.casefold():'0010',
        'Byte'.casefold():'0100',
        'Kanji'.casefold():'1000',
    }

    return mode_indicator_dict[mode.casefold()]

def get_error_correction_level_indicator(error_correction_level):
    error_correction_level_indicator_dict = {
        'L':'01',
        'M':'00',
        'Q':'11',
        'H':'10'
    }
    return error_correction_level_indicator_dict[error_correction_level]

# This function returns a sequence of 15 bits which encodes format information. First 5 bits are data and the rest are error correction bits.
def get_format_information(error_correction_level,mask_format_indicator):
    # Get raw format information
    sequence = ''
    sequence += get_error_correction_level_indicator(error_correction_level)
    sequence += mask_format_indicator
    # Add error correction
    bch = BCH_code_string(15,5)
    sequence = bch.generate(sequence)
    # Apply mask
    mask_string = '101010000010010'
    sequence = xor_strings(sequence,mask_string)

    return sequence

# This function returns a sequence of 18 bits which encodes version information. First 6 bits are data and the rest are error correction bits.
# Only version >= 7 has version information 
def get_version_information(version):
    sequence = ''
    if version >= 7:
        # Convert version to bit string
        sequence += to_bit_string(version,length=6)
        # Add error correction 
        bch = BCH_code_string(18,6)
        sequence = bch.generate(sequence)
    return sequence

# Table 2
def get_terminator_format():
    return '0000'

# Table 9: Error correction characteristics 
# Error correction code per block is saved as (n,c,k,r)
# (n,c,k,r) represents a group
# n = number of blocks in each group
# c = total number of codewords 
# k = number of data codewords 
# r = error correction capacity 
def get_number_of_error_correction_code(version,error_correction_level):
    number_of_error_correction_code_dict = {
        '1L':[(1,26,19,2)],'1M':[(1,26,16,4)],'1Q':[(1,26,13,6)],'1H':[(1,26,9,8)],
        '2L':[(1,44,34,4)],
        '2M':[(1,44,28,8)],
        '2Q':[(1,44,22,11)],
        '2H':[(1,44,16,14)],
        '3L':[(1,70,55,7)],
        '3M':[(1,70,44,13)],
        '3Q':[(2,35,17,9)],
        '3H':[(2,35,13,11)],
        '4L':[(1,100,80,10)],
        '4M':[(2,50,32,9)],
        '4Q':[(2,50,24,13)],
        '4H':[(4,25,9,8)],
        '5L':[(1,134,108,13)],
        '5M':[(2,67,43,12)],
        '5Q':[(2,33,15,9),(2,34,16,9)],
        '5H':[(2,33,11,11),(2,34,12,11)],
        '6L':[(2,96,68,9)],
        '6M':[(4,43,27,8)],
        '6Q':[(4,43,19,12)],
        '6H':[(4,43,15,14)],
        '7L':[(2,98,78,10)],
        '7M':[(4,49,31,9)],
        '7Q':[(2,32,14,9),(4,33,15,9)],
        '7H':[(4,39,13,13),(1,40,14,13)],
        '8L':[(2,121,97,12)],
        '8M':[(2,60,38,11),(2,61,39,11)],
        '8Q':[(4,40,18,11),(2,41,19,11)],
        '8H':[(4,40,14,13),(2,41,15,13)],
        '9L':[(2,146,116,15)],
        '9M':[(3,58,36,11),(2,59,37,11)],
        '9Q':[(4,36,16,10),(4,37,17,10)],
        '9H':[(4,16,12,12),(4,37,13,12)],
        '10L':[(2,86,68,9),(2,87,69,9)],
        '10M':[(4,69,43,13),(1,70,44,13)],
        '10Q':[(6,43,19,12),(2,44,20,12)],
        '10H':[(6,43,15,14),(2,44,16,14)],
        '11L':[],
        '11M':[],
        '11Q':[],
        '11H':[],
        '12L':[],
        '12M':[],
        '12Q':[],
        '12H':[],
        '13L':[],
        '13M':[],
        '13Q':[],
        '13H':[],
        '14L':[],
        '14M':[],
        '14Q':[],
        '14H':[],
        '15L':[],
        '15M':[],
        '15Q':[],
        '15H':[],
        '16L':[],
        '16M':[],
        '16Q':[],
        '16H':[],
        '17L':[],
        '17M':[],
        '17Q':[],
        '17H':[],
        '18L':[],
        '18M':[],
        '18Q':[],
        '18H':[],
        '19L':[],
        '19M':[],
        '19Q':[],
        '19H':[],
        '20L':[],
        '20M':[],
        '20Q':[],
        '20H':[],
        '21L':[],
        '21M':[],
        '21Q':[],
        '21H':[],
        '22L':[],
        '22M':[],
        '22Q':[],
        '22H':[],
        '23L':[],
        '23M':[],
        '23Q':[],
        '23H':[],
        '24L':[],
        '24M':[],
        '24Q':[],
        '24H':[],
        '25L':[],
        '25M':[],
        '25Q':[],
        '25H':[],
        '26L':[],
        '26M':[],
        '26Q':[],
        '26H':[],
        '27L':[],
        '27M':[],
        '27Q':[],
        '27H':[],
        '28L':[],
        '28M':[],
        '28Q':[],
        '28H':[],
        '29L':[],
        '29M':[],
        '29Q':[],
        '29H':[],
        '30L':[],
        '30M':[],
        '30Q':[],
        '30H':[],
        '31L':[],
        '31M':[],
        '31Q':[],
        '31H':[],
        '32L':[],
        '32M':[],
        '32Q':[],
        '32H':[],
        '33L':[],
        '33M':[],
        '33Q':[],
        '33H':[],
        '34L':[],
        '34M':[],
        '34Q':[],
        '34H':[],
        '35L':[],
        '35M':[],
        '35Q':[],
        '35H':[],
        '36L':[],
        '36M':[],
        '36Q':[],
        '36H':[],
        '37L':[],
        '37M':[],
        '37Q':[],
        '37H':[],
        '38L':[],
        '38M':[],
        '38Q':[],
        '38H':[],
        '39L':[],
        '39M':[],
        '39Q':[],
        '39H':[],
        '40L':[],
        '40M':[],
        '40Q':[],
        '40H':[]
        
    }
    key = str(version) + error_correction_level
    return number_of_error_correction_code_dict[key]

def get_module_arrangement_in_version_information():
    arrangement = [] 
    arrangement.append([
        (-11,0),(-10,0),(-9,0),
        (-11,1),(-10,1),(-9,1),
        (-11,2),(-10,2),(-9,2),
        (-11,3),(-10,3),(-9,3),
        (-11,4),(-10,4),(-9,4),
        (-11,5),(-10,5),(-9,5)
    ][::-1])
    arrangement.append([
        (0,-11),(0,-10),(0,-9),
        (1,-11),(1,-10),(1,-9),
        (2,-11),(2,-10),(2,-9),
        (3,-11),(3,-10),(3,-9),
        (4,-11),(4,-10),(4,-9),
        (5,-11),(5,-10),(5,-9)
    ][::-1])
    return arrangement

# Figure 25
def get_module_arrangement_in_format_information():
    arrangement = []
    arrangement.append([(0,8),(1,8),(2,8),(3,8),(4,8),(5,8),(7,8),(8,8),(8,7),(8,5),(8,4),(8,3),(8,2),(8,1),(8,0)][::-1])
    arrangement.append([(8,-1),(8,-2),(8,-3),(8,-4),(8,-5),(8,-6),(8,-7),(8,-8),(-7,8),(-6,8),(-5,8),(-4,8),(-3,8),(-2,8),(-1,8)][::-1])
    return arrangement

class mask():
    def __init__(self):
        pass 

    def mask(self,mat,reference):
        mat_size = len(mat)
        for ii in range(mat_size):
            for jj in range(mat_size):
                if mat[ii,jj] != 2:
                    mat[ii,jj] = mat[ii,jj] ^ self.maskij(ii,jj,reference)
        return mat

    def maskij(self,ii,jj,reference):
        if reference == '000':
            return (ii+jj)%2
        elif reference == '001':
            return ii%2
        elif reference == '010':
            if jj%3 == 0:
                return 0
            else:
                return 1
        elif reference == '011':
            if (ii+jj)%3 == 0:
                return 0 
            else:
                return 1 
        elif reference == '100':
            return ((ii//2)+(jj//3))%2
        elif reference == '101':
            if (ii*jj)%2 + (ii*jj)%3 == 0:
                return 0 
            else:
                return 1
        elif reference == '110':
            return ((ii*jj)%2+(ii*jj)%3)%2
        elif reference == '111':
            return ((ii+jj)%2+(ii*jj)%3)%2
        

        
if __name__ == '__main__':
    # a = BCH_code_string(15,5)
    # print(a.generate('00101'))
    print(get_format_information('M','101'))
    print(get_version_information(7))