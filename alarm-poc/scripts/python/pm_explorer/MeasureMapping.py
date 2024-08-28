# ********************************************************************
# Ericsson Inc.                                                 SCRIPT
# ********************************************************************
#
#
# (c) Ericsson Inc. 2019 - All rights reserved.
#
# The copyright to the computer program(s) herein is the property
# of Ericsson Inc. The programs may be used and/or copied only with
# the written permission from Ericsson Inc. or in accordance with the
# terms and conditions stipulated in the agreement/contract under
# which the program(s) have been supplied.
#
# ********************************************************************
# Name    : MeasureMapping.py
# Date    : 11/10/2019
# Revision: 1.0
# Purpose : Map ENIQ pm tables to MOMs, Counter Lists and Measures
#
# Usage   : PM Explorer
#

import datetime
import Spotfire.Dxp.Application

from Spotfire.Dxp.Data import *
from Spotfire.Dxp.Data.Import import DatabaseDataSource, DatabaseDataSourceSettings, DataTableDataSource, TextFileDataSource, TextDataReaderSettings
from Spotfire.Dxp.Framework.ApplicationModel import *
from Spotfire.Dxp.Application.Visuals import VisualContent

from System import Array, String, DateTime
from System.IO import StreamWriter, MemoryStream, SeekOrigin, FileStream, FileMode, File
from System.Collections.Generic import HashSet


def createTable(dataTableName, stream):
    settings = TextDataReaderSettings()
    settings.Separator = ";"
    settings.AddColumnNameRow(0)
    settings.ClearDataTypes(False)
    stream.Seek(0, SeekOrigin.Begin)
    fs = TextFileDataSource(stream, settings)
    if Document.Data.Tables.Contains(dataTableName):
        Document.Data.Tables[dataTableName].ReplaceData(fs)
    else:
        Document.Data.Tables.Add(dataTableName, fs)


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


def fetchDataFromENIQAsync():
    dataSourceName = Document.Properties['ENIQREPDB']
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.Odbc", "DSN=" + dataSourceName, sql)
    try:
        dataTableDataSource = DatabaseDataSource(dataSourceSettings)
        if Document.Data.Tables.Contains(tableName):
            dt = Document.Data.Tables[tableName]
            dt.ReplaceData(dataTableDataSource)
        else:
            dt = Document.Data.Tables.Add(tableName, dataTableDataSource)
    except:
        print "except"
        raise


print datetime.datetime.now().time()

# Measures to ENIQ-CounterList-MOM mapping columns
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

stream = MemoryStream()
measureStream = MemoryStream()
csvWriter = StreamWriter(stream)
measureCsvWriter = StreamWriter(measureStream)
measureCsvWriter.WriteLine(';'.join(measureMappingColumns) + '\r\n')

createTable("Counter Mapping", stream)

measureCsvWriter.Flush()
createTable("Measure Mapping", measureStream)

ps = Application.GetService[ProgressService]()
dataSourceName = ''

