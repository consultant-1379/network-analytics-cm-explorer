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
# Name    : PassAlarmState.py
# Date    : 05/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from System import Array
from Spotfire.Dxp.Data import DataValueCursor, IndexSet
from Spotfire.Dxp.Data.Import import DatabaseDataSource, DatabaseDataSourceSettings


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


alarmDefinitionsDataTableName = 'Alarm Definitions'
dataTable = Document.Data.Tables[alarmDefinitionsDataTableName]
markedRowSelection = Document.ActiveMarkingSelectionReference.GetSelection(dataTable).AsIndexSet()


cursors = {column: DataValueCursor.CreateFormatted(dataTable.Columns[column]) for column in alarmColumns}


for row in dataTable.GetRows(markedRowSelection, Array[DataValueCursor](cursors.values())):
    Document.Properties["ErrorInput"] = cursors[AlarmColumn.AlarmState].CurrentValue  


if markedRowSelection.Count == 0:
    Document.Properties["IsMarked"] = False
else:
    Document.Properties["IsMarked"] = True