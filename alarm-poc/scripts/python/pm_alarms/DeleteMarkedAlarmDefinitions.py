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
# Name    : DeleteMarkedAlarmDefinitions.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from Spotfire.Dxp.Data import DataValueCursor, IndexSet
from Spotfire.Dxp.Data.Import import DatabaseDataSource, DatabaseDataSourceSettings


class AlarmColumn:
    AlarmName = 'AlarmName'
    AlarmType = 'AlarmType'
    KPIName = 'MeasureName'
    Condition = 'Condition'
    ThresholdValue = 'ThresholdValue'
    Severity = 'Severity'  # AlarmLevel
    AlarmState = 'AlarmState'
    NECollection = 'NECollection'  # NeList
    SpecificProblem = 'SpecificProblem'
    ProbableCause = 'ProbableCause'


def deleteAlarmDefinitionInDB(alarmName):
    sqlTemplate = '''
DELETE FROM [dbo].[AlarmDefinitions]
      WHERE [Alarm_Name] = '%s'
'''
    print('Alarm Name = ', alarmName)
    sql = sqlTemplate % alarmName
    print('sql = %s' % sql)
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.SqlClient",
                                                    "Server=atclvm657.athtem.eei.ericsson.se;Database=alarm_db;UID=netanserver;PWD=Ericsson02", sql)
    tempTableName = 'temp'
    databaseDataSource = DatabaseDataSource(dataSourceSettings)
    Document.Data.Tables.Add(tempTableName, databaseDataSource)
    Document.Data.Tables.Remove(tempTableName)


AlarmColumn = AlarmColumn()  # Create an enum to represent column names
alarmColumns = [AlarmColumn.AlarmName, AlarmColumn.AlarmType, AlarmColumn.MeasureName, AlarmColumn.Condition, AlarmColumn.ThresholdValue,
                AlarmColumn.Severity, AlarmColumn.AlarmState, AlarmColumn.NECollection, AlarmColumn.SpecificProblem, AlarmColumn.ProbableCause]

alarmDefinitionsDataTableName = 'Alarm Definitions'
alarmDefinitionsDataTable = Document.Data.Tables[alarmDefinitionsDataTableName]
markedRowSelection = Document.ActiveMarkingSelectionReference.GetSelection(alarmDefinitionsDataTable).AsIndexSet()
cursor = DataValueCursor.CreateFormatted(alarmDefinitionsDataTable.Columns[AlarmColumn.AlarmName])

for row in alarmDefinitionsDataTable.GetRows(markedRowSelection, cursor):
    deleteAlarmDefinitionInDB(alarmName=cursor.CurrentValue)

Document.Data.Tables[alarmDefinitionsDataTableName].Refresh()
Document.Properties["DeleteBtnInput"] = "Deleted"