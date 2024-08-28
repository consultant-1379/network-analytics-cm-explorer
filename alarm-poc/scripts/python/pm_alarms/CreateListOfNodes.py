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
# Name    : CreateListOfNodes.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : create list of nodes from add button
#
# Usage   : PM Alarms
#

import clr
clr.AddReference('System.Data')  # needs to be imported before System.Data is called

import System
from System.Data import DataSet, DataTable, XmlReadMode
from Spotfire.Dxp.Data import DataType, DataTableSaveSettings, AddRowsSettings
from System.IO import StringReader, StreamReader, StreamWriter, MemoryStream, SeekOrigin
from System.Threading import Thread
from Spotfire.Dxp.Data import IndexSet
from Spotfire.Dxp.Data import RowSelection
from Spotfire.Dxp.Data import DataValueCursor
from Spotfire.Dxp.Data import DataSelection
from Spotfire.Dxp.Data import DataPropertyClass
from Spotfire.Dxp.Data import Import
from System.Net import HttpWebRequest
from Spotfire.Dxp.Data.Import import TextFileDataSource, TextDataReaderSettings
from Spotfire.Dxp.Data.Import import DatabaseDataSource, DatabaseDataSourceSettings




class NodeCollectionColumn:
    Collection_Name = 'CollectionName'
    Node_Name = 'NodeName'
    Node_Type = 'NodeType'


NodeCollectionColumn = NodeCollectionColumn()

NodeListDP = Document.Properties['NodeList']
NodeTypeDP = Document.Properties['NodeType']
#Collection_Name = Document.Properties['CollectionName']
Collection_Name = Document.Properties["SelectedCollectionToModify"]
#print Collection_Name
if Collection_Name is None:
    Collection_Name = Document.Properties['CollectionName']


selectedNodeDataTableName = 'SelectedNodes'
nodeCollectionsDataTableName = 'NodeCollection'
NodeListDataTable = Document.Data.Tables['NodeList']

NodesInNodeList = DataValueCursor.CreateFormatted(NodeListDataTable.Columns["node"])
NodeTypeInNodeList = DataValueCursor.CreateFormatted(NodeListDataTable.Columns["NodeType"])

selectedNodeDataTable = Document.Data.Tables["SelectedNodes"]


# valData=[]
def getSelectedNodesNames(dataTableName):
    selectedNodesNames = []
    selectedNodeType= []
    if Document.Data.Tables.Contains(dataTableName):
        dataTable = Document.Data.Tables[dataTableName]
        cursor = DataValueCursor.CreateFormatted(dataTable.Columns[NodeCollectionColumn.Node_Name])
        # cursor2 = DataValueCursor.CreateFormatted(dataTable.Columns[NodeCollectionColumn.Node_Type])
        rows = IndexSet(dataTable.RowCount, True)

        for row in dataTable.GetDistinctRows(rows, cursor):
            selectedNodesNames.append(cursor.CurrentValue)
            selectedNodeType.append(cursor.CurrentValue)
    return selectedNodesNames


valData = getSelectedNodesNames(dataTableName=selectedNodeDataTableName)


def getNodeType(dataTableName):
    selectedNopdeType = ""
    if Document.Data.Tables.Contains(dataTableName):
        dataTable = Document.Data.Tables[dataTableName]
        cursor = DataValueCursor.CreateFormatted(dataTable.Columns[NodeCollectionColumn.Node_Type])
        rows = IndexSet(dataTable.RowCount, True)
        for row in range(0, 1):
            selectedNopdeType = dataTable.Columns['NodeType'].RowValues.GetFormattedValue(row)
        # NodeType of 1st Row of column nodetype
    return selectedNopdeType


dataTable = DataTable("temp")
dataTable.Columns.Add(NodeCollectionColumn.Collection_Name, System.String)
dataTable.Columns.Add(NodeCollectionColumn.Node_Name, System.String)
dataTable.Columns.Add(NodeCollectionColumn.Node_Type, System.String)


## Getting the Node type from verifying, requires an extra loop and check
'''
for node in NodeListDP:
    if node not in valData:
        for row in NodeListDataTable.GetRows(NodesInNodeList, NodeTypeInNodeList):
            if node == NodesInNodeList.CurrentValue:
                nodeType = NodeTypeInNodeList.CurrentValue
                dt = dataTable.NewRow()
                dt[NodeCollectionColumn.Collection_Name] = Collection_Name
                dt[NodeCollectionColumn.Node_Name] = node
                dt[NodeCollectionColumn.Node_Type] = nodeType
                dataTable.Rows.Add(dt)
'''


def verifyNodeType(dataTableNodeType, NodeType):
    if dataTableNodeType == NodeType:
        return True
    else:
        return False


for node in NodeListDP:
    if node not in valData:
        if selectedNodeDataTable.RowCount == 0 or verifyNodeType(getNodeType(dataTableName=selectedNodeDataTableName), NodeTypeDP) == True:
            print "Adding Nodes"
            dt = dataTable.NewRow()
            dt[NodeCollectionColumn.Collection_Name] = Collection_Name
            dt[NodeCollectionColumn.Node_Name] = node
            dt[NodeCollectionColumn.Node_Type] = getNodeType("NodeList")
            dataTable.Rows.Add(dt)
            Document.Properties['ActionMessage'] = "Nodes Added"
        else:
            print "Nodes Cant be added"
            Document.Properties['ActionMessage'] = "Please select the same node type"


textData = "CollectionName\tNodeName\tNodeType\r\n"
for row in dataTable.Rows:
    textData += row[NodeCollectionColumn.Collection_Name] + "\t" + row[NodeCollectionColumn.Node_Name] + "\t" + row[NodeCollectionColumn.Node_Type] + "\r\n"
print textData

if textData != "CollectionName\tNodeName\tNodeType\r\n":
    stream = MemoryStream()
    writer = StreamWriter(stream)
    writer.Write(textData)
    writer.Flush()
    stream.Seek(0, SeekOrigin.Begin)

    readerSettings = TextDataReaderSettings()
    readerSettings.Separator = "\t"
    readerSettings.AddColumnNameRow(0)
    readerSettings.SetDataType(0, DataType.String)
    readerSettings.SetDataType(1, DataType.String)
    readerSettings.SetDataType(2, DataType.String)

    dSource = TextFileDataSource(stream, readerSettings)

    if Document.Data.Tables.Contains(selectedNodeDataTableName):
        settings = AddRowsSettings(Document.Data.Tables["SelectedNodes"],dSource)
        Document.Data.Tables["SelectedNodes"].AddRows(dSource, settings)

