keySql = """
SELECT
COUNTER + '.' + elements.TABLENAME as MEASURE,
MOMCOUNTER,
LIST(elements.DATANAME) AS KEYS,
keyElements.DATANAME AS ELEMENT,
elements.TABLENAME,
COUNTER,
TIMEAGGREGATION,
GROUPAGGREGATION,
elements.NODETYPE,
elements.SYSTEMAREA
FROM
(
SELECT
DISTINCT UPPER(DATANAME) AS COUNTER,
UPPER(DATAID) AS MOMCOUNTER,
TIMEAGGREGATION,
GROUPAGGREGATION,
UPPER(RIGHT(TYPEID, CHARINDEX(':', REVERSE(TYPEID)) - 1)) AS TABLENAME
FROM DWHREP.MEASUREMENTCOUNTER
ORDER BY TABLENAME
)counters,
(
SELECT
DATANAME,
UPPER(RIGHT(TYPEID, CHARINDEX(':', REVERSE(TYPEID)) - 1)) AS TABLENAME,
LEFT(TABLENAME, 4 + (CHARINDEX('_', SUBSTRING(TABLENAME, 6, LENGTH(TABLENAME) - 4)))) AS TABLE_SHORTNAME,
SUBSTRING(TABLE_SHORTNAME, 6, LENGTH(TABLE_SHORTNAME) - 5) AS NODETYPECHECK,
CASE WHEN NODETYPECHECK LIKE 'SGSN%' THEN 'SGSN' END AS NODETYPE,
CASE
WHEN NODETYPE = 'SGSN' THEN 'Core'
ELSE ''
END AS SYSTEMAREA
FROM MEASUREMENTKEY MK
INNER JOIN TPACTIVATION TP ON MK.TYPEID LIKE TP.VERSIONID+'%'
WHERE UPPER(TP.STATUS) = 'ACTIVE'
AND TABLE_SHORTNAME IN (
    'DC_E_SGSNMME',
    'DC_E_SGSN'
)
AND DATANAME NOT IN
(
'BATCH_ID',
'DATE_ID',
'DATETIME_ID',
'DAY_ID',
'DC_RELEASE',
'DC_SOURCE',
'DC_SUSPECTFLAG',
'DC_TIMEZONE',
'HOUR_ID',
'MIN_ID',
'MONTH_ID',
'PERIOD_DURATION'
))elements,
(
SELECT
DATANAME,
UPPER(RIGHT(TYPEID, CHARINDEX(':', REVERSE(TYPEID)) - 1)) AS TABLENAME
FROM MEASUREMENTKEY MK
INNER JOIN TPACTIVATION TP ON MK.TYPEID LIKE TP.VERSIONID+'%'
WHERE UPPER(TP.STATUS) = 'ACTIVE'
AND DATANAME NOT IN
(
'BATCH_ID',
'DATE_ID',
'DATETIME_ID',
'DAY_ID',
'DC_RELEASE',
'DC_SOURCE',
'DC_SUSPECTFLAG',
'DC_TIMEZONE',
'HOUR_ID',
'MIN_ID',
'MONTH_ID',
'PERIOD_DURATION'
)
AND ISELEMENT = 1
)keyElements
WHERE elements.TABLENAME = keyElements.TABLENAME
AND elements.TABLENAME = counters.TABLENAME
GROUP BY
elements.TABLENAME, 
keyElements.DATANAME, 
counters.COUNTER, 
counters.MOMCOUNTER,
counters.TIMEAGGREGATION,
counters.GROUPAGGREGATION,
elements.NODETYPE,
elements.SYSTEMAREA
ORDER BY elements.TABLENAME
"""

sql = keySql
tableName = 'ENIQ Mapping'
ps.ExecuteWithProgress("Fetching counter and table mapping data", 'Testing Connection to %s ...' % (dataSourceName), fetchDataFromENIQAsync)

# CounterList MOM Mapping columns
mapColumns = '''MoClass
MeasurementType
measurementTypeId
measurementName
collectionMethod
description
aggregation
Node Version
GSM
WCDMA
LTE
NR
PM Group
Counter or Gauge'''.split('\n')

# Mapping Table columns - ENIQ to counterlist MOM
columns = ';'.join('''COUNTER
TABLENAME
KEYS
ELEMENT
TIMEAGGREGATION
GROUPAGGREGATION
MOMCOUNTER
NODETYPE
SYSTEMAREA
MOCLASS
MEASUREMENTTYPE
MEASUREMENTTYPEID
MEASUREMENTNAME
COLLECTIONMETHOD
DESCRIPTION
AGGREGATION
NODE VERSION
GSM
WCDMA
LTE
NR
PM GROUP
COUNTER OR GAUGE'''.split('\n')) + '\r\n'


'''
ENIQ Mapping Section



ENIQ pm tables and columns mapped to CounterList and MOM data
'''

# Measures - KPIs
MeasureDataTableName = 'Measures'
MeasureDataTable = Document.Data.Tables[MeasureDataTableName]
measureCursor = createCursor(MeasureDataTable)

# CounterList MOM
CounterMomTableName = 'CounterList MOM'
CounterMomDataTable = Document.Data.Tables[CounterMomTableName]
countermomCursor = createCursor(CounterMomDataTable)

