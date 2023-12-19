'''
Author(s): Alex Trujillo, Jaleta Tesgera, Pedro Ochoa
Date: 12/14/2023
'''
#this class will be a superclass of the Excel_Handler class. Its attributes will be inherited.
import json
import os
from ..model.Constants import Json_Strings as jst
import pandas as pd


class Product_Handler:
    def __init__(self) -> None:
        self.productCols = jst
        jsonPath = os.path.join(os.path.dirname(os.path.abspath(__file__))).replace('service','data/Products.json')
        self.filepath = jsonPath
        self.readJson()
        self.populateDataframe()
        print(self.products)


    #reads in our product json
    def readJson(self):
        self.jsonFile = None
        with open(self.filepath, 'r') as reader:
            self.jsonFile = json.load(reader)
        #the list of products
        self.products = self.jsonFile[jst.products]
        
    #creates a dataframe out of the loaded json
    def populateDataframe(self):
        constraintsList = []
        for i, product in enumerate(self.products):
            productName = product[jst.name]
            constraints = product[jst.constraints]
            constraints['name'] = productName
            constraintsList.append(constraints)
        self.products = pd.DataFrame(constraintsList)
        
    #call this function if a new product is added or removed during runtime
    def refreshProducts(self):
        self.readJson()
        self.populateDataframe()
