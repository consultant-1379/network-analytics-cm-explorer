from System.IO import MemoryStream, StreamWriter, SeekOrigin
from System import Array
from Spotfire.Dxp.Data import DataValueCursor, IndexSet
from Spotfire.Dxp.Data.Import import TextDataReaderSettings, TextFileDataSource

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


def getExistingSelections(selectedDataTableName):
    existingSet = set()
    if Document.Data.Tables.Contains(selectedDataTableName):
        selectedDataTable = Document.Data.Tables[selectedDataTableName]
        try:
            cursor = createCursor(dataTableSelected)
            for row in selectedDataTable.GetRows(Array[DataValueCursor](cursor.values())):
                row = []
                for col in measureMappingColumns:
                    row.append(cursor[col].CurrentValue)
                existingSet.add(';'.join(row))
        except Exception as e:
            print("Exception: ", e)
    return existingSet


def getSelectedMeasures(dataTableSelected):
    markedRowSelection = Document.Data.Markings["MeasuresSelected"].GetSelection(dataTableSelected).AsIndexSet()
    measureCursor = createCursor(dataTableSelected)
    selectedSet = set()
    for row in dataTableSelected.GetRows(markedRowSelection, Array[DataValueCursor](measureCursor.values())):
        row = []
        for col in measureMappingColumns:
            row.append(measureCursor[col].CurrentValue)
        selectedSet.add(';'.join(row))
    return selectedSet


def removeFromExistingSelections(selectedDataTable, selectedSet):
    delimiter = ';'
    stream = MemoryStream()
    csvWriter = StreamWriter(stream)
    csvWriter.WriteLine(';'.join(measureMappingColumns) + '\r\n')
    for item in selectedSet:
        csvWriter.WriteLine(item)
    settings = TextDataReaderSettings()
    settings.Separator = delimiter
    settings.AddColumnNameRow(0)
    csvWriter.Flush()
    stream.Seek(0, SeekOrigin.Begin)
    textFileDataSource = TextFileDataSource(stream, settings)
    selectedDataTable.ReplaceData(textFileDataSource)


existingSet = getExistingSelections(selectedDataTableName)
selectedSet = getSelectedMeasures(dataTableSelected)
print selectedSet
measures = existingSet.difference(selectedSet)
print measures
removeFromExistingSelections(dataTableSelected, measures)
