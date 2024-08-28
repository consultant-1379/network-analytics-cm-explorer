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
# Name    : ClearAlarmDefinition.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from System import Array
from Spotfire.Dxp.Data import DataValueCursor, IndexSet
from Spotfire.Dxp.Data.Import import DatabaseDataSource, DatabaseDataSourceSettings


import sys
sys.path.append(ModulesService.GetResourceDirectoryPath("ericsson.scripts.custom_validate.py"))
from custom_validate import inValidForENM, validateEmptyFeilds


class AlarmState:
    Active = 'Active'
    Inactive = 'Inactive'


class AlarmColumn:
    AlarmName = 'Alarm_Name'
    AlarmType = 'Alarm_Type'
    KPIName = 'KPI_Name'
    Condition = 'Condition'
    ThresholdValue = 'Threshold_Value'
    Severity = 'Severity'  # AlarmLevel
    AlarmState = 'Alarm_State'
    NECollection = 'NE_Collection'  # NeList
    SpecificProblem = 'Specific_Problem'
    ProbableCause = 'Probable_Cause'
    LookbackMinutes = 'Lookback_minutes'
    Granularity = 'Granularity'
    Aggregation = 'Aggregation'
    KPI_Type = 'KPI_Type'


AlarmState = AlarmState()  # Create an enum to represent alarm states
AlarmColumn = AlarmColumn()  # Create an enum to represent column names
alarmColumns = [AlarmColumn.AlarmName, AlarmColumn.AlarmType, AlarmColumn.KPIName, AlarmColumn.Condition, AlarmColumn.ThresholdValue, AlarmColumn.Severity, AlarmColumn.NECollection, AlarmColumn.SpecificProblem, AlarmColumn.ProbableCause, AlarmColumn.LookbackMinutes, AlarmColumn.Granularity,AlarmColumn.Aggregation, AlarmColumn.KPI_Type, AlarmColumn.AlarmState]
alarmDefinitionErrorPropertyName = 'AlarmDefinitionError'
Document.Properties[alarmDefinitionErrorPropertyName] = ''


def updateAlarmDefinitionInDB(alarmDefinition):
    sqlTemplate = '''
UPDATE [dbo].[Alarm_Definitions]
   SET [Alarm_Type] = '%s'
      ,[KPI_Name] = '%s'
      ,[Condition] = '%s'
      ,[Threshold_Value] = '%s'
      ,[Severity] = '%s'
      ,[NE_Collection] = '%s'
      ,[Specific_Problem] = '%s'
      ,[Probable_Cause] = '%s'
      ,[Lookback_minutes] = '%s'
      ,[Granularity] = '%s'
      ,[Aggregation] = '%s'
      ,[KPI_Type] = '%s'
       ,[Alarm_State] = '%s'
 WHERE [Alarm_Name] = '%s'
'''
    print(alarmDefinition)
    print('Alarm Name = ', alarmDefinition[0])
    print('Alarm items = ', alarmDefinition[1:])
    print tuple(alarmDefinition[1:] + alarmDefinition[:1])
    sql = sqlTemplate % tuple(alarmDefinition[1:] + alarmDefinition[:1])  # Alarm Name is at the start of the list, but at the end of the query, so need to shuffle
    print('sql = %s' % sql)
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.SqlClient", "Server=atclvm1401.athtem.eei.ericsson.se;Database=alarm_db;UID=netanserver;PWD=Ericsson01", sql)
    tableName = 'temp'
    databaseDataSource = DatabaseDataSource(dataSourceSettings)
    newDataTable = Document.Data.Tables.Add(tableName, databaseDataSource)
    Document.Data.Tables.Remove(tableName)







def setValidationErrorMessage():
    isValid = True
    errorMessage = ""

    dp = {}
    dp["Alarm Name"] = Document.Properties['AlarmName']
    dp["Alarm Type"] = Document.Properties['AlarmType']
    dp["NE Collection"] = Document.Properties['NECollection']
    dp["MeasureInput"] = Document.Properties['KPIName']
    dp["Threshold Value Input"] = Document.Properties['ThresholdValue']
    dp["Probable Cause Input"] = Document.Properties['ProbableCause']
    dp["Specific Problem Input"] = Document.Properties['SpecificProblem']
    
    EmptyFields = validateEmptyFeilds(**dp)
    ENMValid = inValidForENM(dp["Alarm Name"], dp["Probable Cause Input"], dp["Specific Problem Input"])


    if len(EmptyFields)>0 :
        isValid = False
        errorMessage = " please provide Value for: " + str(EmptyFields)
    if not ENMValid:
        isValid = False
        errorMessage  += ", please remove '#' or '?' from the input fields"

    Document.Properties['ValidationError'] = errorMessage

    return isValid


alarmStateActive = 'Active'
alarmStateInactive = 'Inactive'
alarmDefinitionsDataTableName = 'Alarm Definitions'
dataTable = Document.Data.Tables[alarmDefinitionsDataTableName]
markedRowSelection = Document.ActiveMarkingSelectionReference.GetSelection(dataTable).AsIndexSet()
print alarmColumns
cursors = {column: DataValueCursor.CreateFormatted(dataTable.Columns[column]) for column in alarmColumns}



for row in dataTable.GetRows(markedRowSelection, Array[DataValueCursor](cursors.values())):
    if cursors[AlarmColumn.AlarmState].CurrentValue == alarmStateActive:
        Document.Properties[alarmDefinitionErrorPropertyName] = 'Error: Alarm "%s" not in valid state, state = %s' % (cursors[AlarmColumn.AlarmName].CurrentValue, cursors[AlarmColumn.AlarmState].CurrentValue)
    else:
        Document.Properties[alarmDefinitionErrorPropertyName] = ''  # clear any existing warning
        if setValidationErrorMessage():
            updateAlarmDefinitionInDB(alarmDefinition=[Document.Properties[propertyName.replace('_', '')] for propertyName in alarmColumns[:-1]] + [alarmStateInactive])
        else:
            print "please fix the erronous values"
Document.Data.Tables[alarmDefinitionsDataTableName].Refresh()