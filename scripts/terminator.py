import standard 

def get_terminator(data_len,version,error_correction_level):
    max_data_len = standard.get_maximum_number_of_encoding_bits(version,error_correction_level)
    remaining_nbits = max_data_len - data_len 
    terminator = ''
    terminator_format = standard.get_terminator_format()

    # Zero padding 
    if remaining_nbits <= len(terminator_format):
        terminator += terminator_format[:remaining_nbits]
    else:
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
    

