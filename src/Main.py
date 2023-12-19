'''
Author(s): Alex Trujillo, Jaleta Tesgera, Pedro Ochoa
Date: 12/14/2023
'''
#main file
from optimization.service.Constraint_Setup import Constraints
from time import time

if __name__ == '__main__':
    begin = time()
    test = Constraints()
    
    
    print(f'Total Runtime: {time() - begin} seconds')
    