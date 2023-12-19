'''
Author(s): Alex Trujillo
Date: 12/14/2023
'''
from dataclasses import dataclass

#file types and extensions
EXCEL_FILETYPE = [('xlsx file type', '*.xlsx')]
EXCEL_DEFAULT_EXTENSION = '*.xslx'

#dataclass with expected excel column names for use in excel data formatting
@dataclass
class Excel_Columns:
    #base columns:
    storageComplexBin:              str = 'StorageComplexPIN'
    destinationBinID:               str = 'DestinationBinID'
    binEntranceCount:               str = 'BinEntranceCount'
    isShortTermStorage:             str = 'isShortTermStorage'
    isOpenedBin:                    str = 'isOpenedBin'
    isCompromisedLot:               str = 'isCompromisedLot'
    severity:                       str = 'Severity'
    stackingOrder:                  str = 'StackingOrder'
    sourceFieldInteger:             str = 'SourceFieldInteger'
    varietyID:                      str = 'VarietyID'
    loadInDate:                     str = 'LoadInDate'
    percentUSDANumber1:             str = 'PercentUSDANumber1'
    percentSixOz:                   str = 'PercentSixOz'
    percentTenOz:                   str = 'PercentTenOz'
    percentBruiseFree:              str = 'PercentBruiseFree'
    percentHollowHeart:             str = 'PercentHollowHeart'
    percentDirtRockForeignMaterial: str = 'PercentDirtRockForeignMaterial'
    percentUnusable:                str = 'PercentUnusable'
    specificGravity:                str = 'SpecificGravity'
    cornPenaltyDollars:             str = 'CornPenaltyDollars'
    rawColorScore:                  str = 'RawColorScore'
    blanchColorScore:               str = 'BlanchColorScore'
    binCapacityCWT:                 str = 'BinCapacityCWT'
    loadInCWT:                      str = 'LoadInCWT'
    loadOutCWT:                     str = 'LoadOutCWT'
    
    #columns that will be added in aggreagations/calculations
    currentCWT:                     str = 'CurrentCWT'
    percentCWTLeft:                 str = 'PercentCWTLeft'
    percentBinCapacityLeft:         str = 'PercentBinCapacityLeft'
    totalBinCWT:                    str = 'TotalBinCWT'
    totalBinPctLeft:                str = 'TotalBinPercentLeft'
    totalLoadInPctLeft:             str = 'TotalLoadInPctLeft'
    #penalty column
    penalty:                        str = 'LotPenalty'
    lotValue:                       str = 'LotValue'
    makableProductCount:            str = 'MakableProductCount'

    #for easy resetting of the columns
    baseColumns = [ storageComplexBin, 
                    destinationBinID, 
                    binEntranceCount, 
                    isShortTermStorage, 
                    isOpenedBin, 
                    isCompromisedLot, 
                    severity, 
                    stackingOrder, 
                    sourceFieldInteger, 
                    varietyID, 
                    loadInDate, 
                    percentUSDANumber1, 
                    percentSixOz, 
                    percentTenOz, 
                    percentBruiseFree, 
                    percentHollowHeart, 
                    percentDirtRockForeignMaterial, 
                    percentUnusable, 
                    specificGravity, 
                    cornPenaltyDollars, 
                    rawColorScore, 
                    blanchColorScore, 
                    binCapacityCWT, 
                    loadInCWT, 
                    loadOutCWT,
                    lotValue]

@dataclass
class Json_Strings:
    products = 'products'
    name = 'name'
    constraints = 'constraints'
    line1Capacity = 'Line1Capacity'
    line2Capacity = 'Line2Capacity'
    sixOz = 'sixoz'
    tenOz = 'tenoz'
    bruiseFree = 'bruise_free'
    hollow = 'hollow'
    minGravity = 'min_gravity'
    maxGravity = 'max_gravity'
    fryColor = 'fry_color'
    corn = 'corn'
    requiredCWT = 'RequiredCWT'

@dataclass
class Output_Dataframe_Columns:
    day = 'Day'
    binId = 'SourceBinID'
    complexPin = 'SourceComplexPIN'
    stackingOrderNumber = 'StackingOrderNumber'
    loadOutCWT = 'LoadOutCWT' 