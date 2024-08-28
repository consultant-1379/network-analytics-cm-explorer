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
# Name    : FetchKPIMappings.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

import System
import Spotfire.Dxp.Application
from Spotfire.Dxp.Data.Import import DatabaseDataSource, DatabaseDataSourceSettings, DataTableDataSource, TextFileDataSource, TextDataReaderSettings
from Spotfire.Dxp.Framework.ApplicationModel import *
from Spotfire.Dxp.Data import *
from System import Array
from System.IO import  StreamWriter, MemoryStream, SeekOrigin
from Spotfire.Dxp.Application.Visuals import VisualContent
from System.Collections.Generic import HashSet
from System.IO import FileStream, FileMode, File, MemoryStream, SeekOrigin, StreamWriter
import System.String
from Spotfire.Dxp.Data.Import import TextDataReaderSettings
from Spotfire.Dxp.Data.Import import TextFileDataSource
from Spotfire.Dxp.Data.Import import DataTableDataSource
from System import DateTime


def createTable(dataTableName, stream):
    settings = TextDataReaderSettings()
    settings.Separator = ";"
    settings.AddColumnNameRow(0)
    settings.ClearDataTypes(False)
    settings.SetDataType(0, DataType.Integer)
    settings.SetDataType(1, DataType.String)
    stream.Seek(0, SeekOrigin.Begin)
    fs = TextFileDataSource(stream, settings)
    if Document.Data.Tables.Contains(dataTableName):
        Document.Data.Tables[dataTableName].ReplaceData(fs)
    else:
        Document.Data.Tables.Add(dataTableName, fs)


stream = MemoryStream()
csvWriter = StreamWriter(stream)
createTable("KPI Tables", stream)

ps = Application.GetService[ProgressService]()
dataSourceName = ''

keySql = """
SELECT 
COUNTERS + '.' + elements.TABLENAME as MeasureName,
LIST(elements.DATANAME) AS KEYS, 
keyElements.DATANAME AS ELEMENT, 
elements.TABLENAME, 
COUNTERS, 
TIMEAGGREGATION, 
GROUPAGGREGATION, 
CASE 
WHEN UPPER(SUBSTRING(elements.TABLENAME, 6, CHARINDEX('_', SUBSTRING(elements.TABLENAME, 6, LENGTH(elements.TABLENAME) - 6)) - 1)) = 'IMS'
THEN 
CASE WHEN CHARINDEX('_', SUBSTRING(elements.TABLENAME, 10, LENGTH(elements.TABLENAME) - 10)) > 0
THEN UPPER(SUBSTRING(elements.TABLENAME, 10, CHARINDEX('_', SUBSTRING(elements.TABLENAME, 10, LENGTH(elements.TABLENAME) - 10)) - 1))
ELSE UPPER(SUBSTRING(elements.TABLENAME, 10, LENGTH(elements.TABLENAME) - 9))
END
ELSE
REPLACE(UPPER(SUBSTRING(elements.TABLENAME, 6, CHARINDEX('_', SUBSTRING(elements.TABLENAME, 6, LENGTH(elements.TABLENAME) - 6)) - 1)), 'IMS', '') 
END AS NODETYPE,
CASE 
WHEN NODETYPE LIKE '%ERBS%' OR NODETYPE LIKE '%RBS%' OR NODETYPE LIKE '%RAN%' THEN 'Radio'
WHEN NODETYPE LIKE '%IMS%' OR NODETYPE LIKE '%CSCF%' OR NODETYPE LIKE '%SBG%' OR NODETYPE LIKE '%MTAS%' OR NODETYPE LIKE '%SGSN%' OR NODETYPE LIKE '%WMG%' OR NODETYPE LIKE '%EPDG%' OR NODETYPE LIKE '%MGW%' THEN 'Core'
END AS SYSTEMAREA
FROM
(
SELECT 
DISTINCT UPPER(DATANAME) AS 'COUNTERS', 
UPPER(DATAID) AS 'MOMCounter',
TIMEAGGREGATION,
GROUPAGGREGATION,
UPPER(SUBSTRING(TYPEID, LENGTH(TYPEID)-CHARINDEX(':', REVERSE(TYPEID))+2, CHARINDEX(':', REVERSE(TYPEID)))) AS TABLENAME
FROM DWHREP.MEASUREMENTCOUNTER
ORDER BY TABLENAME
)counters,
(
SELECT
DATANAME,
UPPER(SUBSTRING(TYPEID, LENGTH(TYPEID)-CHARINDEX(':', REVERSE(TYPEID))+2, CHARINDEX(':', REVERSE(TYPEID)))) AS TABLENAME
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
))elements,
(
SELECT
DATANAME,
UPPER(SUBSTRING(TYPEID, LENGTH(TYPEID)-CHARINDEX(':', REVERSE(TYPEID))+2, CHARINDEX(':', REVERSE(TYPEID)))) AS TABLENAME
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
counters.COUNTERS, 
counters.TIMEAGGREGATION,
counters.GROUPAGGREGATION,
NODETYPE, 
SYSTEMAREA
ORDER BY elements.TABLENAME
"""


