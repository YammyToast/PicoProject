



# Binding Preview Tables

## Time: ./mods/time/bindings.h

|Name|Parameters|Return Type|Raw Function|
| :---: | :---: | :---: | :---: |
|HOUR_TRIGGER|<table><tr><th>Name</th><th>Type</th><th>Description</th></tr><tr><td>_MILITIME</td><td>int</td><td>Current hour in 'Military Time' (24 hour) format. Eg: 01 is 1am, 22 is 10pm.</td></tr></table>|void|void HOUR_TRIGGER(int _MILITIME);|

## Schedule: ./mods/schedule/bindings.h

|Name|Parameters|Return Type|Raw Function|
| :---: | :---: | :---: | :---: |
|HOUR_WARNING|<table><tr><th>Name</th><th>Type</th><th>Description</th></tr><tr><td>event_name</td><td>char*</td><td>Display name for the event indicated by the alert.</td></tr><tr><td>event_type</td><td>char*</td><td>Value to display for the type of event indicated by the alert.</td></tr></table>|void|void HOUR_WARNING(char* event_name, char* event_type);|


*Generated using mdutils*