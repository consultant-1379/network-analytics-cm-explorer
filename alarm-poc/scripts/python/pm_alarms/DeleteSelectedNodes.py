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
# Name    : DeleteSelectedNodes.py
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

    Document.Properties['ActionMessage'] = "Node Collection Deleted"
    sql = sqlTemplate % collection_name
    print('sql = %s' % sql)
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.SqlClient",
                                                    "Server=atclvm657.athtem.eei.ericsson.se;Database=alarm_db;UID=netanserver;PWD=Ericsson02", sql)
    tempTableName = 'temp'
    databaseDataSource = DatabaseDataSource(dataSourceSettings)
    Document.Data.Tables.Add(tempTableName, databaseDataSource)
    Document.Data.Tables.Remove(tempTableName)


deleteNodeCollection(CollectionName)
deleteNodeCollectionFromTable(CollectionName)
Document.Properties["selectedNodes"] = ""
Document.Properties["SelectedCollectionToModify"] = None
Document.Data.Tables['NodeCollection'].Refresh()