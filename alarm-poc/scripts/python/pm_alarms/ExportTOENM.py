
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
# Name    : ExportTOENM.py
# Date    : 08/30/2019
# Revision: 1.0
# Purpose : Exports triggered alarm rules to ENM through REST
#
# Usage   : PM Alarm
#

import clr
clr.AddReference('System.Data')
import System.Web
from Spotfire.Dxp.Data import *
from System.IO import StreamReader
from System import Uri
from System.Net import ServicePointManager, SecurityProtocolType, WebRequest, CookieContainer
from System.Data.Odbc import OdbcConnection
from datetime import datetime

clr.AddReference('System.Web.Extensions')
ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12
dataSourceName = Document.Properties['ENIQDB']


def createRequest(url, method):
    """Function that accepts url and method (POST,PUT) and creates request, and stores session

    Arguments:
        url {Uri} -- url used to connect to ENM
        method {string} -- defines whether a POST or PUT request is needed

    Returns:
        request -- [description]
    """
    request = WebRequest.Create(url)
    request.Method = method
    request.Timeout = 50000
    request.Accept = "application/json"
    request.ContentType = "application/json"
    request.CookieContainer = CookieContainer()
    return request


def createCookies(request, urlLogin):
    """Gets cookies for current session

    Arguments:
        request {httprequest} -- current connection to enm - created by createRequest()
        urlLogin {Uri} -- url used to connect to ENM

    Returns:
        cookies -- returns current cookies for session
    """
    cookies = request.CookieContainer.GetCookies(urlLogin)
    return cookies


def putRequest(request, cookies, json):
    """For the session, send json data to the server - in this case send to ENM

    Arguments:
        request {httprequest} -- current connection to enm - created by createRequest()
        cookies {cookies} -- current cookies for session
        json {string} -- JSON used to send details to ENM
    """
    request.CookieContainer.Add(cookies)
    buffer = System.Text.Encoding.ASCII.GetBytes(json)
    streamWriter = request.GetRequestStream()
    streamWriter.Write(buffer, 0, len(buffer))
    streamWriter.Close()


def getResponse(response):
    """For any request, get the response stream and then close out streams

    Arguments:
        response {httpresponse} -- result of the response of the request
    """
    stream = response.GetResponseStream()
    streamReader = StreamReader(stream)
    content = streamReader.ReadToEnd()

    print(content)

    streamReader.Close()
    response.Close()
    stream.Close()


def sqlEniq(sql):
    """ Run a SQL query against the ENIQ server using ODBC connection

    Arguments:
        sql {string} -- A SQL query string
    """

    #set connection and execute
    conn_string = "DSN=" + dataSourceName
    connection = OdbcConnection(conn_string)
    connection.Open()
    command = connection.CreateCommand()
    command.CommandText = sql
    command.ExecuteReader()
    connection.Close()


def logErrorMessage(ENMHostname, errorDetail, alarmName, managedObjectInstance, objectOfReference, ossName, reportTitle, eventTime):
    """Log error messages for connection issues, json issues etc.

    Arguments:
        ENMHostname {string} -- ENM server name
        ErrorDetail {string} -- Error message (json, connection error etc.)
        AlarmName {string} -- Alarm rule name
        ManagedObjectInstance {string} -- [description]
        ObjectOfReference {string} -- node detail
        OssName {string} -- oss name
        ReportTitle {string} -- using 'PM Alarm' mainly, but can be any value. ReportTitle is from BO version
        EventTime {string} -- time in which the error message is sent to the db
    """

    sql = "INSERT INTO DC_Z_ALARM_ERROR (ENMHostname, ErrorDetail, AlarmName ,ManagedObjectInstance ,ObjectOfReference ,OssName ,ReportTitle ,EventTime) VALUES ('" \
        + ENMHostname \
        + "','" \
        + errorDetail.replace("'", "''") \
        + "','" \
        + alarmName \
        + "','" \
        + managedObjectInstance \
        + "','" \
        + objectOfReference \
        + "','" \
        + ossName \
        + "','" \
        + reportTitle \
        + "','" + eventTime + "')"
    print sql
    sqlEniq(sql)


def findCurrentPartition():

    sql = "SELECT tableName FROM DWHPARTITION WHERE CURRENT DATE BETWEEN STARTTIME AND ENDTIME AND STORAGEID IN ('DC_Z_ALARM_INFO:RAW')"
    conn_string = "DSN=" + dataSourceName + "repdb"
    connection = OdbcConnection(conn_string)
    connection.Open()
    command = connection.CreateCommand()
    command.CommandText = sql
    reader = command.ExecuteReader()
    loopguard = 0
    while reader.Read() and loopguard != 1:  #! adding loop guard as more testing requried if multiple would be returned or while loop would break?
        currentPartition = reader[0]
        loopguard = 1
    connection.Close()
    return currentPartition

