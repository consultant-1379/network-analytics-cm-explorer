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
# Name    : ClearAlarmDefinitionsValues.py
# Date    : 04/09/2019
# Revision: 1.0
# Purpose : Reset Alarm Rules Editor to default values once new Alarm
#           Defiition is created or changed and when switching between
#           tabs.
#
# Usage   : PM Alarms
#

Document.Properties['AlarmName'] = ''
Document.Properties['MeasureType'] = 'KPI'
Document.Properties['MeasureName'] = ''
Document.Properties['Condition'] = '<='
Document.Properties['ThresholdValue'] = 0.0
Document.Properties['Severity'] = 'MINOR'
Document.Properties['Granularity'] = '15'
Document.Properties['LookbackMinutes'] = '60'
Document.Properties['Aggregation'] = 'None'
Document.Properties['ProbableCause'] = ''
Document.Properties['SpecificProblem'] = ''