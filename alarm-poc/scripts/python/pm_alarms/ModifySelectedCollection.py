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
# Name    : ModifySelectedCollection.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from Spotfire.Dxp.Data import DataValueCursor, IndexSet
from Spotfire.Dxp.Data.Import import DatabaseDataSource, DatabaseDataSourceSettings

CollectionName = Document.Properties['SelectedCollectionToModify']
CollectionTable = Document.Data.Tables['NodeCollection']
cursor = DataValueCursor.CreateFormatted(CollectionTable.Columns["CollectionName"])


def deleteNodeCollectionFromTable(Collection_name):
    for row in CollectionTable.GetRows(cursor):
        value = cursor.CurrentValue
        if CollectionName == value:
            RowSelection = CollectionTable.Select("CollectionName = '%s'" % str(value))
            CollectionTable.RemoveRows(RowSelection)


def deleteNodeCollection(collection_name):
    sqlTemplate = '''
    DELETE FROM [dbo].[NodeCollections]
    WHERE [CollectionName] = '%s'
    '''

    sql = sqlTemplate % collection_name
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.SqlClient",
                                                    "Server=atclvm657.athtem.eei.ericsson.se;Database=alarm_db;UID=netanserver;PWD=Ericsson02", sql)
    tempTableName = 'temp'
    databaseDataSource = DatabaseDataSource(dataSourceSettings)
    Document.Data.Tables.Add(tempTableName, databaseDataSource)
    Document.Data.Tables.Remove(tempTableName)


deleteNodeCollection(CollectionName)
deleteNodeCollectionFromTable(CollectionName)


class NodeCollectionColumn:
    CollectionName = 'CollectionName'
    NodeName = 'NodeName'
    NodeType = 'NodeType'

NodeCollectionColumn = NodeCollectionColumn()
nodeCollectionColumns = [NodeCollectionColumn.CollectionName, NodeCollectionColumn.NodeName]

nodeCollectionsErrorPropertyName = 'NodeCollectionError'
Document.Properties[nodeCollectionsErrorPropertyName] = ''


def getNodeCollectionsNames(dataTableName):
    nodeCollections = []
    if Document.Data.Tables.Contains(dataTableName):
        dataTable = Document.Data.Tables[dataTableName]
        cursor = DataValueCursor.CreateFormatted(dataTable.Columns[NodeCollectionColumn.CollectionName])
        rows = IndexSet(dataTable.RowCount, True)

        for row in dataTable.GetDistinctRows(rows, cursor):
            nodeCollections.append(cursor.CurrentValue)
    return nodeCollections


def getSelectedNodesNames(dataTableName):
    selectedNodesNames = []
    if Document.Data.Tables.Contains(dataTableName):
        dataTable = Document.Data.Tables[dataTableName]
        cursor = DataValueCursor.CreateFormatted(dataTable.Columns[NodeCollectionColumn.NodeName])
        rows = IndexSet(dataTable.RowCount, True)

        for row in dataTable.GetDistinctRows(rows, cursor):
            selectedNodesNames.append(cursor.CurrentValue)
    return selectedNodesNames


def getSelectedNodeType(dataTableName):
    selectedNodeType = ''
    if Document.Data.Tables.Contains(dataTableName):
        dataTable = Document.Data.Tables[dataTableName]
        cursor = DataValueCursor.CreateFormatted(dataTable.Columns[NodeCollectionColumn.NodeType])
        rows = IndexSet(dataTable.RowCount, True)
        for row in dataTable.GetDistinctRows(rows, cursor):
           selectedNodeType = cursor.CurrentValue
    return selectedNodeType


def writeNodeCollectionToDB(nodeCollection):
    sqlTemplate = '''
INSERT INTO [dbo].[NodeCollections]
           ([CollectionName]
           ,[NodeName]
           ,[NodeType])
     VALUES
           %s
'''
    sql = sqlTemplate % nodeCollection
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.SqlClient",
                                                    "Server=atclvm657.athtem.eei.ericsson.se;Database=alarm_db;UID=netanserver;PWD=Ericsson02", sql)
    tempTableName = 'temp'
    databaseDataSource = DatabaseDataSource(dataSourceSettings)
    print sql
    Document.Data.Tables.Add(tempTableName, databaseDataSource)
    Document.Data.Tables.Remove(tempTableName)


def getMarkedData():
    selectedNodeDataTableName = 'SelectedNodes'
    valData = getSelectedNodesNames(dataTableName=selectedNodeDataTableName)
    NodeType = getSelectedNodeType(dataTableName=selectedNodeDataTableName)
    print NodeType
    a = []
    for i in valData:
        a.append((CollectionName, i, NodeType))

    return ','.join("('{}', '{}', '{}')".format(i, j, k) for i, j, k in a)


nodeCollectionsDataTableName = 'NodeCollection'
nodeCollections = getNodeCollectionsNames(dataTableName=nodeCollectionsDataTableName)


Document.Properties[nodeCollectionsErrorPropertyName] = ''  # clear any existing warning
nodenames = getMarkedData()
writeNodeCollectionToDB(nodenames)
     #writeAlarmDefinitionToDB(alarmDefinition=[Document.Properties[propertyName.replace('_', '')] for propertyName in alarmColumns])


Document.Properties["selectedNodes"] = ""
Document.Data.Tables[nodeCollectionsDataTableName].Refresh()

Document.Properties["SelectedCollectionToModify"] = None
