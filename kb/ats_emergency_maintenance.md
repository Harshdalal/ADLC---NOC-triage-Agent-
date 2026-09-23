# Automatic Transfer Switch (ATS) Emergency Maintenance Guide

Source: KB-SRC-010 · Owner: Power Team

## Automatic Transfer Switch (ATS) Emergency Bypass & Reset
ATS troubleshooting during a grid outage failure: 1) Measure incoming phase
voltages L1, L2, L3 on the utility and emergency generator terminals. 2) If the
utility is normal but the ATS fails to switch, inspect the motor-driven transfer
mechanism for a mechanical jam. 3) To execute a manual bypass: switch the ATS
control selector to MANUAL, insert the manual transfer handle, and crank to the
NORMAL or EMERGENCY position until the positive interlock clicks. 4) If the
control processor PCB is frozen: cycle the 24V DC auxiliary power supply to
reboot the microcontroller logic. 5) Flash the latest firmware with enhanced
transient spike immunity before re-enabling auto mode.