# ENIQ Mapping
ENIQMappingDataTableName = 'ENIQ Mapping'
ENIQMappingDataTable = Document.Data.Tables[ENIQMappingDataTableName]
ENIQMappingCursor = createCursor(ENIQMappingDataTable)
ENIQMappingCounterCursor = createCursor(ENIQMappingDataTable)

mappinglist = {}
mapping_rows = columns
eniqCounters = []

for mappingRow in ENIQMappingDataTable.GetRows(Array[DataValueCursor](ENIQMappingCursor.values())):
    ENIQCounter = ENIQMappingCursor['COUNTER'].CurrentValue
    eniqCounters.append(ENIQCounter)
    for countermom in CounterMomDataTable.GetRows(Array[DataValueCursor](countermomCursor.values())):
        compareCounter = countermomCursor['measurementName'].CurrentValue
        MOMCounter = ENIQMappingCursor['MOMCOUNTER'].CurrentValue
        systemArea = ENIQMappingCursor['SYSTEMAREA'].CurrentValue
        nodetype = ENIQMappingCursor['NODETYPE'].CurrentValue
        if ENIQCounter.upper() == compareCounter.upper() or MOMCounter.upper() == compareCounter.upper():
            keys = ENIQMappingCursor['KEYS'].CurrentValue
            element = ENIQMappingCursor['ELEMENT'].CurrentValue
            timeAgg = ENIQMappingCursor['TIMEAGGREGATION'].CurrentValue
            groupAgg = ENIQMappingCursor['GROUPAGGREGATION'].CurrentValue
            tableListName = ENIQMappingCursor['TABLENAME'].CurrentValue
            if ENIQCounter in mappinglist.keys():
                if tableListName not in mappinglist[ENIQCounter].keys():
                    mappinglist[ENIQCounter][tableListName] = [[keys], [element], [timeAgg], [groupAgg], [MOMCounter], [nodetype], [systemArea]]
                    for col in mapColumns:
                        if countermomCursor[col].CurrentValue == '':
                            mappinglist[ENIQCounter][tableListName].append([' '])
                        else:
                            mappinglist[ENIQCounter][tableListName].append([countermomCursor[col].CurrentValue])
            else:
                mappinglist[ENIQCounter] = {}
                mappinglist[ENIQCounter][tableListName] = [[keys], [element], [timeAgg], [groupAgg], [MOMCounter], [nodetype], [systemArea]]
                for col in mapColumns:
                    if countermomCursor[col].CurrentValue == '':
                        mappinglist[ENIQCounter][tableListName].append([' '])
                    else:
                        mappinglist[ENIQCounter][tableListName].append([countermomCursor[col].CurrentValue])

for counter in eniqCounters:
    for mappingRow in ENIQMappingDataTable.GetRows(Array[DataValueCursor](ENIQMappingCounterCursor.values())):
        if counter == ENIQMappingCounterCursor['COUNTER'].CurrentValue:
            MOMCounter = ENIQMappingCounterCursor['MOMCOUNTER'].CurrentValue
            systemArea = ENIQMappingCounterCursor['SYSTEMAREA'].CurrentValue
            nodetype = ENIQMappingCounterCursor['NODETYPE'].CurrentValue
            keys = ENIQMappingCounterCursor['KEYS'].CurrentValue
            element = ENIQMappingCounterCursor['ELEMENT'].CurrentValue
            timeAgg = ENIQMappingCounterCursor['TIMEAGGREGATION'].CurrentValue
            groupAgg = ENIQMappingCounterCursor['GROUPAGGREGATION'].CurrentValue
            tableListName = ENIQMappingCounterCursor['TABLENAME'].CurrentValue
            if counter not in mappinglist.keys():
                mappinglist[counter] = {}
                mappinglist[counter][tableListName] = [[keys], [element], [timeAgg], [groupAgg], [MOMCounter], [nodetype], [systemArea]]
            elif tableListName not in mappinglist[counter].keys():
                mappinglist[counter][tableListName] = [[keys], [element], [timeAgg], [groupAgg], [MOMCounter], [nodetype], [systemArea]]
            for col in mapColumns:
                mappinglist[counter][tableListName].append([' '])

