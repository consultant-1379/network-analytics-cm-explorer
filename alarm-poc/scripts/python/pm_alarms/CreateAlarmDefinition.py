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
    LookBack = 'LookbackMinutes'
    Granularity = 'Granularity'
    Aggregation = 'Aggregation'
    MeasureType = 'KPIOrCounter'


AlarmState = AlarmState()  # Create an enum to represent alarm states
AlarmColumn = AlarmColumn()  # Create an enum to represent column names
alarmColumns = [AlarmColumn.AlarmName, AlarmColumn.AlarmType, AlarmColumn.MeasureName, AlarmColumn.Condition, AlarmColumn.ThresholdValue,
                AlarmColumn.Severity, AlarmColumn.NECollection, AlarmColumn.AlarmState, AlarmColumn.SpecificProblem, AlarmColumn.ProbableCause,
                AlarmColumn.LookBack, AlarmColumn.Granularity, AlarmColumn.Aggregation, AlarmColumn.MeasureType]
alarmDefinitionErrorPropertyName = 'AlarmDefinitionError'
Document.Properties[alarmDefinitionErrorPropertyName] = ''


# function
def getAlarmDefinitionsNames(dataTableName):
    alarmDefinitions = []
    if Document.Data.Tables.Contains(dataTableName):
        dataTable = Document.Data.Tables[dataTableName]
        rows = IndexSet(dataTable.RowCount, True)
        print('Number of alarm definitions = %d' % rows.Count)
        cursor = DataValueCursor.CreateFormatted(dataTable.Columns[AlarmColumn.AlarmName])
        for row in dataTable.GetRows(rows, cursor):
            alarmDefinitions.append(cursor.CurrentValue)
    return alarmDefinitions


# function
def writeAlarmDefinitionToDB(alarmDefinition):
    sqlTemplate = '''
INSERT INTO [dbo].[AlarmDefinitions]
           ([AlarmName]
           ,[AlarmType]
           ,[MeasureName]
           ,[Condition]
           ,[ThresholdValue]
           ,[Severity]
           ,[NECollection]
           ,[AlarmState]
           ,[SpecificProblem]
           ,[ProbableCause]
           ,[LookbackMinutes]
           ,[Granularity]
           ,[Aggregation]
           ,[MeasureType])
     VALUES
           ('%s'
           ,'%s'
           ,'%s'
           ,'%s'
           ,'%s'
           ,'%s'
           ,'%s'
           ,'%s'
           ,'%s'
           ,'%s'
           ,'%s'
           ,'%s'
           ,'%s'
           ,'%s')
'''
    print('Alarm Definition = ', alarmDefinition)
    sql = sqlTemplate % tuple(alarmDefinition)
    print('sql = %s' % sql)
    print(sql)
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.SqlClient",
                                                    "Server=atclvm1401.athtem.eei.ericsson.se;Database=alarm_db;UID=netanserver;PWD=Ericsson01", sql)
    tempTableName = 'temp'
    databaseDataSource = DatabaseDataSource(dataSourceSettings)
    Document.Data.Tables.Add(tempTableName, databaseDataSource)
    Document.Data.Tables.Remove(tempTableName)

def resetValues():
    Document.Properties['AlarmName'] = ''
    Document.Properties['Severity'] = 'MINOR'
    Document.Properties['Granularity'] = '15'
    Document.Properties['LookbackMinutes'] = '60'
    Document.Properties['ProbableCause'] = ''
    Document.Properties['SpecificProblem'] = ''
    Document.Properties["ValidationError"] = ''

alarmDefinitionsDataTableName = 'Alarm Definitions'
alarmDefinitions = getAlarmDefinitionsNames(dataTableName=alarmDefinitionsDataTableName)


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


newAlarmName = Document.Properties[AlarmColumn.AlarmName]
print Document.Properties[AlarmColumn.AlarmName]

if ValidateErrors():
    if newAlarmName in alarmDefinitions:
        Document.Properties[alarmDefinitionErrorPropertyName] = 'Error: Alarm Definition "%s" already exists' % newAlarmName
    else:
        Document.Properties[alarmDefinitionErrorPropertyName] = ''  # clear any existing warning
        Document.Properties['AlarmState'] = AlarmState.Inactive  # all new Alarms are Inactive by default
        #If its a single node then replace collection with that value
        

        writeAlarmDefinitionToDB(alarmDefinition=[Document.Properties[propertyName.replace('_', '')] for propertyName in alarmColumns])
        Document.Properties["ValidationError"] = ""
        resetValues()
    

Document.Data.Tables[alarmDefinitionsDataTableName].Refresh()
