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
# Name    : Reset.py
# Date    : 02/09/2019
# Revision: 1.0
# Purpose : 
#
# Usage   : PM Alarms
#

from Spotfire.Dxp.Application.Filters import *
from Spotfire.Dxp.Application import PanelTypeIdentifiers

makevisible = ['SYSTEMAREA']
for p in Document.Pages:
    if(p.Title == "Alarm Definitions"):
        for panel in p.Panels:
            if panel.TypeId == PanelTypeIdentifiers.FilterPanel:
                for group in panel.TableGroups:
                    if group.Name =="KPI Tables":
                        for fh in group.FilterHandles:
                            if fh.FilterReference.Name not in makevisible:
                                    fh.Visible = False
                                    fh.FilterReference.Reset()
                                else:
                                    fh.Visible=True
                                    fh.FilterReference.Reset()
                    else:
                        group.Visible = False