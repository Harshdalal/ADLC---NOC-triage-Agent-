# Transmission Path Failover Procedures

Source: KB-SRC-008 · Owner: TX NOC Team

## Transmission Path Failover Activation
When the primary transmission path fails, backup path activation steps: 1)
Confirm the primary path failure on NCE-IP or EPNM (link down alarm on all hops).
2) Verify the backup path is pre-configured in the IGP (L3VPN or MPLS-TE). 3)
Check backup path health on the EMS before traffic switchover. 4) If automatic
failover did not occur within 60 seconds, initiate a manual switch on the
aggregation SPE. 5) Verify service restoration on the BBU EMS after switchover.
6) Document the switchover time and duration in the transmission log.

SLA: automatic failover must complete within 50ms for ring protection, or 90s for
linear protection.

## Dependent-site backhaul
A site whose backhaul routes through another site's aggregation hub loses its
own transmission path if that hub goes down, even though nothing failed at the
dependent site itself. Reroute the dependent site's traffic via its secondary
ring while the hub site's own outage is resolved; do not wait for the hub to
recover before rerouting.
