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
# Name    : ProduceAlarms.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : Checks the alarms against ENIQ to see if threshold broken
#
# Usage   : PM Alarms
#

from Spotfire.Dxp.Data import *
from System import Array
from Spotfire.Dxp.Data import AddColumnsSettings, JoinType, DataColumnSignature, DataType
from Spotfire.Dxp.Framework.ApplicationModel import *
from Spotfire.Dxp.Data.Import import *
from System import DateTime
from collections import OrderedDict

dataSourceName = Document.Properties['ENIQDB']
ps = Application.GetService[ProgressService]()


def createCursor(eTable):
    """Create cursors for a given table, these are used to loop through columns

    Arguments:
        eTable {data table} -- table object

    Returns:
        cursDict -- dictionary of cursors for the given table
    """
    cursList = []
    colList = []
    for eColumn in eTable.Columns:
        cursList.append(DataValueCursor.CreateFormatted(eTable.Columns[eColumn.Name]))
        colList.append(eTable.Columns[eColumn.Name].ToString())
    cusrDict = dict(zip(colList, cursList))
    return cusrDict


def removeTable(tableName):
    """Remove the alarm table so that it can be repopulated

    Arguments:
        tableName {string} -- table to be removed from the analysis
    """
    if Document.Data.Tables.Contains(tableName):
        Document.Data.Tables.Remove(tableName)


def createNEList(NE_Collection):
    """Create a list of nodes for the node collections

    Arguments:
        NE_Collection {string} -- the name of the collection of nodes

    Returns:
        nodeList -- a comma seperated list of nodes for that collection
    """
    NEList = []
    activeCollection = nodeCollectionsDataTable.Select("[CollectionName] ='" + NE_Collection + "'")

    for nodes in nodeCollectionsDataTable.GetRows(activeCollection.AsIndexSet(), Array[DataValueCursor](nodeCollectionCur.values())):
        NEList.append(nodeCollectionCur['NodeName'].CurrentValue)

    #check if its a single node (i.e. an empty list because node not included in collection list)
    if not NEList:
        nodeList = "'" + NE_Collection + "'"
    else:
        nodeList = ','.join("'{}'".format(i) for i in NEList)

    return nodeList


def fetchDataFromENIQAsync(dataSourceSettings, tableName):
    """Run the sql query generated to populate the alarm table

    Arguments:
        dataSourceSettings {string} -- connection string and associated SQL query
        tableName {string} -- table to get the data from
    """

    try:
        dataTableDataSource = DatabaseDataSource(dataSourceSettings)
        print dataTableDataSource.Name
        # Check if Alarm Table already exists
        if Document.Data.Tables.Contains(tableName):
            print "Exists"

            AlarmDataTable = Document.Data.Tables[tableName]
            print AlarmDataTable.RowCount
            settings = AddRowsSettings(AlarmDataTable, dataTableDataSource)
            AlarmDataTable.AddRows(dataTableDataSource, settings)
        else:
            # Create Alarm Table if not already present
            print "Adding Data Table"
            AlarmDataTable = Document.Data.Tables.Add(tableName, dataTableDataSource)
            print AlarmDataTable.RowCount

        ps.CurrentProgress.CheckCancel()

    except:
        print "except"
        raise


def createElementList(kpiName, alarmName, formula, eniqKeys, eniqElementField, alarmDefAggr):
    """Creates the list of fields required for the alarms (e.g. moid, ossid)

    Arguments:
        kpiName {string} -- The name of the KPI/counter
        alarmName {string} -- The name given by the user for the alarm
        formula {string} -- the formula for the kpi/counter
        eniqKeys {string} -- the key fields for the table for the kpi etc.
        eniqElementField {string} -- the primary key for the table
        alarmDefAggr {string} -- the elvel of aggregation required, which affects how the data is returned

    Returns:
        col -- a dictionary of field names
    """
    col = OrderedDict()

    # for each element for the KPI, add a column entry
    eniqElementList = eniqKeys.split(",")
    for element in eniqElementList:
        if element != eniqElementField:
            col[element] = element

    # these following keys won't change, however the values will be dynamic
    col['ELEMENT'] = "{}".format(eniqElementField)

    # for the hour aggr, it needs to ignore the date field and aggregate based on the other fields
    if alarmDefAggr == '1 Day':
        col["DATE_ID"] = "DATE_ID"
    elif alarmDefAggr == '1 Hour':
        col["HOUR_ID"] = "HOUR_ID"
    else:
        col["UTC_DATETIME_ID"] = "UTC_DATETIME_ID"

    col["MeasureName"] = "'{}'".format(kpiName)
    col["ALARM_NAME"] = "'{}'".format(alarmName)
    col["KPI_VALUE"] = "({})".format(formula)

    return col