for i in mappinglist.keys():
    for j in mappinglist[i].keys():
        mapping_rows += i + ';' + j
        for k in range(0, len(columns.split(';')) - 2):
            mapping_rows += ';' + ','.join(mappinglist[i][j][k])
        mapping_rows += '\r\n'

stream = MemoryStream()
writer = StreamWriter(stream)
writer.Write(mapping_rows)
writer.Flush()
stream.Seek(0, SeekOrigin.Begin)

readerSettings = TextDataReaderSettings()
readerSettings.Separator = ";"
readerSettings.AddColumnNameRow(0)

textDataSource = TextFileDataSource(stream, readerSettings)
settings = AddRowsSettings(Document.Data.Tables['Counter Mapping'], textDataSource)
Document.Data.Tables['Counter Mapping'].AddRows(textDataSource, settings)


'''
ENIQ CounterList MOM Measure Mapping Section



ENIQ, CounterList and MOM data mapped to Measures table and counters listed as selectable measures
'''

# ENIQ CounterList MOM Mapping
CounterMappingDataTableName = 'Counter Mapping'
CounterMappingDataTable = Document.Data.Tables[CounterMappingDataTableName]
CounterMappingCursor = createCursor(CounterMappingDataTable)

# ENIQ CounterList MOM Measure Mapping
MeasureMappingDataTableName = 'Measure Mapping'
MeasureMappingDataTable = Document.Data.Tables[MeasureMappingDataTableName]
MeasureMappingCursor = createCursor(MeasureMappingDataTable)

mappinglist = {}
measureRows = ';'.join(measureMappingColumns) + '\r\n'


'''
Add Measures from Measure/KPI table to Measure Mapping Table
'''

for measureRow in MeasureDataTable.GetRows(Array[DataValueCursor](measureCursor.values())):
    kpiname = measureCursor['Measure'].CurrentValue
    if kpiname in mappinglist.keys():
        kpiname = measureCursor['Measure'].CurrentValue + ' - ' + measureCursor['Access Type'].CurrentValue
    counters = measureCursor['Counters'].CurrentValue.Split(',')
    formula = measureCursor['Formula'].CurrentValue
    lte = measureCursor['LTE Access Type'].CurrentValue
    wcdma = measureCursor['WCDMA Access Type'].CurrentValue
    gsm = measureCursor['GSM Access Type'].CurrentValue
    accessType = measureCursor['Access Type'].CurrentValue
    measureType = measureCursor['Measure Type'].CurrentValue
    nr = measureCursor['NR Access Type'].CurrentValue

    for counterMappingRow in CounterMappingDataTable.GetRows(Array[DataValueCursor](CounterMappingCursor.values())):
        for counter in counters:
            compareCounter = CounterMappingCursor['COUNTER'].CurrentValue
            compareMOMCounter = CounterMappingCursor['MOMCOUNTER'].CurrentValue
            nodetype = measureCursor['Node Type'].CurrentValue
            if 'SGSN' in nodetype:
                nodetype = 'SGSN'
            systemarea = measureCursor['System Area'].CurrentValue
            moClass = CounterMappingCursor['MOCLASS'].CurrentValue
            if counter.upper() == compareCounter.upper() or counter.upper() == compareMOMCounter.upper():
                if compareMOMCounter.upper() in formula.upper():
                    formula = formula.upper().replace(compareMOMCounter.upper(), compareCounter)
                elif compareMOMCounter in formula:
                    formula = formula.replace(compareMOMCounter, compareCounter)

                tableListName = CounterMappingCursor['TABLENAME'].CurrentValue
                keys = CounterMappingCursor['KEYS'].CurrentValue
                element = CounterMappingCursor['ELEMENT'].CurrentValue
                timeAgg = CounterMappingCursor['TIMEAGGREGATION'].CurrentValue
                groupAgg = CounterMappingCursor['GROUPAGGREGATION'].CurrentValue
                if kpiname in mappinglist.keys():
                    if tableListName in mappinglist[kpiname].keys():
                        if counter not in mappinglist[kpiname][tableListName][0] and compareCounter not in mappinglist[kpiname][tableListName][0]:
                            mappinglist[kpiname][tableListName][0].append(compareCounter)
                            mappinglist[kpiname][tableListName][3].append(timeAgg)
                            mappinglist[kpiname][tableListName][4].append(groupAgg)
                    else:
                        mappinglist[kpiname][tableListName] = [[compareCounter], [keys], [element], [timeAgg], [groupAgg], [nodetype], [systemarea], [formula], [lte], [wcdma], [gsm], [accessType], [measureType], [nr], [moClass]]
                else:
                    mappinglist[kpiname] = {}
                    mappinglist[kpiname][tableListName] = [[compareCounter], [keys], [element], [timeAgg], [groupAgg], [nodetype], [systemarea], [formula], [lte], [wcdma], [gsm], [accessType], [measureType], [nr], [moClass]]
                if mappinglist[kpiname][tableListName][7][0] != formula:
                    mappinglist[kpiname][tableListName][7][0] = formula

