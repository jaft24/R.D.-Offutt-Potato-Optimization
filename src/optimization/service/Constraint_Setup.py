'''
Author(s): Alex Trujillo, Jaleta Tesgera, Pedro Ochoa
Date: 12/14/2023
'''

import pandas as pd
import numpy as np
from copy import deepcopy
from .Excel_Handler import Excel_Handler
from .Products import Product_Handler
from ..model.Constants import Excel_Columns, EXCEL_DEFAULT_EXTENSION, EXCEL_FILETYPE, Output_Dataframe_Columns as output
import pulp
from tkinter.filedialog import asksaveasfilename
'''
The way that this class will work is that it will have an rhs and constraint matrix

self.excelfile is an instance of the Excel_Handler class. This is NOT the dataframe, but an object that contains the pd.DataFrame
self.product will be an instance of a product.
self.rhs will be a list of values
self.constraints will be a list of lists

Class requirements:
1.  There must be a function for each constraint in our problem.
2.  The functions will set up the left hand side and the right hand sides from the excel data.
3.  The final outcome of each function should be using the .append() function to the self.constraints and self.rhs
    to append the new rhs and constraint to the initialized lists.
    
This class now inherits the properties of the Excel_Handler class which just means that there is now easier access
to the properties of the Excel_Handler. Now to access the excelfile's dataframe, you must use self.excelfile
'''
class Constraints(Excel_Handler):
    def __init__(self):
        super().__init__()
        self.cols = Excel_Columns()
        #empty right hand side and constraint matrix 
        self.currentProduct: pd.DataFrame
        self.rhs: list = []
        self.constraints: list[list] = []
        self.constraintDirection: list[str] = []
        self.objective: list = []
        self.constraintRowTemplate: list = [] #DO NOT USE THIS VARIABLE DIRECTLY GET A NEW CONSTRAINT ROW. USE THE COPY FACTORY. LISTS ARE MUTABLE IN PYTHON. USE: self.getConstraintRowTemplate() for each row.
        self.objectiveDirection = 'min'
        #this is a useful number: the sum of all available CWT
        self.totalAvailableWeight = np.sum(self.excelfile[self.cols.currentCWT])
        self.uniqueBins = list(self.excelfile[self.cols.destinationBinID].unique())
        self.numberOfLots = self.excelfile.shape[0]

        #EXAMLE PLACEHOLDER (WILL BE DELETE IN FINAL PROJECT)
        self.selectSingleProduct('BrandA', 150000)
        self.createObjective()
        #run the constraint functions below:
        
        #lot quality constraints
        self.percentSixOzConstraint()
        self.percentTenOzConstraint()
        self.bruiseFreeConstraint()
        self.hollowHeartConstraint()
        self.minGravityConstraint()
        self.maxGravityConstraint()
        self.fryColorConstraint()
        self.cornConstraint()
        #logistical constraints
        self.lineCapacityConstraint()
        self.fourLotsConstraint()
        self.oneBinPerStorageComplexConstraint()
        self.maxTruckloadConstraint()
        self.binTakenFromConstraint()
        #self.lotBlockingConstraint()
        
        
        self.beginLpLoop()


    def selectSingleProduct(self, productName: str, cwt: int):
        self.currentProduct = self.products.loc[self.products[self.productCols.name] == productName].reset_index(drop = True)
        self.currentProduct[self.productCols.requiredCWT] = [cwt]
        print(self.currentProduct)


    def createObjective(self):
        #the number of decision variables is 3*(number of lots) + (the number of bins)
        self.numberOfDecisionVariables = int((self.excelfile.shape[0] * 3) + len(self.excelfile[self.cols.destinationBinID].unique()))
        #initialize each variable's vector
        xVector = []
        yVector = []
        zVector = [0] * int(self.excelfile.shape[0])
        bVector = [0] * int(len(self.excelfile[self.cols.destinationBinID].unique()))
        #largest value of any lot
        largestLotValue = np.max(self.excelfile[self.cols.lotValue])
        #iterate through the lots to get each x and y
        for lotIndex, row in self.excelfile.iterrows():
            #Ci*Xi (Lot Value)i * (X)i
            currentLotValue = row[self.cols.lotValue]
            xVector.append(currentLotValue)

            currentRequiredCWT = self.currentProduct.at[0, self.productCols.requiredCWT]
                
            newYValue = largestLotValue * currentRequiredCWT * (1 - row[self.cols.penalty])
            
            yVector.append(newYValue)
        
        self.objective.extend(xVector)
        self.objective.extend(yVector)
        self.objective.extend(zVector)
        self.objective.extend(bVector)
        #creation of the constraintRowTemplate along with beginning indexes for x,y,z,b
        self.xDVs = 0 #beginning index of the x variables
        x = [0] * len(xVector)
        self.constraintRowTemplate.extend(x)
        self.yDVs = len(self.constraintRowTemplate) #beginning index of the y variables
        y = [0] * len(yVector) 
        self.constraintRowTemplate.extend(y)
        self.zDVs = len(self.constraintRowTemplate) #beginning index of the z variables
        z = [0] * len(zVector)
        self.xyzCount = len(x) #x,y,z vectors will all be the same length
        self.constraintRowTemplate.extend(z)
        b = [0] * len(bVector)
        self.bDVs = len(self.constraintRowTemplate) #beginning index of the b variables
        self.bCount = len(b) #b will be a different length than x, y, and z
        self.constraintRowTemplate.extend(b)

    #returns a copy of the constaint row template
    def getConstraintRowTemplate(self):
        return deepcopy(self.constraintRowTemplate)
    

    def percentSixOzConstraint(self):
        
        goal = self.currentProduct.at[0, self.productCols.sixOz]
        #the lot index we are starting at is the x decision variable
        lotIndex = self.xDVs
        
        for binIndex, binId in enumerate(self.uniqueBins):
            #get a copy of the constraintRowTemplate
            currentConstraintRow = self.getConstraintRowTemplate()
            #isolate the current bin's data
            binData = self.excelfile.loc[(self.excelfile[self.cols.destinationBinID] == binId)]
            
            #grab the six oz column
            currentSixOzCol = binData[self.cols.percentSixOz]
            #grab the bin's current cwt column
            currentCWTCol = binData[self.cols.currentCWT]
            #subtract goal from six oz column
            currentSixOzCol = np.subtract(currentSixOzCol, goal)
            #multiply by the cwt column
            currentSixOzCol = np.multiply(currentSixOzCol, currentCWTCol)
            #set the new values of the segment of the constraint row
            currentConstraintRow[lotIndex:len(currentSixOzCol)] = currentSixOzCol
            #add the rhs value for this row
            self.rhs.append(0)
            #add the direction for this row
            self.constraintDirection.append('>=')
            #add the constraint row to the contraint matrix
            self.constraints.append(currentConstraintRow)
            #increase the lot index to the next lot
            lotIndex += len(currentSixOzCol)
            

    
    def percentTenOzConstraint(self):
        
        goal = self.currentProduct.at[0, self.productCols.tenOz]
        #the lot index we are starting at is the x decision variable
        lotIndex = self.xDVs
        
        for binIndex, binId in enumerate(self.uniqueBins):
            #get a copy of the constraintRowTemplate
            currentConstraintRow = self.getConstraintRowTemplate()
            #isolate the current bin's data
            binData = self.excelfile.loc[(self.excelfile[self.cols.destinationBinID] == binId)]
            
            #grab the ten oz column
            currentTenOzCol = binData[self.cols.percentTenOz]
            #grab the bin's current cwt column
            currentCWTCol = binData[self.cols.currentCWT]
            #subtract goal from ten oz column
            currentTenOzCol = np.subtract(currentTenOzCol, goal)
            #multiply by the cwt column
            currentTenOzCol = np.multiply(currentTenOzCol, currentCWTCol)
            #set the new values of the segment of the constraint row
            currentConstraintRow[lotIndex:len(currentTenOzCol)] = currentTenOzCol
            #add the rhs value for this row
            self.rhs.append(0)
            #add the direction for this row
            self.constraintDirection.append('>=')
            #add the constraint row to the contraint matrix
            self.constraints.append(currentConstraintRow)
            #increase the lot index to the next lot
            lotIndex += len(currentTenOzCol)
            
            
        
        

    def bruiseFreeConstraint(self):
        
        goal = self.currentProduct.at[0, self.productCols.bruiseFree]
        #the lot index we are starting at is the x decision variable
        lotIndex = self.xDVs
        
        for binIndex, binId in enumerate(self.uniqueBins):
            #get a copy of the constraintRowTemplate
            currentConstraintRow = self.getConstraintRowTemplate()
            #isolate the current bin's data
            binData = self.excelfile.loc[(self.excelfile[self.cols.destinationBinID] == binId)]
            
            #grab the bruise free column
            currentBruiseFreeCol = binData[self.cols.percentBruiseFree]
            #grab the bin's current cwt column
            currentCWTCol = binData[self.cols.currentCWT]
            #subtract goal from  bruise free column
            currentBruiseFreeCol = np.subtract(currentBruiseFreeCol, goal)
            #multiply by the cwt column
            currentBruiseFreeCol = np.multiply(currentBruiseFreeCol, currentCWTCol)
            #set the new values of the segment of the constraint row
            currentConstraintRow[lotIndex:len(currentBruiseFreeCol)] = currentBruiseFreeCol
            #add the rhs value for this row
            self.rhs.append(0)
            #add the direction for this row
            self.constraintDirection.append('>=')
            #add the constraint row to the contraint matrix
            self.constraints.append(currentConstraintRow)
            #increase the lot index to the next lot
            lotIndex += len(currentBruiseFreeCol)
        
    
    def hollowHeartConstraint(self):
        
        goal = self.currentProduct.at[0, self.productCols.hollow]
        #the lot index we are starting at is the x decision variable
        lotIndex = self.xDVs
        
        for binIndex, binId in enumerate(self.uniqueBins):
            #get a copy of the constraintRowTemplate
            currentConstraintRow = self.getConstraintRowTemplate()
            #isolate the current bin's data
            binData = self.excelfile.loc[(self.excelfile[self.cols.destinationBinID] == binId)]
            
            #grab the hollow column
            currentHollowHeartCol = binData[self.cols.percentHollowHeart]
            #grab the bin's current cwt column
            currentCWTCol = binData[self.cols.currentCWT]
            #subtract goal from  hollow column
            currentHollowHeartCol = np.subtract(goal, currentHollowHeartCol)
            #multiply by the cwt column
            currentHollowHeartCol = np.multiply(currentHollowHeartCol, currentCWTCol)
            #set the new values of the segment of the constraint row
            currentConstraintRow[lotIndex:len(currentHollowHeartCol)] = currentHollowHeartCol
            #add the rhs value for this row
            self.rhs.append(0)
            #add the direction for this row
            self.constraintDirection.append('>=')
            #add the constraint row to the contraint matrix
            self.constraints.append(currentConstraintRow)
            #increase the lot index to the next lot
            lotIndex += len(currentHollowHeartCol)


    def minGravityConstraint(self):
        goal = self.currentProduct.at[0, self.productCols.minGravity]
        lotIndex = self.xDVs
        
        for binIndex, binId in enumerate(self.uniqueBins):
            currentConstraintRow = self.getConstraintRowTemplate()
            binData = self.excelfile.loc[(self.excelfile[self.cols.destinationBinID] == binId)]
            
            currentGravityCol = binData[self.cols.specificGravity]
            currentCWTCol = binData[self.cols.currentCWT]
            currentGravityCol = np.subtract(currentGravityCol, goal)
            currentGravityCol = np.multiply(currentGravityCol, currentCWTCol)
            currentConstraintRow[lotIndex:len(currentGravityCol)] = currentGravityCol
            self.rhs.append(0)
            self.constraintDirection.append('>=')
            self.constraints.append(currentConstraintRow)
            lotIndex += len(currentGravityCol)


    def maxGravityConstraint(self):
        goal = self.currentProduct.at[0, self.productCols.maxGravity]
        lotIndex = self.xDVs
        
        for binIndex, binId in enumerate(self.uniqueBins):
            currentConstraintRow = self.getConstraintRowTemplate()
            binData = self.excelfile.loc[(self.excelfile[self.cols.destinationBinID] == binId)]
            
            currentGravityCol = binData[self.cols.specificGravity]
            currentCWTCol = binData[self.cols.currentCWT]
            currentGravityCol = np.subtract(goal, currentGravityCol)
            currentGravityCol = np.multiply(currentGravityCol, currentCWTCol)
            currentConstraintRow[lotIndex:len(currentGravityCol)] = currentGravityCol
            self.rhs.append(0)
            self.constraintDirection.append('>=')
            self.constraints.append(currentConstraintRow)
            lotIndex += len(currentGravityCol)


    def fryColorConstraint(self):
        goal = self.currentProduct.at[0, self.productCols.fryColor]
        lotIndex = self.xDVs
        
        for binIndex, binId in enumerate(self.uniqueBins):
            currentConstraintRow = self.getConstraintRowTemplate()
            binData =self.excelfile.loc[(self.excelfile[self.cols.destinationBinID] == binId)]
            
            currentColorCol = binData[self.cols.blanchColorScore]
            currentCWTCol = binData[self.cols.currentCWT]
            currentColorCol = np.subtract(goal, currentColorCol)
            currentColorCol = np.multiply(currentColorCol, currentCWTCol)
            currentConstraintRow[lotIndex:len(currentColorCol)] = currentColorCol
            
            self.rhs.append(0)
            self.constraintDirection.append('>=')
            self.constraints.append(currentConstraintRow)
            lotIndex += len(currentColorCol)
            

    def cornConstraint(self):
        goal = self.currentProduct.at[0, self.productCols.corn]
        lotIndex = self.xDVs
        
        for binIndex, binId in enumerate(self.uniqueBins):
            currentConstraintRow = self.getConstraintRowTemplate()
            binData = self.excelfile.loc[(self.excelfile[self.cols.destinationBinID] == binId)]
            
            currentCornCol = binData[self.cols.cornPenaltyDollars]
            currentCWTCol = binData[self.cols.currentCWT]
            currentCornCol = np.subtract(goal, currentCornCol)
            currentCornCol = np.multiply(currentCornCol, currentCWTCol)
            currentConstraintRow[lotIndex:len(currentCornCol)] = currentCornCol
            
            self.rhs.append(0)
            self.constraintDirection.append('>=')
            self.constraints.append(currentConstraintRow)
            lotIndex += len(currentCornCol)
            
    #pull from at most 4 lots per day.
    def fourLotsConstraint(self):
        currentConstraintRow = self.getConstraintRowTemplate()
        binIndex = self.bDVs
        
        currentConstraintRow[binIndex:] = [1] * self.bCount
        self.rhs.append(4)
        self.constraintDirection.append('<=')
        self.constraints.append(currentConstraintRow)
        
        
    #only pull from one bin per storage complex
    def oneBinPerStorageComplexConstraint(self):
        uniqueStorageComplexes = self.excelfile[self.cols.storageComplexBin].unique()
        
        binIndex = self.bDVs
        for complexIndex, complexId in enumerate(uniqueStorageComplexes):
            currentConstraintRow = self.getConstraintRowTemplate()
            binData = self.excelfile.loc[(self.excelfile[self.cols.storageComplexBin] == complexId)]
            
            
            uniqueComplexBins = self.excelfile[self.cols.destinationBinID].unique()
            binCount = len(uniqueComplexBins)
            
            
            
            currentBinCol = binData[self.cols.destinationBinID]
            currentConstraintRow[binIndex:binCount] = [1] * binCount
            
            self.rhs.append(1)
            self.constraintDirection.append('<=')
            self.constraints.append(currentConstraintRow)
            
            binIndex += binCount
            
        
    def maxTruckloadConstraint(self):
        
        xIndex = self.xDVs
        yIndex = self.yDVs
        zIndex = self.zDVs
        
        for lotIndex, row in self.excelfile.iterrows():
            currentCWT = row[self.cols.currentCWT]
            #little m will either be 1000 or the current cwt, whatever is smaller
            m = np.min([currentCWT, 1000])
            #each lot gets 4 constraint rows for this constraint
            constA, constB, constC, constD = self.getConstraintRowTemplate(), self.getConstraintRowTemplate(), self.getConstraintRowTemplate(), self.getConstraintRowTemplate()
            #constraint A
            constA[xIndex] = 1
            constA[yIndex] = -m
            self.constraints.append(constA)
            self.rhs.append(0)
            self.constraintDirection.append('>=')
            #constraint B
            constB[xIndex] = 1
            constB[yIndex] = -currentCWT
            self.constraints.append(constB)
            self.rhs.append(0)
            self.constraintDirection.append('<=')
            #constraint C
            constC[xIndex] = 1
            constC[zIndex] = m
            self.constraints.append(constC)
            self.rhs.append(currentCWT)
            self.constraintDirection.append('<=')
            #constraint D
            constD[xIndex] = 1
            constD[zIndex] = currentCWT
            self.constraints.append(constD)
            self.rhs.append(currentCWT)
            self.constraintDirection.append('>=')
            #incrememnt the indicies so that they now refer to the next variable space
            xIndex += 1
            yIndex += 1
            zIndex += 1
            
    #is this bin taken from?        
    def binTakenFromConstraint(self):
        
        yIndex = self.yDVs
        bIndex = self.bDVs
        for i, binId in enumerate(self.uniqueBins):
            #data setup
            binData: pd.DataFrame = self.excelfile.loc[(self.excelfile[self.cols.destinationBinID] == binId)]
            currentConstraintRow = self.getConstraintRowTemplate()
            
            y = 1/binData.shape[0]
            currentConstraintRow[yIndex:binData.shape[0]] = [y] * binData.shape[0]
            currentConstraintRow[bIndex] = -1
            self.constraints.append(currentConstraintRow)
            self.constraintDirection.append('<=')
            self.rhs.append(0)
            
            yIndex += binData.shape[0]
            bIndex += 1
            
    # Block a lot from going past a lot that is not finished        
    def lotBlockingConstraint(self):
        
        yLotIndex = self.yDVs
        zlotIndex = self.zDVs
        
        
        for binId in self.uniqueBins:
            binData = self.excelfile.loc[(self.excelfile[self.cols.destinationBinID] == binId)]
            firstStackingOrder = binData[self.cols.stackingOrder].max()
            lastStackingOrder = binData[self.cols.stackingOrder].min()
            binEntranceCount = binData[self.cols.binEntranceCount].iloc[0]

            for lotInBinOrder in binData[self.cols.stackingOrder]:
                currentConstraintRow = self.getConstraintRowTemplate()
                goal = 0
                
                if binEntranceCount == 2:
                    if lotInBinOrder == firstStackingOrder or lotInBinOrder == lastStackingOrder:
                        yLotIndex += 1
                        zlotIndex += 1
                        continue 
                    else:
                        goal = 2
                        """
                        No need to check for exceeding constraints since the if statement
                        already handles that lots before y and after y (Z) are not corner lots 
                        same rules apply as we go down ↓
                        """
                        currentConstraintRow[yLotIndex] = 1
                        currentConstraintRow[zlotIndex - 1] = 1
                        currentConstraintRow[zlotIndex + 1] = 1
                        yLotIndex += 1
                        zlotIndex += 1
                elif binEntranceCount == 1:
                    if lotInBinOrder == firstStackingOrder:
                        yLotIndex += 1
                        zlotIndex += 1
                        continue
                    elif lotInBinOrder == lastStackingOrder:
                        goal = 1
                        currentConstraintRow[yLotIndex] = 1
                        """
                        for Every corner Y with no second door Z+1 does not exist
                        """
                        currentConstraintRow[zlotIndex + 1] = 1
                        yLotIndex += 1
                        zlotIndex += 1
                    else:
                        goal = 2
                        currentConstraintRow[yLotIndex] = 1
                        currentConstraintRow[zlotIndex - 1] = 1
                        currentConstraintRow[zlotIndex + 1] = 1
                        yLotIndex += 1
                        zlotIndex += 1
                else:
                    
                    yLotIndex += 1
                    zlotIndex += 1
                    continue

                self.constraints.append(currentConstraintRow)
                self.rhs.append(goal)
                self.constraintDirection.append('<=')
                #print(f"Lot Blocking Constraints - {currentConstraintRow} - <= - {goal} End")

    #for both lines
    def lineCapacityConstraint(self):
        #sum of line1 and line2 capacity
        goal = self.currentProduct.at[0, self.productCols.line1Capacity] + self.currentProduct.at[0, self.productCols.line2Capacity]
        
        goal = np.min([goal, self.currentProduct.at[0, self.productCols.requiredCWT]])
        
        currentConstraintRow = self.getConstraintRowTemplate()
        #the X DVs coefficient will be equal to one
        currentConstraintRow[:self.xyzCount] = [1] * self.xyzCount
        
        #append the constraint
        self.constraints.append(currentConstraintRow)
        self.rhs.append(goal)
        self.constraintDirection.append('>=')

    #reinitializes the constraints
    def reinitConstraints(self):
        self.rhs: list = []
        self.constraints: list[list] = []
        self.constraintDirection: list[str] = []
        self.objective: list = []
        self.constraintRowTemplate: list = [] #DO NOT USE THIS VARIABLE DIRECTLY GET A NEW CONSTRAINT ROW. USE THE COPY FACTORY. LISTS ARE MUTABLE IN PYTHON. USE: self.getConstraintRowTemplate() for each row.
        
        self.totalAvailableWeight = np.sum(self.excelfile[self.cols.currentCWT])
        self.uniqueBins = list(self.excelfile[self.cols.destinationBinID].unique())
        self.numberOfLots = self.excelfile.shape[0]
        
        self.createObjective()
        #run the constraint functions below:
        
        #lot quality constraints
        self.percentSixOzConstraint()
        self.percentTenOzConstraint()
        self.bruiseFreeConstraint()
        self.hollowHeartConstraint()
        self.minGravityConstraint()
        self.maxGravityConstraint()
        self.fryColorConstraint()
        self.cornConstraint()
        #logistical constraints
        self.lineCapacityConstraint()
        self.fourLotsConstraint()
        self.oneBinPerStorageComplexConstraint()
        self.maxTruckloadConstraint()
        self.binTakenFromConstraint()
        #self.lotBlockingConstraint()            

    
        
        

    #keep this function last:
    def beginLpLoop(self):
        
        days = 0
        outputDataFrame = {output.day: [], output.complexPin: [], output.binId: [], output.stackingOrderNumber: [], output.loadOutCWT: []}
        
        while self.currentProduct.at[0, self.productCols.requiredCWT] > 0:
            
            #lp is our instance of the lp
            lp = pulp.LpProblem('Select_Lots', pulp.LpMinimize)
            #create the 4 categories of decision variables: x, y, z, and b
            xDecisionVars = {f'x{i}': pulp.LpVariable(f'x{i}', lowBound=0, cat=pulp.LpInteger) for i in range(self.xyzCount)}
            yDecisionVars = {f'y{i}': pulp.LpVariable(f'y{i}', lowBound=0, cat=pulp.LpBinary) for i in range(self.xyzCount)}
            zDecisionVars = {f'z{i}': pulp.LpVariable(f'z{i}', lowBound=0, cat=pulp.LpBinary) for i in range(self.xyzCount)}
            bDecisionVars = {f'b{i}': pulp.LpVariable(f'b{i}', lowBound=0, cat=pulp.LpBinary) for i in range(self.bCount)}
            #each gets its own dict until we paste them together
            decisionVars = {**xDecisionVars, **yDecisionVars, **zDecisionVars, **bDecisionVars}
            
            for constraint, direction, rhs in zip(self.constraints, self.constraintDirection, self.rhs):
                #create constraints
                constraintExpr = pulp.lpSum(constraint[i] * decisionVars[f'x{i}'] for i in range(self.xyzCount))
                constraintExpr += pulp.lpSum(constraint[i + self.xyzCount] * decisionVars[f'y{i}'] for i in range(self.xyzCount))
                constraintExpr += pulp.lpSum(constraint[i + int(2 * self.xyzCount)] * decisionVars[f'z{i}'] for i in range(self.xyzCount))
                constraintExpr += pulp.lpSum(constraint[i + int(3 * self.xyzCount)] * decisionVars[f'b{i}'] for i in range(self.bCount))
                
                if direction == '>=':
                    lp += (constraintExpr >= rhs)
                elif direction == '<=':
                    lp += (constraintExpr <= rhs)
                elif direction == '==':
                    lp += (constraintExpr == rhs)
            
            #create objective expression
            objectiveExpr = pulp.lpSum(self.objective[i] * decisionVars[f'x{i}'] for i in range(self.xyzCount))
            objectiveExpr += pulp.lpSum(self.objective[i + self.xyzCount] * decisionVars[f'y{i}'] for i in range(self.xyzCount))
            objectiveExpr += pulp.lpSum(self.objective[i + int(2 * self.xyzCount)] * decisionVars[f'z{i}'] for i in range(self.xyzCount))
            objectiveExpr += pulp.lpSum(self.objective[i + int(3 * self.xyzCount)] * decisionVars[f'b{i}'] for i in range(self.bCount))
            
            lp += objectiveExpr
            
            
            
            
            lp.solve()
            status = pulp.LpStatus[lp.status]
            print("Solution Status:", status)

            # Fetch the solution if optimal
            print(f'\n{self.currentProduct.at[0,self.productCols.requiredCWT]}\n')
            if status == 'Optimal':
                
                
                
                xObjVars = [dv for dv in lp.variables() if ('x' in dv.name and dv.varValue > 0)]
                #reset the index of the dataframe
                self.excelfile = self.excelfile.reset_index(drop = True)
                
                for xVar in xObjVars:
                    cwtTaken = xVar.varValue
                    varName: str = xVar.name
                    lotIndex = int(varName.replace('x',''))
                    print(f'------------\n{varName}: {cwtTaken}CWT\n------------')
                    
                    #self.excelfile.at[lotIndex, self.cols.currentCWT] -= cwtTaken
                    
                    #loadoutCWT may have missing values
                    if pd.isna(self.excelfile.at[lotIndex, self.cols.loadOutCWT]):
                        self.excelfile.at[lotIndex, self.cols.loadOutCWT] = cwtTaken
                    else:
                        self.excelfile.at[lotIndex, self.cols.loadOutCWT] += cwtTaken
                    
                    self.currentProduct.at[0, self.productCols.requiredCWT] -= cwtTaken
                    
                    binId = self.excelfile.at[lotIndex, self.cols.destinationBinID]
                    complexPIN = self.excelfile.at[lotIndex, self.cols.storageComplexBin]
                    stackingOrderNumber = self.excelfile.at[lotIndex, self.cols.stackingOrder]
                    
                    outputDataFrame[output.day].append(days)
                    outputDataFrame[output.complexPin].append(complexPIN)
                    outputDataFrame[output.binId].append(binId)
                    outputDataFrame[output.stackingOrderNumber].append(stackingOrderNumber)
                    outputDataFrame[output.loadOutCWT].append(cwtTaken)
                    

                
                
            days += 1 
            
            #reinitialize the dataframe setup on the current dataframe.
            self.reInitExcelfile()
            self.reinitConstraints()
        
        outputDataFrame = pd.DataFrame(outputDataFrame)
        print(outputDataFrame)
        
        outputSavepath = asksaveasfilename(filetypes=EXCEL_FILETYPE, defaultextension=EXCEL_DEFAULT_EXTENSION)
        if outputSavepath != '':
            with pd.ExcelWriter(outputSavepath) as writer:
                outputDataFrame.to_excel(writer)
        else:
            print('No file output selected.')
            
            