def createCursor(eTable):
    CursList = []
    ColList = []
    colname = []
    for eColumn in eTable.Columns:
        CursList.append(DataValueCursor.CreateFormatted(eTable.Columns[eColumn.Name]))
        ColList.append(eTable.Columns[eColumn.Name].ToString())
    CursArray = Array[DataValueCursor](CursList)
    cusrDict=dict(zip(ColList, CursList))
    return cusrDict


def fetchDataFromENIQAsync():
    dataSourceName = Document.Properties['ENIQDB']
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.Odbc", "DSN=" + dataSourceName + "_repdb", sql)
    try:
        dataTableDataSource = DatabaseDataSource(dataSourceSettings)
        if Document.Data.Tables.Contains(tableName):
            dt = Document.Data.Tables[tableName]
            dt.RemoveRows(RowSelection(IndexSet(dt.RowCount, True)))
            settings = AddRowsSettings(dt, dataTableDataSource)
            dt.AddRows(dataTableDataSource, settings)
        else:
            dt = Document.Data.Tables.Add(tableName, dataTableDataSource)
    except:
        print "except"
        raise


sql = keySql
tableName = 'Mapping'
ps.ExecuteWithProgress("Fetching counter and table mapping data", 'Testing Connection to %s ...' % (dataSourceName), fetchDataFromENIQAsync)

KPIDataTableName = 'KPIs'
KPIDataTable = Document.Data.Tables[KPIDataTableName]

MappingDataTableName = 'Mapping'
MappingDataTable = Document.Data.Tables[MappingDataTableName]

kpiTablesDataTableName = 'KPI Tables'
kpiTablesDataTable = Document.Data.Tables[kpiTablesDataTableName]

KPICursor = createCursor(KPIDataTable)
mappingCursor = createCursor(MappingDataTable)
kpiTablesCursor = createCursor(kpiTablesDataTable)

mappinglist = {}
KPI_rows = 'MeasureName;TABLENAME;COUNTERS;KEYS;ELEMENT;TIMEAGGREGATION;GROUPAGGREGATION;NODETYPE;SYSTEMAREA\r\n'

for kpiRow in KPIDataTable.GetRows(Array[DataValueCursor](KPICursor.values())):
    kpiname = KPICursor['KPIName'].CurrentValue
    print KPICursor.Keys
    print KPICursor.Item
    counters = KPICursor['Counters'].CurrentValue.Split(',')
    for counter in counters:
        for mappingRow in MappingDataTable.GetRows(Array[DataValueCursor](mappingCursor.values())):
            compareCounter = mappingCursor['COUNTERS'].CurrentValue
            nodetype = mappingCursor['NODETYPE'].CurrentValue
            systemarea = mappingCursor['SYSTEMAREA'].CurrentValue
            if counter.upper() == compareCounter:
                tableListName = mappingCursor['TABLENAME'].CurrentValue
                keys = mappingCursor['KEYS'].CurrentValue
                element = mappingCursor['ELEMENT'].CurrentValue
                timeAgg = mappingCursor['TIMEAGGREGATION'].CurrentValue
                groupAgg = mappingCursor['GROUPAGGREGATION'].CurrentValue
                if kpiname in mappinglist.keys():
                    if tableListName in mappinglist[kpiname].keys():
                        if counter not in mappinglist[kpiname][tableListName][0]:
                            mappinglist[kpiname][tableListName][0].append(counter)
                            mappinglist[kpiname][tableListName][3].append(timeAgg)
                            mappinglist[kpiname][tableListName][4].append(groupAgg)
                    else:
                        mappinglist[kpiname][tableListName] = [[counter], [keys], [element], [timeAgg], [groupAgg], [nodetype], [systemarea]]
                else:
                    mappinglist[kpiname] = {}
                    mappinglist[kpiname][tableListName] = [[counter], [keys], [element], [timeAgg],[groupAgg],[nodetype],[systemarea]]

for i in mappinglist.keys():
    for j in mappinglist[i].keys():
        KPI_rows += i + ';' + j
        for k in range(0, len(mappinglist[i][j])):
            KPI_rows += ';' + ','.join(mappinglist[i][j][k])
        KPI_rows += '\r\n'

stream = MemoryStream()
writer = StreamWriter(stream)
writer.Write(KPI_rows)
writer.Flush()
stream.Seek(0, SeekOrigin.Begin)

readerSettings = TextDataReaderSettings()
readerSettings.Separator = ";"
readerSettings.AddColumnNameRow(0)
readerSettings.SetDataType(0, DataType.String)
readerSettings.SetDataType(1, DataType.String)
readerSettings.SetDataType(2, DataType.String)
readerSettings.SetDataType(3, DataType.String)
readerSettings.SetDataType(4, DataType.String)
readerSettings.SetDataType(5, DataType.String)
readerSettings.SetDataType(6, DataType.String)
readerSettings.SetDataType(7, DataType.String)
readerSettings.SetDataType(8, DataType.String)

textDataSource = TextFileDataSource(stream, readerSettings)

settings = AddRowsSettings(Document.Data.Tables['KPI Tables'], textDataSource)

Document.Data.Tables['KPI Tables'].AddRows(textDataSource, settings)

inputTableDS = DataTableDataSource(Document.Data.Tables["Mapping"])
outputTable = Document.Data.Tables['KPI Tables']

addRowsSettings = AddRowsSettings(outputTable, inputTableDS, "MeasureType", "Counter", "KPI")
outputTable.AddRows(inputTableDS, addRowsSettings)
