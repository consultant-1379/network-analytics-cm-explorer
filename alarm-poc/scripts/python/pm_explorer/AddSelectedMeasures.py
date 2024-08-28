from System.IO import MemoryStream, StreamWriter, SeekOrigin
from System import Array
from Spotfire.Dxp.Data import DataValueCursor, IndexSet
from Spotfire.Dxp.Data.Import import TextDataReaderSettings, TextFileDataSource

dataTableName = 'Measure Mapping'
dataTable = Document.Data.Tables[dataTableName]
selectedDataTableName = 'Measure Mapping (Selected)'
dataTableSelected = Document.Data.Tables[selectedDataTableName]

measureMappingColumns = '''Measure
Counters
Formula
Node Type
System Area
Measure Type
LTE Access Type
WCDMA Access Type
GSM Access Type
Access Type
NR Access Type
MOCLASS
TABLENAME
KEYS
ELEMENT
TIMEAGGREGATION
GROUPAGGREGATION
MEASUREMENTTYPE
MEASUREMENTTYPEID
MEASUREMENTNAME
COLLECTIONMETHOD
NODE VERSION
GSM
WCDMA
LTE
NR
PM GROUP
COUNTER OR GAUGE'''.split('\n')

def getExistingSelections(selectedDataTableName):
    selectedSet = set()
    if Document.Data.Tables.Contains(selectedDataTableName):
        selectedDataTable = Document.Data.Tables[selectedDataTableName]
        try:
            cursor = createCursor(dataTableSelected)
            for row in dataTableSelected.GetRows(Array[DataValueCursor](cursor.values())):
                row = []
                for col in measureMappingColumns:
                    row.append(cursor[col].CurrentValue)
                selectedSet.add(';'.join(row))
        except Exception as e:
            print("Exception: ", e)
    return selectedSet


def createCursor(eTable):
    CursList = []
    ColList = []
    colname = []
    for eColumn in eTable.Columns:
        CursList.append(DataValueCursor.CreateFormatted(eTable.Columns[eColumn.Name]))
        ColList.append(eTable.Columns[eColumn.Name].ToString())
    CursArray = Array[DataValueCursor](CursList)
    cusrDict = dict(zip(ColList, CursList))
    return cusrDict


def getSelectedMeasures(selectedSet):
    markedRowSelection = Document.Data.Markings["Measures"].GetSelection(dataTable).AsIndexSet()
    measureCursor = createCursor(dataTable)
    
    for row in dataTable.GetRows(markedRowSelection, Array[DataValueCursor](measureCursor.values())):
        row = []
        for col in measureMappingColumns:
            row.append(measureCursor[col].CurrentValue)
        selectedSet.add(';'.join(row))
    return selectedSet


def addToExistingSelections(selectedDataTableName, selectedSet):
    delimiter = ';'
    stream = MemoryStream()
    csvWriter = StreamWriter(stream)
    for item in selectedSet:
        csvWriter.WriteLine(item)
    settings = TextDataReaderSettings()
    settings.Separator = delimiter
    csvWriter.Flush()
    stream.Seek(0, SeekOrigin.Begin)
    textFileDataSource = TextFileDataSource(stream, settings)
    if Document.Data.Tables.Contains(selectedDataTableName):
        selectedDataTable = Document.Data.Tables[selectedDataTableName]
        selectedDataTable.ReplaceData(textFileDataSource)
    else:
        Document.Data.Tables.Add(selectedDataTableName, textFileDataSource)

selectedSet = getExistingSelections(selectedDataTableName)
addToExistingSelections(selectedDataTableName, getSelectedMeasures(selectedSet))
