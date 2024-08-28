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
# Name    : SuspendResumeMarkedAlarm.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : changes the state of Alarm Defenitions
#
# Usage   : PM Alarms
#

# alarmState is an argument to the script
# should be a string with value of either "Active" or 'Inactive' or Delete

from System import Array
from Spotfire.Dxp.Data import DataValueCursor, IndexSet
from Spotfire.Dxp.Data.Import import DatabaseDataSource, DatabaseDataSourceSettings


class AlarmState:
    Active = 'Active'
    Inactive = 'Inactive'
    Deleted = 'Deleted'


class AlarmColumn:
    AlarmName = 'AlarmName'
    AlarmType = 'AlarmType'
    MeasureName = 'MeasureName'
    Condition = 'Condition'
    ThresholdValue = 'ThresholdValue'
    Severity = 'Severity'  #AlarmLevel
    AlarmState = 'AlarmState'
    NECollection = 'NECollection'  #NeList
    SpecificProblem = 'SpecificProblem'
    ProbableCause = 'ProbableCause'


AlarmState = AlarmState()  # Create an enum to represent alarm states
AlarmColumn = AlarmColumn()  # Create an enum to represent column names
alarmColumns = [AlarmColumn.AlarmName, AlarmColumn.AlarmType, AlarmColumn.MeasureName, AlarmColumn.Condition, AlarmColumn.ThresholdValue, AlarmColumn.Severity, AlarmColumn.AlarmState, AlarmColumn.NECollection, AlarmColumn.SpecificProblem, AlarmColumn.ProbableCause]
alarmDefinitionErrorPropertyName = 'AlarmDefinitionError'
Document.Properties[alarmDefinitionErrorPropertyName] = ''


def getAlarmDefinitions(dataTableName):
    alarmDefinitions = {}
    if Document.Data.Tables.Contains(dataTableName):
        dataTable = Document.Data.Tables[dataTableName]
        rows = IndexSet(dataTable.RowCount, True)
        print('Number of rules = %d' % rows.Count)
        cursors = {column: DataValueCursor.CreateFormatted(dataTable.Columns[column]) for column in alarmColumns}
        for row in dataTable.GetRows(rows, Array[DataValueCursor](cursors.values())):
            alarmDefinitions.update({cursors[AlarmColumn.AlarmName].CurrentValue: tuple(cursors[column].CurrentValue for column in alarmColumns[1:])})
    return alarmDefinitions



def updateAlarmDefinitionInDB(alarmName, alarmState):
    sqlTemplate = '''
UPDATE [dbo].[AlarmDefinitions]
   SET [AlarmState] = '%s'
 WHERE [AlarmName] = '%s'
'''
    print('Alarm Name = ', alarmName)
    print('Alarm State = ', alarmState)
    sql = sqlTemplate % (alarmState, alarmName)
    print('sql = %s' % sql)
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.SqlClient",
                                                    "Server=atclvm657.athtem.eei.ericsson.se;Database=alarm_db;UID=netanserver;PWD=Ericsson02", sql)
    tableName = 'temp'
    databaseDataSource = DatabaseDataSource(dataSourceSettings)
    newDataTable = Document.Data.Tables.Add(tableName, databaseDataSource)
    Document.Data.Tables.Remove(tableName)


if alarmState == 'Deleted':
	print("Hello World")
else:
	print("cannot Delete")

alarmDefinitionsDataTableName = 'Alarm Definitions'
alarmDefinitions = getAlarmDefinitions(dataTableName=alarmDefinitionsDataTableName)


dataTable = Document.Data.Tables[alarmDefinitionsDataTableName]
markedRowSelection = Document.ActiveMarkingSelectionReference.GetSelection(dataTable).AsIndexSet()
cursors = {column: DataValueCursor.CreateFormatted(dataTable.Columns[column]) for column in alarmColumns}

for row in dataTable.GetRows(markedRowSelection, Array[DataValueCursor](cursors.values())):
    if alarmState != cursors[AlarmColumn.AlarmState].CurrentValue:
        updateAlarmDefinitionInDB(alarmName=cursors[AlarmColumn.AlarmName].CurrentValue, alarmState = alarmState)
    # alarmState = 'Inactive' if cursors[AlarmColumn.AlarmState].CurrentValue == 'Active' else alarmState = 'Active'
        updateAlarmDefinitionInDB(alarmName=cursors[AlarmColumn.AlarmName].CurrentValue, alarmState=alarmState)
        Document.Properties["DeleteBtnInput"] = "Deleted"

Document.Data.Tables[alarmDefinitionsDataTableName].Refresh()
