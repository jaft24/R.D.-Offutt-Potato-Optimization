#this file will eventually be deleted, just using it to store the original product descriptions that were provided.
class Label(): 
    def __init__(self) -> None: 
        pass 

class XLSteak(Label): 
    def __init__(self): 
        self.name = 'XLSteak' 
        self.Line1Capacity = 24000 
        self.Line2Capacity = 10000 
        self.sixoz = 0.55 
        self.tenoz = 0.2 
        self.bruise_free = 0.88 
        self.hollow = 0.01 
        self.min_gravity = 1.08 
        self.max_gravity = 1.999 
        self.fry_color = 3 
        self.corn = 10.0 
         
class StraitCutNoPeel(Label): 
    def __init__(self): 
        self.name = 'StraitCutNoPeel'
        self.Line1Capacity = 24000 
        self.Line2Capacity = 10000 
        self.sixoz = 0.5 
        self.tenoz = 0.15 
        self.bruise_free = 0.75 
        self.hollow = 0.02 
        self.min_gravity = 1.078 
        self.max_gravity = 1.999 
        self.fry_color = 4 
        self.corn = 10.0 
 
class SkinnyFA(Label): 
    def __init__(self): 
        self.name = 'SkinnyFA'
        self.Line1Capacity = 24000 
        self.Line2Capacity = 10000 
        self.sixoz = 0.4      
        self.tenoz = 0.0 
        self.bruise_free = 0.0 
        self.hollow = 1.0 
        self.min_gravity = 1.078 
        self.max_gravity = 1.999 
        self.fry_color = 99  
        self.corn = 10.0 
 
class StraitCutWithPeel(Label): 
    def __init__(self): 
        self.name = 'StraitCutWithPeel'
        self.Line1Capacity = 24000 
        self.Line2Capacity = 10000 
        self.sixoz = 0.5 
        self.tenoz = 0.15 
        self.bruise_free = 0.65 
        self.hollow = 0.05 
        self.min_gravity = 1.078 
        self.max_gravity = 1.999 
        self.fry_color = 8 
        self.corn = 10.0 

class BrandA(Label): 
    def __init__(self): 
        self.name = 'BrandA'
        self.Line1Capacity = 24000 
        self.Line2Capacity = 10000 
        self.sixoz = 0.5 
        self.tenoz = 0.1 
        self.bruise_free = 0.8 
        self.hollow = 0.06 
        self.min_gravity = 1.084 
        self.max_gravity = 1.095 
        self.fry_color = 6 
        self.corn = 10.0 
 
class HalfInchCrinkleXL(Label): 
    def __init__(self):
        self.name = 'HalfInchCrinkleXL' 
        self.Line1Capacity = 28000 
        self.Line2Capacity = 16000 
        self.sixoz = 0.6 
        self.tenoz = 0.20 
        self.bruise_free = 0.75 
        self.hollow = 0.03 
        self.min_gravity = 1.074 
        self.max_gravity = 1.999 
        self.fry_color = 12 
        self.corn = 0.0 
 
class HalfInchCrinkleFA(Label): 
    def __init__(self): 
        self.name = 'HalfInchCrinkleFA'
        self.Line1Capacity = 24000 
        self.Line2Capacity = 10000 
        self.sixoz = 0.5 
        self.tenoz = 0.0 
        self.bruise_free = 0.0 
        self.hollow = 1.0 
        self.min_gravity = 1.0 
        self.max_gravity = 2.0 
        self.fry_color = 100 
        self.corn = 0.0 
 
class BrandBatter(Label): 
    def __init__(self): 
        self.name = 'BrandBatter'
        self.Line1Capacity = 20000 
        self.Line2Capacity = 0 
        self.sixoz = 0.5 
        self.tenoz = 0.1 
        self.bruise_free = 0.65 
        self.hollow = 0.2 
        self.min_gravity = 1.073 
        self.max_gravity = 1.094 
        self.fry_color = 10 
        self.corn = 10.0 
 
   
class Chips(Label): 
    def __init__(self): 
        self.name = 'Chips'
        self.Line1Capacity = 0 
        self.Line2Capacity = 7000 
        self.sixoz = 0.0 
        self.tenoz = 0.0 
        self.bruise_free = 0.8 
        self.hollow = 1.0 
        self.min_gravity = 1.09 
        self.max_gravity = 2.0 
        self.fry_color = 15    
        self.corn = 10.0 
   
 
class Ovens(Label): 
    def __init__(self): 
        self.name = 'Ovens'
        self.Line1Capacity = 24000 
        self.Line2Capacity = 10000 
        self.sixoz = 0.0 
        self.tenoz = 0.0 
        self.bruise_free = 0.8 
        self.hollow = 0.04 
        self.min_gravity = 0 
        self.max_gravity = 1.999 
        self.fry_color = 100  
        self.corn = 10.0 
 
class Flats(Label): 
    def __init__(self): 
        self.name = 'Flats'
        self.Line1Capacity = 0 
        self.Line2Capacity = 8000 
        self.sixoz = 0.0 
        self.tenoz = 0.0 
        self.bruise_free = 0.0 
        self.hollow = 0.00 
        self.min_gravity = 1.08 
        self.max_gravity = 1.999 
        self.fry_color = 8  
        self.corn = 0.0