def generateSelectPart(col):
    """Generates the first part of the sql query

    Arguments:
        col {dict} -- a dicitonary of field names

    Returns:
        string -- concatenated version of the field list and joined to the SELECT part of the query
    """
    return "select " + ','.join('{} as "{}"'.format(str(val), str(key)) for key, val in col.items())


def generateSQLdateClause(tableName, granularity, aggr):
    """Generate SQL Date clause for a level of granularity in mins/day

    Arguments:
        tableName {string} -- table name for where clause, i.e.  FROM 'tableName'
        granularity {string} -- level of granularity required
        aggr {string} -- aggreagation level (hour, day etc.)

    Returns:
        sqlDate -- a string with the date selection in the WHERE clause
    """
    # Depending on granularity etc, need to change what date field is picked up for the database
    if aggr == "1 Day":
        dateID = "DATE_ID"
        datepart = "dd"
    else:
        dateID = "UTC_DATETIME_ID"  # This for both ROP and hour level
        datepart = "mi"

    sqlDate = "(" + dateID + " <= ( SELECT MAX(" + dateID + ") FROM " + tableName + ") \
        AND " + dateID + " >= (SELECT DATEADD(" + datepart + ", -" + granularity + " , MAX(" + dateID + "))  FROM " + tableName + "))"

    return sqlDate


def generateSQLThresholdClause(kpiFormula, condition, thresholdValue):
    """Generate SQL WHERE conditions for checking the KPI formula against the given threshold and condition (>,< etc. )

    Arguments:
        kpiFormula {string} -- formula for KPI
        condition {string} -- >,<,>= etc. for the where clause
        thresholdValue {string} -- the value to check the result of the formula against

    Returns:
        [type] -- [description]
    """
    sqlThresh = "(" + kpiFormula + ") " + condition + " " + thresholdValue

    return sqlThresh


def createSQLGroupBy(elementList):
    """Generate the SQL GROUP BY condtion - and ignore whatever values that dont need to be in the group by

    Arguments:
        elementList {dict} -- result of createElementList function

    Returns:
        string -- the formatted GROUP BY statement fields required
    """
    # ignore kpi name,alarm name, kpi value
    groupBy = []
    for value in elementList:
        if value not in ("MeasureName", "ALARM_NAME", "KPI_VALUE"):
            groupBy.append(value)
    return ','.join(groupBy)


def getFormula(kpiCursor, alarmDefKPI):
    """Find the formula for the given KPI

    Arguments:
        kpiCursor {[type]} -- column to search for in the KPI table
        alarmDefKPI {string} -- KPI name

    Returns:
        string -- kpi formula
    """
    for row in KPIDataTable.GetRows(kpiCursor.AsIndexSet(), Array[DataValueCursor](KPIDataTableCur.values())):
        if alarmDefKPI == KPIDataTableCur['KPIName'].CurrentValue:
            return KPIDataTableCur['KPI Formula'].CurrentValue


def parseFormula(KPIformula, counters, eniqTimeAggregation):
    """Parse the formula and replace the counter values with the aggregation type required

    Arguments:
        KPIformula {[string} -- the original kpi formula
        counters {string} -- a list of counters for the kpi, comma seperated
        eniqTimeAggregation {string} -- level of time aggregation for the kpi/counter

    Returns:
        string -- the formula that has the aggreagtion added in
    """
    splitCounters = counters.split(',')
    splitTimeAggregation = eniqTimeAggregation.split(',')

    for counter, aggrType in zip(splitCounters, splitTimeAggregation):
        aggrValue = aggrType + "(" + counter + ")"
        KPIformula = KPIformula.replace(counter, aggrValue)

    return KPIformula


