import numpy as np 

finder_pattern = np.array(
    [[0,0,0,0,0,0,0],
     [0,1,1,1,1,1,0],
     [0,1,0,0,0,1,0],
     [0,1,0,0,0,1,0],
     [0,1,0,0,0,1,0],
     [0,1,1,1,1,1,0],
     [0,0,0,0,0,0,0]]
)

alignment_pattern = np.array(
    [[0,0,0,0,0],
     [0,1,1,1,0],
     [0,1,0,1,0],
     [0,1,1,1,0],
     [0,0,0,0,0]]
)

def get_coordinates_of_alignment_pattern(version):
    row_column_coordinates_dict = {
        1:[],
        2:[6,18],
        3:[6,22],
        4:[6,26],
        5:[6,30,],
        6:[6,34],
        7:[6,22,38],
        8:[6,24,42],
        9:[6,26,46],
        10:[6,28,50],
        11:[6,30,54],
        12:[6,32,58],
        13:[6,34,62],
        14:[6,26,46,66],
        15:[6,26,48,70],
        16:[6,30,50,74],
        17:[6,30,54,78],
        18:[6,30,56,82],
        19:[6,30,58,86],
        20:[6,34,62,90],
    }

    row_column_coordinates = row_column_coordinates_dict[version]
    coordinates = []
    coordinates_number = len(row_column_coordinates)
    for ii in range(coordinates_number):
        for jj in range(coordinates_number):
            if not ((ii==0 and jj==0) or (ii==0 and jj==coordinates_number-1) or (ii==coordinates_number-1 and jj==0)):
                coordinates.append([row_column_coordinates[ii],row_column_coordinates[jj]])
    return coordinates
