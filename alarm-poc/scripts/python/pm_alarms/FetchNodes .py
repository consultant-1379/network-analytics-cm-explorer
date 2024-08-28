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
# Name    : FetchNodes.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from Spotfire.Dxp.Data.Import import DatabaseDataSource, DatabaseDataSourceSettings, DataTableDataSource
from Spotfire.Dxp.Framework.ApplicationModel import *
from Spotfire.Dxp.Data import *
from System import Array

dataSourceName = Document.Properties['ENIQDB']
ps = Application.GetService[ProgressService]()
sql = ""
nodeType = Document.Properties["NodeType"]
elementMappingTable = Document.Data.Tables["KPI Tables"]


def createCursor(eTable):

    CursList = []
    ColList = []
    colname = []
    for eColumn in eTable.Columns:
        CursList.append(DataValueCursor.CreateFormatted(eTable.Columns[eColumn.Name]))
        ColList.append(eTable.Columns[eColumn.Name].ToString())
    CursArray = Array[DataValueCursor](CursList)
    cusrDict=dict(zip(ColList,CursList))
    return cusrDict


def getElementsAndTableNames():
    elementMappingCur = createCursor(elementMappingTable)
    listOfElementsAndTables = {}

    elementName = elementMappingCur["ELEMENT"]
    tableName = elementMappingCur["TABLENAME"]
    nodeTypeEM = elementMappingCur["NODETYPE"]
    rowCount = elementMappingTable.RowCount
    rowsToInclude = IndexSet(rowCount, True)

    for row in elementMappingTable.GetRows(rowsToInclude, elementName, tableName, nodeTypeEM):
        if nodeType in tableName.CurrentValue:
            listOfElementsAndTables.update({tableName.CurrentValue : elementName.CurrentValue})

    return listOfElementsAndTables


def buildSQL():
    counter = 0
    elementsList = getElementsAndTableNames()
    max_value = len(elementsList)-1
    sql = ""
    if len(elementsList) < 1:
        sql = u"SELECT DISTINCT "+list(elementsList.values())[0]+" AS node, '"+nodeType+"' AS Node_Type FROM "+list(elementsList.keys())[0]+"_RAW WHERE UTC_DATETIME_ID >= DATE(NOW()-7)"

    else:
        for table, element in elementsList.items():
            counter += 1
            if counter > 3:
                break
            if table == list(elementsList.keys())[2]:  # if table == list(elementsList.keys())[max_value]:
                sql += "SELECT DISTINCT " + element + " AS node, '"+nodeType+"' AS Node_Type FROM " + table + "_RAW WHERE UTC_DATETIME_ID >= DATE(NOW()-7)"
            else:
                sql += "SELECT DISTINCT " + element + " AS node, '"+nodeType+"' AS Node_Type FROM " + table + "_RAW WHERE UTC_DATETIME_ID >= DATE(NOW()-7) UNION "

    return sql


print buildSQL()


def fetchDataFromENIQAsync():

    dataSourceSettings = DatabaseDataSourceSettings("System.Data.Odbc", "DSN=" + dataSourceName+";Uid=dc;Pwd=dc", buildSQL())
    tableName = 'NodeList'
    ps.CurrentProgress.ExecuteSubtask('Testing Connection to %s ...' % (dataSourceName))

    ps.CurrentProgress.CheckCancel()

    try:
        dataTableDataSource = DatabaseDataSource(dataSourceSettings)
        if Document.Data.Tables.Contains(tableName):
            dt = Document.Data.Tables[tableName]
            dt.RemoveRows(RowSelection(IndexSet(dt.RowCount,True)))
        else:
            dt = Document.Data.Tables.Add(tableName,dataTableDataSource)

        settings = AddRowsSettings(dt,dataTableDataSource)
        dt.AddRows(dataTableDataSource,settings)
    except:
        print "except"
        raise


ps.ExecuteWithProgress("This is ExecuteWithProgress", 'Fetching topology data from: %s ' % (dataSourceName), fetchDataFromENIQAsync)