def execute():
    """Get the active alarm definitions

    Returns:
        None
    """

    try:
        alarmTable = 'Alarm Table'
        removeTable(alarmTable)

        # get active alarms on alarm def table
        activeAlarms = alarmDefinitionsDataTable.Select("[AlarmState] = 'Active'")

        # for each alarm get kpi name to search against kpi tables etc.
        for alarmdef in alarmDefinitionsDataTable.GetRows(activeAlarms.AsIndexSet(), Array[DataValueCursor](alarmDefinitionsCur.values())):

            slectedKPI = KPIDataTable.Select("[KPIName]= '"+alarmDefinitionsCur['MeasureName'].CurrentValue+"'")

            alarmName = alarmDefinitionsCur['AlarmName'].CurrentValue
            alarmDefKPI = alarmDefinitionsCur['MeasureName'].CurrentValue
            alarmDefThresholdValue = alarmDefinitionsCur['ThresholdValue'].CurrentValue
            alarmDefCondition = alarmDefinitionsCur['Condition'].CurrentValue
            alarmDefGranularity = alarmDefinitionsCur['Granularity'].CurrentValue
            alarmDefAggr = alarmDefinitionsCur['Aggregation'].CurrentValue
            NEList = createNEList(alarmDefinitionsCur['NECollection'].CurrentValue)
            KPIType = alarmDefinitionsCur['MeasureType'].CurrentValue

            # TESTVALS
            # slectedKPI = KPIDataTable.Select("[KPIName]= 'PMIFSTATSIPOUTREQUESTS.DC_E_MGW_IPINTERFACE'")
            # alarmName = "pmIfStatsIpInReceives counter"
            # alarmDefKPI = "PMIFSTATSIPINRECEIVES.DC_E_MGW_IPINTERFACE"
            # alarmDefThresholdValue = "20"
            # alarmDefCondition =">"
            # alarmDefGranularity = "10"
            # NEList = createNEList("ieatnetsimv6083-23_K3C128801")
            # KPIType = "Counter"
            # test vals end

            slectedSearchKPI = KPITablesDataTable.Select("[MeasureName]= '" + alarmDefKPI + "'")
            # loop through KPI Tables to get counter, table name etc for KPI.
            maxReturn = 1  # ! : temp - this just return back one table for the kpi for now, not multiple
            count = 0

            for kpi in KPITablesDataTable.GetRows(slectedSearchKPI.AsIndexSet(), Array[DataValueCursor](kpiTablesCollectionCur.values())):
                currKPIName = kpiTablesCollectionCur['MeasureName'].CurrentValue

                if alarmDefKPI == currKPIName and count < maxReturn:
                    eniqtablename = kpiTablesCollectionCur['TABLENAME'].CurrentValue

                    # Append on to table name based on level of aggregation required
                    if alarmDefAggr == "1 Day":
                        modeniqtablename = eniqtablename + "_DAY"
                    else:
                        modeniqtablename = eniqtablename + "_RAW"

                        # ? flex counters, pdf counters

                    eniqCounters = kpiTablesCollectionCur['COUNTERS'].CurrentValue
                    eniqKeys = kpiTablesCollectionCur['KEYS'].CurrentValue
                    eniqElementField = kpiTablesCollectionCur['ELEMENT'].CurrentValue
                    eniqTimeAggregation = kpiTablesCollectionCur['TIMEAGGREGATION'].CurrentValue

                    count += 1

            if KPIType == "KPI":
                KPIformula = getFormula(slectedKPI, alarmDefKPI)
            else:
                # this is a counter, so just reuse the value in the counters field
                KPIformula = eniqCounters

            # surround each counter with the correct aggregation type for use in the sql query
            # ? what about none for time aggregation if this is a conuter
            manipulatedFormula = parseFormula(KPIformula, eniqCounters, eniqTimeAggregation)

            elementList = createElementList(alarmDefKPI, alarmName, manipulatedFormula, eniqKeys, eniqElementField,alarmDefAggr)

            # generate sql query
            # ! really should be updated to a parameterized query or converted to stored proc to avoid issue with the free text fields
            sql = generateSelectPart(elementList) + \
                " FROM " + modeniqtablename + \
                " WHERE" +\
                generateSQLdateClause(modeniqtablename, alarmDefGranularity, alarmDefAggr) + \
                " AND " +\
                generateSQLThresholdClause(KPIformula, alarmDefCondition, alarmDefThresholdValue) +\
                " AND " + \
                eniqElementField + " IN " + "(" + NEList + ")" +\
                " GROUP BY " +\
                createSQLGroupBy(elementList)

            print sql
            dataSourceSettings = DatabaseDataSourceSettings("System.Data.Odbc", "DSN=" + dataSourceName, sql)
            fetchDataFromENIQAsync(dataSourceSettings, alarmTable)
    except:
        raise


alarmDefinitionsDataTableName = 'Alarm Definitions'
alarmDefinitionsDataTable = Document.Data.Tables[alarmDefinitionsDataTableName]

KPIDataTableName = 'KPIs'
KPIDataTable = Document.Data.Tables[KPIDataTableName]

nodeCollectionsDataTableName = 'NodeCollection'
nodeCollectionsDataTable = Document.Data.Tables[nodeCollectionsDataTableName]

KPITablesDataTableName = 'KPI Tables'
KPITablesDataTable = Document.Data.Tables[KPITablesDataTableName]

# create cursors for tables
alarmDefinitionsCur = createCursor(alarmDefinitionsDataTable)
KPIDataTableCur = createCursor(KPIDataTable)
nodeCollectionCur = createCursor(nodeCollectionsDataTable)
kpiTablesCollectionCur = createCursor(KPITablesDataTable)


ps.ExecuteWithProgress("This is ExecuteWithProgress", 'Testing Connection to %s ...' % (dataSourceName), execute)
# Document.Properties["sendToENM"]=DateTime.UtcNow