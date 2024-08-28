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
# Name    : CreateAlarmDefinitionsDBTable.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from Spotfire.Dxp.Data.Import import DatabaseDataSource, DatabaseDataSourceSettings


sql = '''
USE [alarm_db]
GO

DROP TABLE [dbo].[Alarm Definitions]
GO

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[AlarmDefinitions](
    [AlarmName] [nchar](50) NULL,
    [AlarmType] [nchar](50) NULL,
    [MeasureName] [nchar](50) NULL,
    [Condition] [nchar](50) NULL,
    [Threshold Value] real NULL,
    [Alarm Level] [nchar](50) NULL,
    [NE List] [nchar](500) NULL,
    [Alarm State] [nchar](50) NULL
) ON [PRIMARY]

GO
'''

dataSourceSettings = DatabaseDataSourceSettings("System.Data.SqlClient",
                                                "Server=ieatrcxb6794.athtem.eei.ericsson.se;Database=alarm_db;UID=netanserver;PWD=Ericsson01", sql)
tableName = 'temp'
databaseDataSource = DatabaseDataSource(dataSourceSettings)
newDataTable = Document.Data.Tables.Add(tableName, databaseDataSource)
Document.Data.Tables.Remove(tableName)
