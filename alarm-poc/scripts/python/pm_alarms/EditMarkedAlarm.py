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
# Name    : EditMarkedAlarm.py
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
    AlarmName = 'AlarmName'
    AlarmType = 'AlarmType'
    MeasureName = 'MeasureName'
    Condition = 'Condition'
    ThresholdValue = 'ThresholdValue'
    Severity = 'Severity'  # AlarmLevel
    AlarmState = 'AlarmState'
    NECollection = 'NECollection'  # NeList
    SpecificProblem = 'SpecificProblem'
    ProbableCause = 'ProbableCause'
    LookbackMinutes = 'LookbackMinutes'
    Granularity = 'Granularity'
    Aggregation = 'Aggregation'
    MeasureType = 'MeasureType'


AlarmState = AlarmState()  # Create an enum to represent alarm states
AlarmColumn = AlarmColumn()  # Create an enum to represent column names
alarmColumns = [AlarmColumn.AlarmName, AlarmColumn.AlarmType, AlarmColumn.MeasureName, AlarmColumn.Condition, AlarmColumn.ThresholdValue,
                AlarmColumn.Severity, AlarmColumn.NECollection, AlarmColumn.SpecificProblem, AlarmColumn.ProbableCause, AlarmColumn.LookbackMinutes,
                AlarmColumn.Granularity, AlarmColumn.Aggregation, AlarmColumn.MeasureType, AlarmColumn.AlarmState]
alarmDefinitionErrorPropertyName = 'AlarmDefinitionError'
Document.Properties[alarmDefinitionErrorPropertyName] = ''

def resetValues():
    Document.Properties['AlarmName'] = ''
    Document.Properties['AlarmType'] = 'Threshold'
    Document.Properties['NOCollection'] = ''
    Document.Properties['KPIType'] = 'Counter'
    Document.Properties['Condition'] = '<='
    Document.Properties['Severity'] = 'MINOR'
    Document.Properties['Granularity'] = '15'
    Document.Properties['LookbackMinutes'] = '60'
    Document.Properties['ProbableCause'] = ''
    Document.Properties['SpecificProblem'] = ''


def updateAlarmDefinitionInDB(alarmDefinition):
    sqlTemplate = '''
UPDATE [dbo].[AlarmDefinitions]
   SET [AlarmType] = '%s'
      ,[MeasureName] = '%s'
      ,[Condition] = '%s'
      ,[ThresholdValue] = '%s'
      ,[Severity] = '%s'
      ,[NECollection] = '%s'
      ,[SpecificProblem] = '%s'
      ,[ProbableCause] = '%s'
      ,[LookbackMinutes] = '%s'
      ,[Granularity] = '%s'
      ,[Aggregation] = '%s'
      ,[MeasureType] = '%s'
       ,[AlarmState] = '%s'
 WHERE [AlarmName] = '%s'
'''
    print(alarmDefinition)
    print('Alarm Name = ', alarmDefinition[0])
    print('Alarm items = ', alarmDefinition[1:])
    print tuple(alarmDefinition[1:] + alarmDefinition[:1])
    sql = sqlTemplate % tuple(alarmDefinition[1:] + alarmDefinition[:1])  # Alarm Name is at the start of the list, but at the end of the query, so need to shuffle
    print('sql = %s' % sql)
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.SqlClient",
                                                    "Server=atclvm1401.athtem.eei.ericsson.se;Database=alarm_db;UID=netanserver;PWD=Ericsson01", sql)
    tableName = 'temp'
    databaseDataSource = DatabaseDataSource(dataSourceSettings)
    newDataTable = Document.Data.Tables.Add(tableName, databaseDataSource)
    Document.Data.Tables.Remove(tableName)


alarmStateActive = 'Active'
alarmStateInactive = 'Inactive'
alarmDefinitionsDataTableName = 'Alarm Definitions'
dataTable = Document.Data.Tables[alarmDefinitionsDataTableName]
markedRowSelection = Document.ActiveMarkingSelectionReference.GetSelection(dataTable).AsIndexSet()

cursors = {column: DataValueCursor.CreateFormatted(dataTable.Columns[column]) for column in alarmColumns}



def ValidateErrors():
    isValid = True
    errorMessage = ""

    dp = {}
    dp["Alarm Name"] = Document.Properties['AlarmName']
    dp["Alarm Type"] = Document.Properties['AlarmType']

    singleNode = Document.Properties['NOCollection']
    if singleNode != '':
        Document.Properties['NECollection'] = singleNode

    dp["NE Collection"] = Document.Properties['NECollection']
    
    
    dp["Measure Input"] = Document.Properties['MeasureName']
    dp["Threshold ValueInput"] = str(Document.Properties['ThresholdValue'])
    dp["Probable Cause Input"] = Document.Properties['ProbableCause']
    dp["Specific Problem Input"] = Document.Properties['SpecificProblem']
    
    EmptyFields = validateEmptyFeilds(**dp)
    ENMValid = inValidForENM(dp["Alarm Name"], dp["Probable Cause Input"], dp["Specific Problem Input"])
    
    if len(EmptyFields)>0 :
        isValid = False
        errorMessage = " please provide Value for: " + str(EmptyFields)
    if ENMValid == False:
        isValid = False
        errorMessage  += ", please remove '#' or '?' from the input fields"

    Document.Properties['ValidationError'] = errorMessage

    return isValid


if ValidateErrors():
    for row in dataTable.GetRows(markedRowSelection, Array[DataValueCursor](cursors.values())):
        if cursors[AlarmColumn.AlarmState].CurrentValue == alarmStateActive:
            Document.Properties[alarmDefinitionErrorPropertyName] = 'Error: Alarm "%s" not in valid state, state = %s' % (cursors[AlarmColumn.AlarmName].CurrentValue, cursors[AlarmColumn.AlarmState].CurrentValue)
        else:
            Document.Properties[alarmDefinitionErrorPropertyName] = ''  # clear any existing warning
            # If its a single node then replace collection with that value
            updateAlarmDefinitionInDB(alarmDefinition=[Document.Properties[propertyName.replace('_', '')] for propertyName in alarmColumns[:-1]] + [alarmStateInactive])
            resetValues()

    Document.Data.Tables[alarmDefinitionsDataTableName].Refresh()
