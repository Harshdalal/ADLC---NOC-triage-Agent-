# BBU Power Failure Troubleshooting Guide

Source: KB-SRC-001 · Owner: RAN NOC Team

## DC Power Failure Initial Response
When a BBU DC Power Off alarm is raised (Alarm ID 2151), immediately verify the DC
input voltage reading. If voltage drops below 43V, the BBU will execute a controlled
shutdown. Steps: 1) Check AC mains supply at the main distribution board. 2) Verify
rectifier module status on the EMS. 3) If all rectifiers are offline, dispatch a
field engineer with a mobile genset immediately. 4) Estimate battery backup time
based on load (typically 4-8 hours depending on battery age and site load). 5)
Create a P1 incident if the site has the SA-flag set or is a Golden Hub profile.

## Battery Backup Estimation Guide
To estimate remaining battery backup time during a power outage: 1) Check the
current battery string voltage (fully charged = 54V DC for a 48V system). 2)
Measure current draw from BBU+RRU+fan load (typical macro site = 15-25A). 3)
Estimated time = (battery Ah capacity x 0.8 derating factor) / current draw.
Example: 200Ah x 0.8 / 20A = 8 hours. Important: battery efficiency degrades with
age. Sites with batteries over 5 years old: apply a 0.6 derating factor. Dispatch
the genset if estimated backup time is under 4 hours. Coordinate with field ops:
genset deployment takes approximately 45-90 minutes from depot.

## Rectifier Module Replacement Procedure
Rectifier module hot-swap procedure: 1) Confirm spare module compatibility with the
site BOM. 2) On the EMS, note DC bus load distribution. 3) Unlock the rectifier
shelf front panel. 4) Slide the failed module out; insert the new module. 5) Verify
the green LED on the new module within 30 seconds. 6) Monitor the DC bus voltage
stabilise to the 48-54V range. 7) Verify the alarm clears on the EMS within 5
minutes. Document the part serial number in the CMDB. Note: do NOT replace more
than one module simultaneously, to avoid a power bus interruption.
