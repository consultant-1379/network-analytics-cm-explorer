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
# Name    : AddSelectedNodes.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from Spotfire.Dxp.Data import DataValueCursor, IndexSet
from Spotfire.Dxp.Data.Import import DatabaseDataSource, DatabaseDataSourceSettings


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
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.SqlClient", "Server=atclvm657.athtem.eei.ericsson.se;Database=alarm_db;UID=netanserver;PWD=Ericsson02", sql)
    tempTableName = 'temp'
    databaseDataSource = DatabaseDataSource(dataSourceSettings)
    Document.Data.Tables.Add(tempTableName, databaseDataSource)
    Document.Data.Tables.Remove(tempTableName)


def getMarkedData():
    Collection_Name = Document.Properties['CollectionName']
    selectedNodeDataTableName = 'SelectedNodes'
    valData = getSelectedNodesNames(dataTableName=selectedNodeDataTableName)
    NodeType = getSelectedNodeType(dataTableName=selectedNodeDataTableName)
    a = []
    for i in valData:
        a.append((Collection_Name, i, NodeType))

    return ','.join("('{}', '{}', '{}')".format(i, j, k) for i, j, k in a)


Collection_Name = Document.Properties['CollectionName']
nodeCollectionsDataTableName = 'NodeCollection'
nodeCollections = getNodeCollectionsNames(dataTableName=nodeCollectionsDataTableName)


newCollectionName = Document.Properties[NodeCollectionColumn.CollectionName.replace('_', '')]
if newCollectionName in nodeCollections:
    Document.Properties[nodeCollectionsErrorPropertyName] = 'Error: Collection Name "%s" already exists' % newCollectionName
    print "Collection Name %s already exists" % newCollectionName
else:
    Document.Properties[nodeCollectionsErrorPropertyName] = ''  # clear any existing warning
    nodenames = getMarkedData()
    writeNodeCollectionToDB(nodenames)
    #writeAlarmDefinitionToDB(alarmDefinition=[Document.Properties[propertyName.replace('_', '')] for propertyName in alarmColumns])

Document.Data.Tables[nodeCollectionsDataTableName].Refresh()
Document.Properties["selectedNodes"] = ""
Document.Properties["SelectedCollectionToModify"] = None
