'''
Author(s): Alex Trujillo
Date: 12/14/2023
'''
from datetime import datetime
import pandas as pd
import numpy as np
from ..model.Constants import Excel_Columns


cols = Excel_Columns()

'''
All of these functions will get the existing penalty column, create the additional penalty, and add the additional penalty to the existing penalty.
They will then return the excel that was input so that the syntax of applying the penalties to the excelfile attribute of the excel_handler class will be:
excel_handler.excelfile = penaltyFunction(excel_handler.excelfile)

I understand that iterrows may not be the fastest operation for iterating through a dataframe, but these dataframes will not be large enough for speed to be a concern.
'''
#clamp a value between a range of values
def clamp(value, lower = 0.0, upper = 1.0):
    if value > upper:
        return upper
    elif value < lower:
        return lower
    else:
        return value

#eliminate the weight unusable from the weight of the lot
def weightUnusablePenalty(excel: pd.DataFrame):
    #iterate through rows in excel
    for lotIndex, row in excel.iterrows():
        #penalty scalar of 1 means that the lot is good
        penaltyScalar = 1.0
        #subtract the percent unusable from the penalty scalar
        penaltyScalar -= row[cols.percentUnusable]
        #reduce the penalty by the penalty scalar
        excel.at[lotIndex, cols.penalty] *= penaltyScalar
    return excel

#penalization from bins being open
def openBinPenalty(excel: pd.DataFrame):
    #This penalty decrease the lot value exponentially on a scale of 1.0 - 0.0
    penalty = 1.0
    #grab the current value column
    valueColumn = list(excel[cols.lotValue])
    
    #the difference between listIndex and dfIndex is that list index goes from 0-length of the value column while the dfIndex may skip some values
    for listIndex, (dfIndex, row) in enumerate(excel.iterrows()):
        
        pctCwtRemaining = row[cols.totalBinPctLeft]
        #if the bin is closed there is no penalty. If it is opened, then the penalty will apply
        if row[cols.isOpenedBin] == 1:
            penalty = (2**pctCwtRemaining) - 1
        else:
            penalty = 1
        
        valueColumn[listIndex] *= penalty
        
        #print(f'{listIndex}: {pctCwtRemaining}  {penalty}   {valueColumn[listIndex]}')
        
    excel[cols.lotValue] = valueColumn
    return excel

#penalization from lots being compromised
def compromisedLotPenalty(excel: pd.DataFrame):
    for lotIndex, row in excel.iterrows():
        penaltyScalar = 1.0
        #if the lot is compromised, reduce the value by up to 25% (severity is on a scale of 0-3 with 1 being worst)
        if row[cols.isCompromisedLot] == 1:
            severity = row[cols.severity]
            #if 1: value decreases 75%, if 2: value decreases 50%, if 3: value decreases 25% (penalty scalar is redundant here)
            excel.at[lotIndex, cols.penalty] *= (0.25 * severity)
        #no need for an else because multiplying by 1 does nothing
    return excel


