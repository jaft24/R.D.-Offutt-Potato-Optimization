'''
Author(s): Alex Trujillo
Date: 12/14/2023
'''
import pandas as pd
import numpy as np

from ..model.Constants import EXCEL_DEFAULT_EXTENSION, EXCEL_FILETYPE, Excel_Columns, Json_Strings as jstr
from tkinter.filedialog import askopenfilename, asksaveasfilename
from .Penalty import weightUnusablePenalty, openBinPenalty, compromisedLotPenalty, blockingPenalty, varietyPenalty, shortTermPenalty, clampPenaltyColumn
from .Products import Product_Handler

class Excel_Handler(Product_Handler):

    def __init__(self, importExcelFile = True) -> None:
        super().__init__() #initialize the superclass

        self.excelfile: pd.DataFrame
        self.cols: Excel_Columns = Excel_Columns()

        #importation of excel
        if importExcelFile:
            self.importExcel()

        #data formatting
        self.handleNan()
        self.getCurrentWeightAndPcts()
        self.getTotalBinCWT()
        self.getPercentOfCapacityLeft()
        
        
        
        self.filterEmptyLots()
        self.filterNAQualities()
        self.createLotPenaltyColumn()
        self.createValueColumn()
        
        #penalization functions
        self.excelfile = weightUnusablePenalty(self.excelfile)
        self.excelfile = openBinPenalty(self.excelfile)
        self.excelfile = compromisedLotPenalty(self.excelfile)
        self.excelfile = blockingPenalty(self.excelfile)
        self.excelfile = varietyPenalty(self.excelfile, scaleDown = True, toSubtract=1, toScale=0.25)
        self.excelfile = shortTermPenalty(self.excelfile, intensity=100) #can modify how quickly this will reduce the value. lower intensity means faster decline.
        #self.excelfile = clampPenaltyColumn(self.excelfile) #may not need this

        


    def importExcel(self):
        filepath = askopenfilename(filetypes = EXCEL_FILETYPE)
        self.excelfile = pd.read_excel(filepath)


    def saveExcel(self): 
        savepath = asksaveasfilename(filetypes = EXCEL_FILETYPE,
                                     defaultextension = EXCEL_DEFAULT_EXTENSION)
        if savepath != '':
            with pd.ExcelWriter(savepath) as writer:
                self.excelfile.to_excel(writer)
            
            
    def handleNan(self):
        self.excelfile[self.cols.loadOutCWT] = self.excelfile[self.cols.loadOutCWT].fillna(0)


    def getCurrentWeightColumn(self):
        self.excelfile[self.cols.currentCWT] = np.subtract(self.excelfile[self.cols.loadInCWT], self.excelfile[self.cols.loadOutCWT])


    def getCurrentWeightAndPcts(self):
        self.excelfile[self.cols.currentCWT] = np.subtract(self.excelfile[self.cols.loadInCWT], self.excelfile[self.cols.loadOutCWT])
        self.excelfile[self.cols.percentCWTLeft] = np.divide(self.excelfile[self.cols.loadOutCWT], self.excelfile[self.cols.loadInCWT])
           
        
    def getTotalBinCWT(self):
        #gets a list of the unique bin ids
        uniqueBins = self.excelfile[self.cols.destinationBinID].unique()
        
        #initialize temporary list that will be used as the binCWT column
        binCWT = []
        
        #loop through each unique bin id
        for i, binID in enumerate(uniqueBins):

            #isolate the current bin as well as the number of lots (length)
            currentBin: pd.DataFrame = self.excelfile.loc[self.excelfile[self.cols.destinationBinID] == binID]
            length = currentBin.shape[0]
            
            currentBinCWT = np.sum(currentBin[self.cols.currentCWT])
            
            binCWT.extend([currentBinCWT]*length)
            
        self.excelfile[self.cols.totalBinCWT] = binCWT    


    def getPercentOfCapacityLeft(self):
        self.excelfile[self.cols.totalBinPctLeft] = [self.clamp(x, 0.0, 1.0) for x in np.divide(self.excelfile[self.cols.totalBinCWT],self.excelfile[self.cols.binCapacityCWT])]
            

    #filters empty lots out of the dataframe
    def filterEmptyLots(self):
        self.excelfile = self.excelfile.loc[self.excelfile[self.cols.currentCWT] != 0.0]

    def filterNAQualities(self):
        removalIndexes = []
        for lotIndex, row in self.excelfile.iterrows():
            if pd.isna(row[self.cols.percentSixOz]):
                removalIndexes.append(lotIndex)
                continue
            elif pd.isna(row[self.cols.percentTenOz]):
                removalIndexes.append(lotIndex)
                continue
            elif pd.isna(row[self.cols.percentBruiseFree]):
                removalIndexes.append(lotIndex)
                continue
            elif pd.isna(row[self.cols.percentHollowHeart]):
                removalIndexes.append(lotIndex)
                continue
            elif pd.isna(row[self.cols.specificGravity]):
                removalIndexes.append(lotIndex)
                continue
            elif pd.isna(row[self.cols.blanchColorScore]):
                removalIndexes.append(lotIndex)
                continue
            elif pd.isna(row[self.cols.cornPenaltyDollars]):
                removalIndexes.append(lotIndex)
                continue
        self.excelfile.drop(index=removalIndexes, inplace=True)

    def getSdParamColumn(self, param: str):
        constraintCol = []
        if param == "percentSixOz":
            constraintCol = self.excelfile[self.cols.percentSixOz].tolist()
        elif param == "percentTenOz":
            constraintCol = self.excelfile[self.cols.percentTenOz].tolist()
        elif param == "percentBruiseFree":
            constraintCol = self.excelfile[self.cols.percentBruiseFree].tolist()
        elif param == "percentHollowHeart":
            constraintCol = self.excelfile[self.cols.percentHollowHeart].tolist()
        elif param == "specificGravity":
            constraintCol = self.excelfile[self.cols.specificGravity].tolist()
        elif param == "blanchColorScore":
            constraintCol = self.excelfile[self.cols.blanchColorScore].tolist()
        elif param == "cornPenaltyDollars":
            constraintCol = self.excelfile[self.cols.cornPenaltyDollars].tolist()
        else:
            print("Error: Invalid Constraint")
            return None
        finalConstraintCol = [x for x in constraintCol if not pd.isna(x)]
        sd = np.std(finalConstraintCol)
            
        return sd

    def createValueColumn(self):
        #Create a valuation method for each lot 
        valueColumn = []
        #will be used to store the index of the bins that should be removed because of a lack of metric data
        binsToRemove = []
        
        for binIndex, binRow in self.excelfile.iterrows():
            #binRow will use self.cols for its column name accessing.
            
            #the lot value will iterate by 1 for each constraint in each product passed
            value = 0.0
            makableProducts = 0
            for productIndex, productRow in self.products.iterrows():
                #productRow will use jstr for its column name accessing.

                param = [self.cols.percentSixOz, self.cols.percentTenOz, self.cols.percentBruiseFree, self.cols.percentHollowHeart, self.cols.specificGravity, self.cols.blanchColorScore, self.cols.cornPenaltyDollars]
                    
                if any(pd.isna(binRow[currentValue]) for currentValue in param):
                    binsToRemove.append(binIndex)
                    continue

                #six oz valuation
                value += ((binRow[self.cols.percentSixOz] - productRow[jstr.sixOz]) / self.getSdParamColumn("percentSixOz"))

                #ten oz valuation
                
                value += ((binRow[self.cols.percentTenOz] - productRow[jstr.tenOz]) / self.getSdParamColumn("percentTenOz"))
                
                #bruise free valuation
                
                value += ((productRow[jstr.bruiseFree] - binRow[self.cols.percentBruiseFree]) / self.getSdParamColumn("percentBruiseFree") )

                 #percent hollow heart valuation
                 
                value +=  ((binRow[self.cols.percentHollowHeart] - productRow[jstr.hollow]) / self.getSdParamColumn("percentHollowHeart")) 

                #minimum gravity valuation
                
                value += ((binRow[self.cols.specificGravity] - productRow[jstr.minGravity]) / self.getSdParamColumn("specificGravity"))
                
                #maximum gravity valuation
                
                value += ((productRow[jstr.maxGravity] - binRow[self.cols.specificGravity]) / self.getSdParamColumn("specificGravity"))

                #fry color valuation
                
                value += ((productRow[jstr.fryColor] - binRow[self.cols.blanchColorScore]) / self.getSdParamColumn("blanchColorScore"))
                
                #corn valuation
                
                #value += ((productRow[jstr.corn] - binRow[self.cols.cornPenaltyDollars]) / self.getSdParamColumn("cornPenaltyDollars"))
                

            valueColumn.append(round(value,2))
        
        self.excelfile[self.cols.lotValue] = valueColumn
        #drops bins with no metric data
        self.excelfile.drop(binsToRemove, inplace = True)

    #creating a column for lot penalty
    def createLotPenaltyColumn(self):
        self.excelfile[self.cols.penalty] = [1.0]*self.excelfile.shape[0]
        
        
    def clamp(self, value, lower, upper):
        if value < lower:
            return lower
        elif value > upper:
            return upper
        else:
            return value

    #for multiple iterations of the lp
    def reInitExcelfile(self):
        #data formatting
        self.excelfile = self.excelfile[self.cols.baseColumns] #reset the dataframe to the original base columns
        print(self.excelfile)
        #self.handleNan()
        self.getCurrentWeightAndPcts()
        self.getTotalBinCWT()
        self.getPercentOfCapacityLeft()
        
        self.filterEmptyLots()

        self.createLotPenaltyColumn()
        #self.createValueColumn()
        
        #penalization functions
        self.excelfile = weightUnusablePenalty(self.excelfile)
        self.excelfile = openBinPenalty(self.excelfile)
        self.excelfile = compromisedLotPenalty(self.excelfile)
        self.excelfile = blockingPenalty(self.excelfile)
        self.excelfile = varietyPenalty(self.excelfile, scaleDown = True, toSubtract=1, toScale=0.25)
        self.excelfile = shortTermPenalty(self.excelfile, intensity=100) #can modify how quickly this will reduce the value. lower intensity means faster decline.
        #self.excelfile = clampPenaltyColumn(self.excelfile) #may not need this