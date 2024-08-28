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
# Name    : LoadMarkedAlarm.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from Spotfire.Dxp.Data import DataValueCursor, IndexSet
from System import Array
# import sys
# sys.path.append(ModulesService.GetResourceDirectoryPath("pmalarms.py"))
# from pmalarms import alarmColumns, alarmDefinitionsDataTable


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
    LookBack = 'Lookbackminutes'
    Granularity = 'Granularity'
    Aggregation = 'Aggregation'
    MeasureType = 'MeasureType'


AlarmColumn = AlarmColumn()  # Create an enum to represent column names
alarmColumns = [AlarmColumn.AlarmName, AlarmColumn.AlarmType, AlarmColumn.MeasureName, AlarmColumn.Condition, AlarmColumn.ThresholdValue,
                AlarmColumn.Severity, AlarmColumn.NECollection, AlarmColumn.AlarmState, AlarmColumn.SpecificProblem, AlarmColumn.ProbableCause,
                AlarmColumn.LookBack, AlarmColumn.Granularity, AlarmColumn.Aggregation, AlarmColumn.MeasureType]

alarmDefinitionsDataTableName = 'Alarm Definitions'
alarmDefinitionsDataTable = Document.Data.Tables[alarmDefinitionsDataTableName]

markedRowSelection = Document.ActiveMarkingSelectionReference.GetSelection(alarmDefinitionsDataTable).AsIndexSet()

cursors = {column: DataValueCursor.CreateFormatted(alarmDefinitionsDataTable.Columns[column]) for column in alarmColumns}

for row in alarmDefinitionsDataTable.GetRows(markedRowSelection, Array[DataValueCursor](cursors.values())):
    for propertyName in alarmColumns:
        print('old %s' % Document.Properties[propertyName.replace('_', '')])
        print('new %s' % cursors[propertyName].CurrentValue)
        Document.Properties[propertyName.replace('_', '')] = cursors[propertyName].CurrentValue
