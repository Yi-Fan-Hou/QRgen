from PIL import Image, ImageDraw 
import numpy as np
from standard import *
from pattern import *
from encoder import encoder

class QRgen():
    def __init__(self,data,debug=False):
        if not debug:
            self.version = 5
            self.error_correction_level = 'Q'
            self.encode_mode = 'byte'
            self.mask_format_indicator = '010'
            
            print("Initializing...")
            qr_code_size = get_qr_code_size(self.version)
            qr_code_matrix = np.zeros([qr_code_size,qr_code_size],dtype=np.int8)
            # for ii in range(len(qr_code_matrix)):
            #     qr_code_matrix[:,ii] = 5
            
            qr_code_matrix = self.reserve_function_modules(qr_code_matrix)
            np.save('matrix.npy',qr_code_matrix)

            print("Encoding data...")
            encode_data = encoder(self.version,self.encode_mode).encode(data)
            print("Padding terminator...")
            encode_data += get_terminator(len(encode_data),self.version,self.error_correction_level)
            encode_data_codewords = bit_string_to_codewords(encode_data)

            print("Applying RS error correction...")
            number_of_error_correction_code = get_number_of_error_correction_code(self.version,self.error_correction_level)
            lb = 0
            data_codewords = []
            error_correction_codewords = []
            for igroup in range(len(number_of_error_correction_code)):
                rs = RS_error_corection(number_of_error_correction_code[igroup][1],number_of_error_correction_code[igroup][2])
                for iblock in range(number_of_error_correction_code[igroup][0]):
                    ub = lb + number_of_error_correction_code[igroup][2]
                    encode_data_temp = rs.generate(encode_data_codewords[lb:ub])
                    data_codewords.append(encode_data_temp[:number_of_error_correction_code[igroup][2]])
                    error_correction_codewords.append(encode_data_temp[number_of_error_correction_code[igroup][2]:])
                    lb = ub
            final_codewords = self.interweave_data(data_codewords) + self.interweave_data(error_correction_codewords) 
            print("Arranging symbol characters...")
            qr_code_matrix = self.symbol_character_arrangement(qr_code_matrix,final_codewords)
            print("Applying mask...")
            qr_code_matrix = self.apply_mask(qr_code_matrix)
            print("Adding function modules...")
            qr_code_matrix = self.add_function_modules(qr_code_matrix)

            # np.save('matrix.npy',qr_code_matrix)

            self.matrix_to_image(qr_code_matrix.T,10,5,'test.png')
        else:
            self.debug()


    def debug(self):
        self.version = 1 
        self.error_correction_level = 'M'
        self.encode_mode = 'numeric'
        self.mask_format_indicator = '000'
        
        qr_code_size = get_qr_code_size(self.version)
        qr_code_matrix = np.ones([qr_code_size,qr_code_size],dtype=np.int8)
        qr_code_matrix = self.reserve_function_modules(qr_code_matrix)
        qr_code_matrix = qr_code_matrix // 2 
        self.matrix_to_image(qr_code_matrix,10,5,'test.png')

    def data_analysis(self):
        pass

    def reserve_function_modules(self,mat):
        # Finder pattern + separator + format information
        mat[:9,:9] = 2
        mat[:9,-8:] = 2
        mat[-8:,:9] = 2 
        # Timing pattern 
        mat[6,:] = 2
        mat[:,6] = 2 
        # Version information 
        if self.version >= 7:
            mat[:5,-11:-8] = 2
            mat[-11:-8,:5] = 2
        # Alignment patterns
        for each in get_coordinates_of_alignment_pattern(self.version):
            mat[each[0]-2:each[0]+3,each[1]-2:each[1]+3] = 2

        return mat
    
    # Recursive function
    def interweave_data(self,input_codewords_lists:list):
        codewords_lists = []
        remaining_codewords_lists = []
        min_len = len(input_codewords_lists[0])
        max_len = len(input_codewords_lists[-1])
        if min_len == max_len:
            return list(np.array(input_codewords_lists).T.reshape(min_len*len(input_codewords_lists)))
        else:
            for each_codeword_list in input_codewords_lists:
                if len(each_codeword_list) == min_len:
                    codewords_lists.append(each_codeword_list)
                else:
                    codewords_lists.append(each_codeword_list[:min_len])
                    remaining_codewords_lists.append(each_codeword_list[min_len:])
            return list(np.array(codewords_lists).T.reshape(min_len*len(input_codewords_lists))) + self.interweave_data(remaining_codewords_lists)

    def symbol_character_arrangement(self,qr_code_matrix:np.ndarray,message_codewords:list):
        matrix_size = len(qr_code_matrix)
        reversed_bit_string_sequence = ''
        # for codeword in message_codewords:
        #     reversed_bit_string_sequence += to_bit_string(codeword,length=8)[::-1]
        for codeword in message_codewords:
            reversed_bit_string_sequence += to_bit_string(codeword,length=8)
        reversed_bit_string_sequence += get_remainder_bits(self.version)
        icount = 0
        icolumn_list = [ii for ii in range(matrix_size) if ii%2 == 0][:-4]+[matrix_size-6,matrix_size-4,matrix_size-2]
        for iicolumn in range(len(icolumn_list)):
            icolumn = icolumn_list[iicolumn]
            for irow in range(matrix_size):
                if iicolumn % 2 == 0:
                    potential_position = [(matrix_size-1-irow,matrix_size-icolumn-1),(matrix_size-1-irow,matrix_size-icolumn-2)]
                else:
                    potential_position = [(irow,matrix_size-icolumn-1),(irow,matrix_size-icolumn-2)]
                for each in potential_position:
                    if qr_code_matrix[each] != 2:
                        if reversed_bit_string_sequence[icount] == '0':
                            qr_code_matrix[each] = 0
                        elif reversed_bit_string_sequence[icount] == '1':
                            qr_code_matrix[each] = 1
                        icount += 1 

        return qr_code_matrix
    
    def apply_mask(self,qr_code_matrix):
        _mask = mask()
        return _mask.mask(qr_code_matrix,self.mask_format_indicator)

    def add_function_modules(self,qr_code_matrix):
        matrix_size = len(qr_code_matrix)
        # Finder pattern 
        qr_code_matrix[:7,:7] = finder_pattern 
        qr_code_matrix[:7,-7:] = finder_pattern 
        qr_code_matrix[-7:,:7] = finder_pattern 
        # Seperator 
        qr_code_matrix[7,:8] = 1 
        qr_code_matrix[7,-8:] = 1 
        qr_code_matrix[-8,:8] = 1 
        qr_code_matrix[:8,7] = 1 
        qr_code_matrix[-8:,7] = 1 
        qr_code_matrix[:8,-8] = 1
        # Format information 
        _format_information = get_format_information(self.error_correction_level,mask_format_indicator=self.mask_format_indicator)
        format_information = []
        for each in _format_information:
            if each == '0':
                format_information.append(1)
            elif each == '1':
                format_information.append(0)
        format_information_arrangement = get_module_arrangement_in_format_information()
        for ii in range(len(format_information)):
            qr_code_matrix[format_information_arrangement[0][ii]] = format_information[ii]
            qr_code_matrix[format_information_arrangement[1][ii]] = format_information[ii]
        # Dark module 
        qr_code_matrix[-8,8] = 0
        # Timing pattern 
        timing_pattern = np.ones(matrix_size-16,dtype=np.int8)
        for ii in range(len(timing_pattern)):
            if ii%2 == 0:
                timing_pattern[ii] = 0 
        qr_code_matrix[6,8:-8] = timing_pattern
        qr_code_matrix[8:-8,6] = timing_pattern
        # Version information 
        if self.version >= 7:
            version_information = get_version_information(self.version)
            version_information_arrangement = get_module_arrangement_in_version_information() 
            for ii in range(len(version_information)):
                qr_code_matrix[version_information_arrangement[0][ii]] = version_information[ii]
                qr_code_matrix[version_information_arrangement[1][ii]] = version_information[ii]
        # Alignment patters 
        for each in get_coordinates_of_alignment_pattern(self.version):
            qr_code_matrix[each[0]-2:each[0]+3,each[1]-2:each[1]+3] = alignment_pattern
        
        return qr_code_matrix

    def matrix_to_image(self,matrix,pixel_width,quiet_zone_width,filename):
        img_matrix = self.expand_matrix(matrix,pixel_width,quiet_zone_width)
        self.generate_image(img_matrix,filename)

    def expand_matrix(self,matrix,pixel_width=10,quiet_zone_width=5):
        matrix_shape = np.array(matrix.shape)
        img_matrix_shape = (matrix_shape+quiet_zone_width*2)*pixel_width
        img_matrix = np.ones(img_matrix_shape)

        for ii in range(matrix_shape[0]):
            for jj in range(matrix_shape[1]):
                img_matrix[(quiet_zone_width+ii)*pixel_width:(quiet_zone_width+ii+1)*pixel_width,
                           (quiet_zone_width+jj)*pixel_width:(quiet_zone_width+jj+1)*pixel_width] = matrix[ii,jj]

        return img_matrix

    def generate_image(self,img_matrix,filename):
        shape = img_matrix.shape
        img = Image.new('1',shape,'white')
        drw = ImageDraw.Draw(img)
        for ii in range(shape[0]):
            for jj in range(shape[1]):
                drw.point((ii,jj),fill=int(img_matrix[ii,jj]))
        img.save(filename)


    # def generate_image_(self, bit_matrix, width, filename):
    #     img = Image.new('1',(width,width),'white')
    #     drw = ImageDraw.Draw(img)
    #     pixel_width = int(width / len(bit_matrix))

    #     for ii in range(width):
    #         ii_index = ii // pixel_width 
    #         for jj in range(width):
    #             jj_index = jj // pixel_width 
                
    #             drw.point((ii,jj),fill=int(bit_matrix[ii_index,jj_index]))
    #     img.save(filename)

    






if __name__ == '__main__':
    QRgen('https://www.bilibili.com')