mappinglistref = '''KEYS
ELEMENT
TIMEAGGREGATION
GROUPAGGREGATION
NODE TYPE
SYSTEM AREA
FORMULA
LTE Access Type
WCDMA Access Type
GSM Access Type
Access Type
Measure Type
NR Access Type'''.split('\n')

for i in mappinglist.keys():
    for j in mappinglist[i].keys():
        mappingRowArray = []
        mappingRowArray.append(i)
        tablenameMap = j
        for col in measureMappingColumns:
            if col.upper() == 'MOCLASS':
                mappingRowArray.append(','.join(mappinglist[i][j][len(mappinglist[i][j]) - 1]))
            elif col.upper() == 'TABLENAME':
                mappingRowArray.append(tablenameMap)
            elif col.upper() == 'COUNTER' or col.upper() == 'COUNTERS':
                mappingRowArray.append(','.join(mappinglist[i][j][0]))
            else:
                for ref in range(len(mappinglistref)):
                    if mappinglistref[ref].upper() == col.upper():
                        mappingRowArray.append(','.join(mappinglist[i][j][ref + 1]))
        measureRows += ';'.join(mappingRowArray) + '\r\n'


'''
Add all Counters to Measure Mapping Table
'''

for counterMappingRow in CounterMappingDataTable.GetRows(Array[DataValueCursor](CounterMappingCursor.values())):
    mappingRowArray = []
    tableList = CounterMappingCursor['TABLENAME'].CurrentValue.Split(',')
    for tableListName in tableList:
        mappingRowArray = []
        for col in measureMappingColumns:
            if col == 'Measure':
                mappingRowArray.append(CounterMappingCursor['COUNTER'].CurrentValue + '.' + tableListName)
            elif col == 'Counters' or col == 'Formula':
                mappingRowArray.append(CounterMappingCursor['COUNTER'].CurrentValue)
            elif col == 'Measure Type':
                mappingRowArray.append('Counter')
            elif col == 'Node Type':
                mappingRowArray.append(CounterMappingCursor['NODETYPE'].CurrentValue)
            elif col == 'System Area':
                mappingRowArray.append(CounterMappingCursor['SYSTEMAREA'].CurrentValue)
            elif col == 'TABLENAME':
                mappingRowArray.append(tableListName)
            else:
                if col in CounterMappingCursor.keys():
                    mappingRowArray.append(CounterMappingCursor[col].CurrentValue)
                elif col.upper() in CounterMappingCursor.keys():
                    mappingRowArray.append(CounterMappingCursor[col.upper()].CurrentValue)
                else:
                    mappingRowArray.append('')
        measureRows += ';'.join(mappingRowArray) + '\r\n'

measureStream = MemoryStream()
measureWriter = StreamWriter(measureStream)
measureWriter.Write(measureRows)
measureWriter.Flush()
measureStream.Seek(0, SeekOrigin.Begin)

measureReaderSettings = TextDataReaderSettings()
measureReaderSettings.Separator = ";"
measureReaderSettings.AddColumnNameRow(0)

measureTextDataSource = TextFileDataSource(measureStream, measureReaderSettings)
measureSettings = AddRowsSettings(Document.Data.Tables['Measure Mapping'], measureTextDataSource)
Document.Data.Tables['Measure Mapping'].AddRows(measureTextDataSource, measureSettings)
print datetime.datetime.now().time()
