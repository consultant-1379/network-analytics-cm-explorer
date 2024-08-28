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
    LookBack = 'Lookback_minutes'
    Granularity = 'Granularity'
    Aggregation = 'Aggregation'
    KPI_Type = 'KPIOrCounter'


AlarmState = AlarmState()  # Create an enum to represent alarm states
AlarmColumn = AlarmColumn()  # Create an enum to represent column names
alarmColumns = [AlarmColumn.AlarmName, AlarmColumn.AlarmType, AlarmColumn.KPIName, AlarmColumn.Condition, AlarmColumn.ThresholdValue,
                AlarmColumn.Severity, AlarmColumn.NECollection, AlarmColumn.AlarmState, AlarmColumn.SpecificProblem, AlarmColumn.ProbableCause,
                AlarmColumn.LookBack, AlarmColumn.Granularity, AlarmColumn.Aggregation, AlarmColumn.KPI_Type]
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
INSERT INTO [dbo].[Alarm_Definitions]
           ([Alarm_Name]
           ,[Alarm_Type]
           ,[KPI_Name]
           ,[Condition]
           ,[Threshold_Value]
           ,[Severity]
           ,[NE_Collection]
           ,[Alarm_State]
           ,[Specific_Problem]
           ,[Probable_Cause]
           ,[Lookback_minutes]
           ,[Granularity]
           ,[Aggregation]
           ,[KPI_Type])
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
    sql = sqlTemplate % tuple(alarmDefinition)
    dataSourceSettings = DatabaseDataSourceSettings("System.Data.SqlClient",
                                                    "Server=atclvm1401.athtem.eei.ericsson.se;Database=alarm_db;UID=netanserver;PWD=Ericsson01", sql)
    tempTableName = 'temp'
    databaseDataSource = DatabaseDataSource(dataSourceSettings)
    Document.Data.Tables.Add(tempTableName, databaseDataSource)
    Document.Data.Tables.Remove(tempTableName)

def resetValues():
    Document.Properties['AlarmName'] = ''
    #Document.Properties['AlarmType'] = 'Threshold'
    #Document.Properties['NECollection'] = ''
    #Document.Properties['NOCollection'] = ''
    #Document.Properties['KPIType'] = 'Counter'
    #Document.Properties['KPIName'] = ''
    #Document.Properties['Condition'] = '<='
    #Document.Properties['ThresholdValue'] = ''
    Document.Properties['Severity'] = 'MINOR'
    Document.Properties['Granularity'] = '15'
    Document.Properties['LookbackMinutes'] = '60'
    #Document.Properties['Aggregation'] = ''
    Document.Properties['ProbableCause'] = ''
    Document.Properties['SpecificProblem'] = ''
    Document.Properties["ValidationError"] = ''

alarmDefinitionsDataTableName = 'Alarm Definitions'
alarmDefinitions = getAlarmDefinitionsNames(dataTableName=alarmDefinitionsDataTableName)

newAlarmName = Document.Properties[AlarmColumn.AlarmName.replace('_', '')]

def setValidationErrorMessage():
    isValid = True
    errorMessage = ""

    dp = {}
    dp["Alarm Name"] = Document.Properties['AlarmName']
    dp["Alarm Type"] = Document.Properties['AlarmType']
    dp["NE Collection"] = Document.Properties['NECollection']
    dp["MeasureInput"] = Document.Properties['KPIName']
    dp["ThresholdValueInput"] = Document.Properties['ThresholdValue']
    dp["ProbableCauseInput"] = Document.Properties['ProbableCause']
    dp["SpecificProblemInput"] = Document.Properties['SpecificProblem']
    
    EmptyFields = validateEmptyFeilds(**dp)
    ENMValid = inValidForENM(dp["Alarm Name"], dp["ProbableCauseInput"], dp["SpecificProblemInput"])
    
    if len(EmptyFields)>0 :
        isValid = False
        errorMessage = " please provide Value for: " + str(EmptyFields)
    if ENMValid == False:
        isValid = False
        errorMessage  += ", please remove '#' or '?' from the input fields"

    Document.Properties['ValidationError'] = errorMessage

    return isValid


if setValidationErrorMessage():
    if newAlarmName in alarmDefinitions:
        Document.Properties[alarmDefinitionErrorPropertyName] = 'Error: Alarm Definition "%s" already exists' % newAlarmName
    else:
        Document.Properties[alarmDefinitionErrorPropertyName] = ''  # clear any existing warning
        Document.Properties['AlarmState'] = AlarmState.Inactive  # all new Alarms are Inactive by default
        #If its a single node then replace collection with that value
        singleNode = Document.Properties['NOCollection']
        if singleNode != '':
            Document.Properties['NECollection'] = singleNode

        writeAlarmDefinitionToDB(alarmDefinition=[Document.Properties[propertyName.replace('_', '')] for propertyName in alarmColumns])
        Document.Properties["ValidationError"] = ""
        resetValues()
      

Document.Data.Tables[alarmDefinitionsDataTableName].Refresh()
