# Netwatcher
Monitor your network for unknown MAC addresses using data from UniFi controller and alert using Pushover

## Background:
I have tried and used "Watch Your LAN" and NetAlerX for several year and got tired of the way they works by scanning the network (arp-scan)
This small script connects to your Unifi controller API and get all client data and verify MAC addresses with a simple text file.
If I need to add another trusted MAC address, you just add another line in the text file.
So far I keept it very small and basic (on purpose).. :-)  

## Fetures:
- Extract all known MAC addresses connected to your network managed by Unifi Network Server
- Alert to Pushover if new (untrusted) MAC addresses are seen on the network
- Manually add trusted MAC addresses to trusted.txt

## Screenshot:
 Not available at the moment
 
## ToDO:
- Add simple WebUI to add trusted MAC addresses to trusted.txt
- Add more notification services Discord, Gotify, a.s.o
- ???
