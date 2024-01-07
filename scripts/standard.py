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
        '1L': [(1,26,19,2)],                   '1M': [(1,26,16,4)],                '1Q': [(1,26,13,6)],                '1H': [(1,26,9,8)],
        '2L': [(1,44,34,4)],                   '2M': [(1,44,28,8)],                '2Q': [(1,44,22,11)],               '2H': [(1,44,16,14)],
        '3L': [(1,70,55,7)],                   '3M': [(1,70,44,13)],               '3Q': [(2,35,17,9)],                '3H': [(2,35,13,11)],
        '4L': [(1,100,80,10)],                 '4M': [(2,50,32,9)],                '4Q': [(2,50,24,13)],               '4H': [(4,25,9,8)],
        '5L': [(1,134,108,13)],                '5M': [(2,67,43,12)],               '5Q': [(2,33,15,9),(2,34,16,9)],    '5H': [(2,33,11,11),(2,34,12,11)],
        '6L': [(2,96,68,9)],                   '6M': [(4,43,27,8)],                '6Q': [(4,43,19,12)],               '6H': [(4,43,15,14)],
        '7L': [(2,98,78,10)],                  '7M': [(4,49,31,9)],                '7Q': [(2,32,14,9),(4,33,15,9)],    '7H': [(4,39,13,13),(1,40,14,13)],
        '8L': [(2,121,97,12)],                 '8M': [(2,60,38,11),(2,61,39,11)],  '8Q': [(4,40,18,11),(2,41,19,11)],  '8H': [(4,40,14,13),(2,41,15,13)],
        '9L': [(2,146,116,15)],                '9M': [(3,58,36,11),(2,59,37,11)],  '9Q': [(4,36,16,10),(4,37,17,10)],  '9H': [(4,16,12,12),(4,37,13,12)],
        '10L':[(2,86,68,9),(2,87,69,9)],       '10M':[(4,69,43,13),(1,70,44,13)],  '10Q':[(6,43,19,12),(2,44,20,12)],  '10H':[(6,43,15,14),(2,44,16,14)],
        '11L':[(4,101,81,10)],                 '11M':[(1,80,50,15),(4,81,51,15)],  '11Q':[(4,50,22,14),(4,51,23,14)],  '11H':[(3,36,12,12),(8,37,13,12)],
        '12L':[(2,116,92,12),(2,117,93,12)],   '12M':[(6,58,36,11),(2,59,37,11)],  '12Q':[(4,46,20,13),(6,47,21,13)],  '12H':[(7,42,14,14),(4,43,15,14)],
        '13L':[(4,133,107,13)],                '13M':[(8,59,37,11),(1,60,38,11)],  '13Q':[(8,44,20,12),(4,45,21,12)],  '13H':[(13,33,11,11),(4,34,12,11)],
        '14L':[(3,145,115,15),(1,146,116,15)], '14M':[(4,64,40,12),(5,65,41,12)],  '14Q':[(11,36,16,10),(5,37,17,10)], '14H':[(11,36,12,12),(5,37,13,12)],
        '15L':[(5,109,87,11),(1,110,88,11)],   '15M':[(5,65,41,12),(5,66,42,12)],  '15Q':[(5,54,24,15),(7,55,25,15)],  '15H':[(11,36,12,12),(7,37,13,12)],
        '16L':[(5,122,98,12),(1,123,99,12)],   '16M':[(7,73,45,14),(3,74,46,14)],  '16Q':[(15,43,19,12),(2,44,20,12)], '16H':[(3,45,15,15),(13,46,16,15)],
        '17L':[(1,135,107,14),(5,136,108,14)], '17M':[(10,74,46,14),(1,75,47,14)], '17Q':[(1,50,22,14),(15,51,23,14)], '17H':[(2,42,14,14),(17,43,15,14)],
        '18L':[(5,150,120,15),(1,151,121,15)], '18M':[(9,69,43,13),(4,70,44,13)],  '18Q':[(17,50,22,14),(1,51,23,14)], '18H':[(2,42,14,14),(19,43,15,14)],
        '19L':[(3,141,113,14),(4,142,114,14)], '19M':[(3,70,44,13),(11,71,45,13)], '19Q':[(17,47,21,13),(4,48,22,13)], '19H':[(9,39,13,13),(16,40,14,13)],
        '20L':[(3,135,107,14),(5,136,108,14)], '20M':[(3,67,41,13),(13,68,42,13)], '20Q':[(15,54,24,15),(5,55,25,15)], '20H':[(15,43,15,14),(10,44,16,14)],
        '21L':[(4,144,116,14),(4,145,117,14)], '21M':[(17,68,42,13)],              '21Q':[(17,50,22,14),(6,51,23,14)], '21H':[(19,46,16,15),(6,47,17,15)],
        '22L':[(2,139,111,14),(7,140,112,14)], '22M':[(17,74,46,14)],              '22Q':[(7,54,24,15),(16,55,25,15)], '22H':[(34,37,13,12)],
        '23L':[(4,151,121,15),(5,152,122,15)], '23M':[(4,75,47,14),(14,76,48,14)], '23Q':[(11,54,24,15),(14,55,25,15)],'23H':[(16,45,15,15),(14,46,16,15)],
        '24L':[(6,147,117,15),(4,148,118,15)], '24M':[(6,73,45,14),(14,74,46,14)], '24Q':[(11,54,24,15),(16,55,25,15)],'24H':[(30,46,16,15),(2,47,17,15)],
        '25L':[(8,132,106,13),(4,133,107,13)], '25M':[(8,75,47,14),(13,76,48,14)], '25Q':[(7,54,24,15),(22,55,25,15)], '25H':[(22,45,15,15),(13,46,16,15)],
        '26L':[(10,142,114,14),(2,143,115,14)],'26M':[(19,74,46,14),(4,75,47,14)], '26Q':[(28,50,22,14),(6,51,23,14)], '26H':[(33,46,16,15),(4,47,17,15)],
        '27L':[(8,152,122,15),(4,153,123,15)], '27M':[(22,73,45,14),(3,74,46,14)], '27Q':[(8,53,23,15),(26,54,24,15)], '27H':[(12,45,15,15),(28,46,16,15)],
        '28L':[(3,147,117,15),(10,148,118,15)],'28M':[(3,73,45,14),(23,74,46,14)], '28Q':[(4,54,24,15),(31,55,25,15)], '28H':[(11,45,15,15),(31,46,16,15)],
        '29L':[(7,146,116,15),(7,147,117,15)], '29M':[(21,73,45,14),(7,74,46,14)], '29Q':[(1,53,23,15),(37,54,24,15)], '29H':[(19,45,15,15),(26,46,16,15)],
        '30L':[(5,145,115,15),(10,146,116,15)],'30M':[(19,75,47,14),(10,76,48,14)],'30Q':[(15,54,24,15),(25,55,25,15)],'30H':[(23,45,15,15),(25,46,16,15)],
        '31L':[(13,145,115,15),(3,146,116,15)],'31M':[(2,74,46,14),(29,75,47,14)], '31Q':[(42,54,24,15),(1,55,25,15)], '31H':[(23,45,15,15),(28,46,16,15)],
        '32L':[(17,145,115,15)],               '32M':[(10,74,46,14),(23,75,47,14)],'32Q':[(10,54,24,15),(35,55,25,15)],'32H':[(19,45,15,15),(35,46,16,15)],
        '33L':[(17,145,115,15),(1,146,116,15)],'33M':[(14,74,46,14),(21,75,47,14)],'33Q':[(29,54,24,15),(19,55,25,15)],'33H':[(11,45,15,15),(46,46,16,15)],
        '34L':[(13,145,115,15),(6,146,116,15)],'34M':[(14,74,46,14),(23,75,47,14)],'34Q':[(44,54,24,15),(7,55,25,15)], '34H':[(59,46,16,15),(1,47,17,15)],
        '35L':[(12,151,121,15),(7,152,122,15)],'35M':[(12,75,47,14),(26,76,48,14)],'35Q':[(39,54,24,15),(14,55,25,15)],'35H':[(22,45,15,15),(41,46,16,15)],
        '36L':[(6,151,121,15),(14,152,122,15)],'36M':[(6,75,47,14),(34,76,48,14)], '36Q':[(46,54,24,15),(10,55,25,15)],'36H':[(2,45,15,15),(64,46,16,15)],
        '37L':[(17,152,122,15),(4,153,123,15)],'37M':[(29,74,46,14),(14,75,47,14)],'37Q':[(49,54,24,15),(10,55,25,15)],'37H':[(24,45,15,15),(46,46,16,15)],
        '38L':[(4,152,122,15),(18,153,123,15)],'38M':[(13,74,46,14),(32,75,47,14)],'38Q':[(48,54,24,15),(14,55,25,15)],'38H':[(42,45,15,15),(32,46,16,15)],
        '39L':[(20,147,117,15),(4,148,118,15)],'39M':[(40,75,47,14),(7,76,48,14)], '39Q':[(43,54,24,15),(22,55,25,15)],'39H':[(10,45,15,15),(67,46,16,15)],
        '40L':[(19,148,118,15),(6,149,119,15)],'40M':[(18,75,47,14),(31,76,48,14)],'40Q':[(34,54,24,15),(34,55,25,15)],'40H':[(20,45,15,15),(61,46,16,15)]
        
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