#penalization for if a lot is blocking a compromised lot
def blockingPenalty(excel: pd.DataFrame):
    #find the bins which have compromised lots
    binIDsWithCompromisedLots: list[tuple] = []
    for lotIndex, row in excel.iterrows():
        if row[cols.isCompromisedLot] == 1:
            #list of tuples where [0]: lot index, [1]: binID
            binIDsWithCompromisedLots.append((lotIndex ,row[cols.destinationBinID]))
            
    #iterate through binIDs with compromised lots
    for compromisedLotIndex, binID in binIDsWithCompromisedLots:
        #the bin that contains the current compromised lot
        compromisedBin: pd.DataFrame = excel.loc[(excel[cols.destinationBinID] == binID)]
        #overall stacking order of the current compromised bin
        stackingOrderVector = compromisedBin[cols.stackingOrder]
        #the stacking index of the compromised lot itself
        compromisedLotStackingIndex = compromisedBin.at[compromisedLotIndex, cols.stackingOrder]
        #pull the bin entance count
        binEntranceCount = compromisedBin.at[compromisedLotIndex, cols.binEntranceCount]

        #this is the penalty of the currently compromised lot
        currentCompromisedLotPenalty = compromisedBin.at[compromisedLotIndex, cols.severity] * 0.25
        #for if there is 1 entrance
        if binEntranceCount == 1:
            blockingLots: pd.DataFrame = compromisedBin.loc[compromisedBin[cols.stackingOrder] < compromisedLotStackingIndex]
            for blockingLotIndex, row in blockingLots.iterrows():
                penaltyToApply = 1 - (row[cols.currentCWT] / (np.sum(blockingLots[cols.currentCWT])) * 0.25 * currentCompromisedLotPenalty)
                #apply penalty to lots that are blocking the compromised lot
                excel.at[blockingLotIndex, cols.penalty] *= penaltyToApply
        elif binEntranceCount == 2:
            #there could be lots blocking on either side
            entranceOneBlockingLots: pd.DataFrame = compromisedBin.loc[compromisedBin[cols.stackingOrder] < compromisedLotStackingIndex]
            entranceTwoBlockingLots: pd.DataFrame = compromisedBin.loc[compromisedBin[cols.stackingOrder] > compromisedLotStackingIndex]
            
            #apply penalty to lots on either side
            for blockingLotIndex, row in entranceOneBlockingLots.iterrows():
                penaltyToApply = 1 - (row[cols.currentCWT] / (np.sum(blockingLots[cols.currentCWT])) * 0.25 * currentCompromisedLotPenalty)
                excel.at[blockingLotIndex, cols.penalty] *= penaltyToApply
                
            for blockingLotIndex, row in entranceTwoBlockingLots.iterrows():
                penaltyToApply = 1 - (row[cols.currentCWT] / (np.sum(blockingLots[cols.currentCWT])) * 0.25 * currentCompromisedLotPenalty)
                excel.at[blockingLotIndex, cols.penalty] *= penaltyToApply
                
        return excel
        
        
        
        


#penalty on the variety of the lot, scaleDown means reducing the overall value to by a number from 0-1 for variety 2. Otherwise if it is false variety 2 lots will have a value directly subtracted from their value
def varietyPenalty(excel: pd.DataFrame, scaleDown: bool, toSubtract = 1, toScale = 0.25):
    if scaleDown == True:
        for lotIndex, row in excel.iterrows():
            if row[cols.varietyID] == 2:
                excel.at[lotIndex, cols.penalty] *= toScale
    else:
        for lotIndex, row in excel.iterrows():
            if row[cols.varietyID] == 2:
                excel.at[lotIndex, cols.penalty] -= toSubtract
    return excel

#returns the number of days its been since the previous october 1st
def getDaysSinceOct1st():
    now = datetime.now()
    oct1stThisYear = datetime(now.year, 10, 1)
    if now < oct1stThisYear:
        oct1stLastYear = datetime(now.year - 1, 10, 1)
        daysSinceOct1st = (now - oct1stLastYear).days
        return daysSinceOct1st
    else:
        daysSinceOct1st = (now - oct1stThisYear).days
        return daysSinceOct1st

#penalty on the storage term of the lot
def shortTermPenalty(excel: pd.DataFrame, intensity: int = 100):
    daysSinceOct1st = getDaysSinceOct1st()
    for lotIndex, row in excel.iterrows():
        if row[cols.isShortTermStorage] == 1:
            #subtracts (daysSinceOct1st / intensity) from the penalty
            excel.at[lotIndex, cols.penalty] = clamp((excel.at[lotIndex, cols.penalty] - (daysSinceOct1st/intensity)), 0.0, 1.0 )
    return excel

#just a double check that the penalty column is between 0 and 1 in case there is some weird numbers in the excels
def clampPenaltyColumn(excel: pd.DataFrame, lowerBound = 0.0, upperBound = 1.0):
    penaltyCol = excel[cols.penalty]
    [clamp(x, lowerBound, upperBound) for x in penaltyCol]
    excel[cols.penalty] = penaltyCol
    return excel