def logAlarm(alarmName, reportTitle, ossName, objectOfReference, managedObjectInstance, perceivedSeverity, eventTime):
    """Log all alarms that have breached the threshold (i.e. any alarms on the alarm table built by the produce alarm script)

    Arguments:
        alarmName {string} -- Alarm rule name
        reportTitle {string} -- using 'PM Alarm' mainly, but can be any value. ReportTitle is from BO version
        ossName {string} -- oss name
        objectOfReference {string} -- node detail
        managedObjectInstance {string} -- [description]
        perceivedSeverity {string} -- Severity level of alarm
        eventTime {string} -- time in which the alarm log message is sent to the db
    """
    # todo add the stored procedure to choose which partition to store the data on
    currPartition = findCurrentPartition()
    print currPartition
    sql = "INSERT INTO " + currPartition + " (AlarmName, ReportTitle, OssName, ObjectOfReference, ManagedObjectInstance, PerceivedSeverity, EventDate) VALUES ('" \
        + alarmName \
        + "','" \
        + reportTitle \
        + "','" \
        + ossName \
        + "','" \
        + objectOfReference \
        + "','" \
        + managedObjectInstance \
        + "','" \
        + perceivedSeverity \
        + "','" \
        + eventTime + "')"
    print sql
    sqlEniq(sql)


# create request to server and get cookies for session
serverName = Document.Properties['ENMDB']
enmUserName = Document.Properties['ENMUserName']
enmPassword = Document.Properties['ENMPassword']
urlLogin = Uri("https://" + serverName + "/login?IDToken1="+ enmUserName +"&IDToken2=" + enmPassword)  # todo update to select fields from admin

try:
    intialRequest = createRequest(urlLogin, "POST")
    intialResponse = intialRequest.GetResponse()

    cookies = createCookies(intialRequest, urlLogin)
    getResponse(intialResponse)
except Exception as e:
    errorDetail = e.message
    logErrorMessage(serverName, errorDetail, '-', '-', '-', '-', 'PM Alarm', str(datetime.utcnow()))

# get alarm defintion table
alarmDefinitionsDataTableName = 'Alarm Definitions'
alarmDefinitionsDataTable = Document.Data.Tables[alarmDefinitionsDataTableName]

# create cursors for alarm defintion
alarmDefinitionSpecificProblem = DataValueCursor.CreateFormatted(alarmDefinitionsDataTable.Columns["SpecificProblem"])
alarmDefinitionAlarmName = DataValueCursor.CreateFormatted(alarmDefinitionsDataTable.Columns["AlarmName"])
alarmDefinitionProbableCause = DataValueCursor.CreateFormatted(alarmDefinitionsDataTable.Columns["ProbableCause"])
alarmDefinitionSeverity = DataValueCursor.CreateFormatted(alarmDefinitionsDataTable.Columns["Severity"])
alarmDefinitionEventType = DataValueCursor.CreateFormatted(alarmDefinitionsDataTable.Columns["AlarmType"])

# get alarm table name and cursor
alarmTableName = 'Alarm Table'
alarmTable = Document.Data.Tables[alarmTableName]
alarmTableCursor = DataValueCursor.CreateFormatted(alarmTable.Columns["ALARM_NAME"])
alarmTableCursorElement = DataValueCursor.CreateFormatted(alarmTable.Columns["ELEMENT"])

# set rowcount for import
rowCount = alarmTable.RowCount
rowsToInclude = IndexSet(rowCount, True)
count = 0

# set max amount of rows to import, so as to not flood the server with requests
# maxRowAmount = 20  #! commenting out as this needs to be handled with a queue etc. - EQEV-67809

# loop through each alarm in PM alarm table (i.e. alarms that broke threshold) and find corresponding details in alarm definitions table
for row in alarmTable.GetRows(alarmTableCursor, alarmTableCursorElement):
    #if count < maxRowAmount: #! commenting out as this needs to be handled with a queue etc. - EQEV-67809

    alarmName = alarmTableCursor.CurrentValue
    elementValue = alarmTableCursorElement.CurrentValue
    objectOfReference = "MeContext=" + elementValue + ",Test=1" #! change the Test=1 to whatever value is required

    for alarmDefRow in alarmDefinitionsDataTable.GetRows(alarmDefinitionAlarmName, alarmDefinitionSpecificProblem, alarmDefinitionProbableCause,
                                                            alarmDefinitionEventType, alarmDefinitionSeverity):
        currentAlarmName = alarmDefinitionAlarmName.CurrentValue
        if currentAlarmName == alarmName:

            specificProblem = alarmDefinitionSpecificProblem.CurrentValue
            probableCause = alarmDefinitionProbableCause.CurrentValue
            eventType = alarmDefinitionEventType.CurrentValue
            perceivedSeverity = alarmDefinitionSeverity.CurrentValue

            urlSendAlarm = Uri("https://" + serverName + "/errevents-service/v1/errorevent/" + objectOfReference + "," + specificProblem + ","
                                + probableCause + "," + eventType)
            json = "{\"perceivedSeverity\":\"" + perceivedSeverity + "\"}"

            print(urlSendAlarm)
            print(json)

            try:
                logAlarm(alarmName, 'PM Alarm', '-', objectOfReference, '-', perceivedSeverity, str(datetime.utcnow()))
                requestTest = createRequest(urlSendAlarm, "PUT")
                putRequest(requestTest, cookies, json)
                response = requestTest.GetResponse()
                getResponse(response)
            except Exception as e:
                print(e.message)
                errorDetail = e.message + ", URL:" + str(urlSendAlarm) + ", JSON:" + str(json)
                logErrorMessage(serverName, errorDetail, alarmName, '-', objectOfReference, '-', 'PM Alarm', str(datetime.utcnow()))
        #count += 1
    #else:
        #break
