# Data Dictionary

- [Introduction](#introduction)
- [Data Dictionary](#data-dictionary)
- [Data Mapping for Line ID and Station ID](#data-mapping-for-line-id-and-station-id)
- [Data Mapping for `station_char`](#data-mapping-for-station_char)

## Introduction


The purpose of this document is to describe the main fields associated with the TTC Subway API. It also translates the fields Line ID, Station ID, and `station_char` from IDs to values that will make sense to a TTC transit user.

## Data Dictionary

| Data Source |      Field Name     |                                              Description                                              |    Example Value    |                                                                                                                                                                                                                           Further Notes                                                                                                                                                                                                                           |                                  Open Questions                                 |
|:-----------:|:-------------------:|:-----------------------------------------------------------------------------------------------------:|:-------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------:|
| ntas data   | requestid           | ID referencing each request made to the API                                                           | 10                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |                                                                                 |
| ntas data   | id                  | Unique ID for each record                                                                             | 12271799686         | A record details the time remaining until a particular train arrives to a subway station platform as of the moment in time when the API was called                                                                                                                                                                                                                                                                                                                |                                                                                 |
| ntas data   | station_char        | ID for the platform where passengers wait for their train.                                            | WIL1                |                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |                                                                                 |
| ntas data   | subwayline          | Refers to the subway line the incoming train is travelling on                                         | YUS                 | There are three subway lines in the data: Yonge University (YUS), Bloor Danforth (BD), and Sheppard (SHEP)                                                                                                                                                                                                                                                                                                                                                        |                                                                                 |
| ntas data   | system_message_type | State of the API                                                                                      | Normal              | Typically returns value of normal - be worried if it does not                                                                                                                                                                                                                                                                                                                                                                                                     |                                                                                 |
| ntas data   | timint              | Time remaining until train arrives at station                                                         | 12.74324436         | It is believed that this is determined by the distance of the arriving train from the station. For example, at 500 meters away, a train would always display 1 minute away.                                                                                                                                                                                                                                                                                       |                                                                                 |
| ntas data   | traindirection      | The direction the incoming train is heading                                                           | North               | Takes on four values:  North, south, east, or west                                                                                                                                                                                                                                                                                                                                                                                                                | What does it mean when the station ID is Union and the train dirction is South? |
| ntas data   | trainid             | ID of the incoming train                                                                              | 4                   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |                                                                                 |
| ntas data   | train_message       | Provides the status of the incoming train.                                                            | Arriving            | Takes on three values: Arriving, At the Station, and Delayed                                                                                                                                                                                                                                                                                                                                                                                                      | What is the TTC definition of delayed?                                          |
| container   | requestid           | ID referencing each request made to the API                                                           | 10                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |                                                                                 |
| container   | data_               |                                                                                                       | (null)              | Always null, can ignore this field                                                                                                                                                                                                                                                                                                                                                                                                                                |                                                                                 |
| container   | stationid           | ID referencing a particular station (e.g. Union) and subway line (e.g. Yonge University yellow line). | 2                   | This is the ID entered when requesting data from the API. Most subway stations only have one station ID. However, some may have two. For example, Bloor-Yonge station has two station IDs, one for the BD green line and one for the YUS yellow line.                                                                                                                                                                                                             |                                                                                 |
| container   | lineid              | ID referencing the subway line that the incoming train is travelling on.                              | 1                   | This is the ID entered when requesting data from the API. For stations with multiple lines (eg Bloor Yonge), the API will return not only train data for the lineid requested but also for the other subway lines at the station. Thus, lineid is not a reliable field for determining which line an incoming train is traveling on. Use the subwayline field instead. There are three subway lines in the data: 1, 2, and 4 corresponding to YUS, BD, and SHEP.  |                                                                                 |
| container   | all_stations        | Whether the call to the API succeeded (ie gathered relevant data) or failed                           | Success             | Typically always success - be worried if not                                                                                                                                                                                                                                                                                                                                                                                                                      |                                                                                 |
| container   | create_date         | Timestamp created by API for the request                                                              | 2017-02-05 23:32:40 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |                                                                                 |

## Data Mapping for Line ID and Station ID 

Note that some station names have two Station IDs. For example, Bloor-Yonge has IDs 22 and 50. ID #22 corresponds to the Yonge-University line whereas ID #50 corresponds to the Bloor-Danforth line. 


| Line ID |  Line Name       | Station ID | Station Name                | 
|---------|------------------|------------|-----------------------------| 
| 1       | Yonge-University | 1          | Sheppard West               | 
| 1       | Yonge-University | 2          | Wilson                      | 
| 1       | Yonge-University | 3          | Yorkdale                    | 
| 1       | Yonge-University | 4          | Lawrence West               | 
| 1       | Yonge-University | 5          | Glencairn                   | 
| 1       | Yonge-University | 6          | Eglinton West               | 
| 1       | Yonge-University | 7          | St Clair West               | 
| 1       | Yonge-University | 8          | Dupont                      | 
| 1       | Yonge-University | 9          | Spadina                     | 
| 1       | Yonge-University | 10         | St George                   | 
| 1       | Yonge-University | 11         | Museum                      | 
| 1       | Yonge-University | 12         | Queen's Park                | 
| 1       | Yonge-University | 13         | St Patrick                  | 
| 1       | Yonge-University | 14         | Osgoode                     | 
| 1       | Yonge-University | 15         | St Andrew                   | 
| 1       | Yonge-University | 16         | Union                       | 
| 1       | Yonge-University | 17         | King                        | 
| 1       | Yonge-University | 18         | Queen                       | 
| 1       | Yonge-University | 19         | Dundas                      | 
| 1       | Yonge-University | 20         | College                     | 
| 1       | Yonge-University | 21         | Wellesley                   | 
| 1       | Yonge-University | 22         | Bloor-Yonge                 | 
| 1       | Yonge-University | 23         | Rosedale                    | 
| 1       | Yonge-University | 24         | Summerhill                  | 
| 1       | Yonge-University | 25         | St Clair                    | 
| 1       | Yonge-University | 26         | Davisville                  | 
| 1       | Yonge-University | 27         | Eglinton                    | 
| 1       | Yonge-University | 28         | Lawrence                    | 
| 1       | Yonge-University | 29         | York Mills                  | 
| 1       | Yonge-University | 30         | Sheppard-Yonge              | 
| 1       | Yonge-University | 31         | North York Centre           | 
| 1       | Yonge-University | 32         | Finch                       | 
| 2       | Bloor-Danforth   | 33         | Kipling                     | 
| 2       | Bloor-Danforth   | 34         | Islington                   | 
| 2       | Bloor-Danforth   | 35         | Royal York                  | 
| 2       | Bloor-Danforth   | 36         | Old Mill                    | 
| 2       | Bloor-Danforth   | 37         | Jane                        | 
| 2       | Bloor-Danforth   | 38         | Runnymede                   | 
| 2       | Bloor-Danforth   | 39         | High Park                   | 
| 2       | Bloor-Danforth   | 40         | Keele                       | 
| 2       | Bloor-Danforth   | 41         | Dundas West                 | 
| 2       | Bloor-Danforth   | 42         | Lansdowne                   | 
| 2       | Bloor-Danforth   | 43         | Dufferin                    | 
| 2       | Bloor-Danforth   | 44         | Ossington                   | 
| 2       | Bloor-Danforth   | 45         | Christie                    | 
| 2       | Bloor-Danforth   | 46         | Bathurst                    | 
| 2       | Bloor-Danforth   | 47         | Spadina                     | 
| 2       | Bloor-Danforth   | 48         | St George                   | 
| 2       | Bloor-Danforth   | 49         | Bay                         | 
| 2       | Bloor-Danforth   | 50         | Bloor-Yonge                 | 
| 2       | Bloor-Danforth   | 51         | Sherbourne                  | 
| 2       | Bloor-Danforth   | 52         | Castle Frank                | 
| 2       | Bloor-Danforth   | 53         | Broadview                   | 
| 2       | Bloor-Danforth   | 54         | Chester                     | 
| 2       | Bloor-Danforth   | 55         | Pape                        | 
| 2       | Bloor-Danforth   | 56         | Donlands                    | 
| 2       | Bloor-Danforth   | 57         | Greenwood                   | 
| 2       | Bloor-Danforth   | 58         | Coxwell                     | 
| 2       | Bloor-Danforth   | 59         | Woodbine                    | 
| 2       | Bloor-Danforth   | 60         | Main Street                 | 
| 2       | Bloor-Danforth   | 61         | Victoria Park               | 
| 2       | Bloor-Danforth   | 62         | Warden                      | 
| 2       | Bloor-Danforth   | 63         | Kennedy                     | 
| 4       | Sheppard         | 64         | Sheppard-Yonge              | 
| 4       | Sheppard         | 65         | Bayview                     | 
| 4       | Sheppard         | 66         | Bessarion                   | 
| 4       | Sheppard         | 67         | Leslie                      | 
| 4       | Sheppard         | 68         | Don Mills                   | 
| 3       | Scarborough      | 69         | Kennedy                     | 
| 3       | Scarborough      | 70         | Lawrence East               | 
| 3       | Scarborough      | 71         | Ellesmere                   | 
| 3       | Scarborough      | 72         | Midland                     | 
| 3       | Scarborough      | 73         | Scarborough Centre          | 
| 3       | Scarborough      | 74         | McCowan                     | 
| 1       | Yonge-University | 75         | Downsview Park              | 
| 1       | Yonge-University | 76         | Finch West                  | 
| 1       | Yonge-University | 77         | York University             | 
| 1       | Yonge-University | 78         | Pioneer Village             | 
| 1       | Yonge-University | 79         | Highway 407                 | 
| 1       | Yonge-University | 80         | Vaughan Metropolitan Centre | 

## Data Mapping for `station_char`

In the data, some station_char values are associated with 2 station IDs and line IDs. This is because when we request data from the API for a station that is part of multiple subway lines, it returns trains details for all subway lines.  

N = North, S = South, E = East, W = West and refers to the direction the train travels.

Note that this excludes station_char values for the new station IDs (75-80).

| station_char | station_char_name   | traindirection | Station ID | Line ID | 
|--------------|---------------------|----------------|------------|---------| 
| DWN1         | Sheppard West N     | North          | 1          | 1       | 
| DWN2         | Sheppard West S     | South          | 1          | 1       | 
| WIL1         | Wilson N            | North          | 2          | 1       | 
| WIL2         | Wilson S            | South          | 2          | 1       | 
| YKD1         | Yorkdale N          | North          | 3          | 1       | 
| YKD2         | Yorkdale S          | South          | 3          | 1       | 
| LWW1         | Lawrence West N     | North          | 4          | 1       | 
| LWW2         | Lawrence West S     | South          | 4          | 1       | 
| GCN1         | Glencairn N         | North          | 5          | 1       | 
| GCN2         | Glencairn S         | South          | 5          | 1       | 
| EGW1         | Eglinton West N     | North          | 6          | 1       | 
| EGW2         | Eglinton West S     | South          | 6          | 1       | 
| SCW1         | St Clair West N     | North          | 7          | 1       | 
| SCW2         | St Clair West S     | South          | 7          | 1       | 
| DUP1         | Dupont N            | North          | 8          | 1       | 
| DUP2         | Dupont S            | South          | 8          | 1       | 
| MUS1         | Museum N            | North          | 11         | 1       | 
| MUS2         | Museum S            | South          | 11         | 1       | 
| QPK1         | Queen's Park N      | North          | 12         | 1       | 
| QPK2         | Queen's Park S      | South          | 12         | 1       | 
| STP1         | St Patrick N        | North          | 13         | 1       | 
| STP2         | St Patrick S        | South          | 13         | 1       | 
| OSG1         | Osgoode N           | North          | 14         | 1       | 
| OSG2         | Osgoode S           | South          | 14         | 1       | 
| STA1         | St Andrew N         | North          | 15         | 1       | 
| STA2         | St Andrew S         | South          | 15         | 1       | 
| UNI1         | Union N             | North          | 16         | 1       | 
| UNI2         | Union S             | South          | 16         | 1       | 
| KNG1         | King N              | North          | 17         | 1       | 
| KNG2         | King S              | South          | 17         | 1       | 
| QUN1         | Queen N             | North          | 18         | 1       | 
| QUN2         | Queen S             | South          | 18         | 1       | 
| DUN1         | Dundas N            | North          | 19         | 1       | 
| DUN2         | Dundas S            | South          | 19         | 1       | 
| COL1         | College N           | North          | 20         | 1       | 
| COL2         | College S           | South          | 20         | 1       | 
| WEL1         | Wellesley N         | North          | 21         | 1       | 
| WEL2         | Wellesley S         | South          | 21         | 1       | 
| ROS1         | Rosedale N          | North          | 23         | 1       | 
| ROS2         | Rosedale S          | South          | 23         | 1       | 
| SUM1         | Summerhill N        | North          | 24         | 1       | 
| SUM2         | Summerhill S        | South          | 24         | 1       | 
| STC1         | St Clair N          | North          | 25         | 1       | 
| STC2         | St Clair S          | South          | 25         | 1       | 
| DAV1         | Davisville N        | North          | 26         | 1       | 
| DAV2         | Davisville S        | South          | 26         | 1       | 
| EGL1         | Eglinton N          | North          | 27         | 1       | 
| EGL2         | Eglinton S          | South          | 27         | 1       | 
| LAW1         | Lawrence N          | North          | 28         | 1       | 
| LAW2         | Lawrence S          | South          | 28         | 1       | 
| YKM1         | York Mills N        | North          | 29         | 1       | 
| YKM2         | York Mills S        | South          | 29         | 1       | 
| NYC1         | North York Centre N | North          | 31         | 1       | 
| NYC2         | North York Centre S | South          | 31         | 1       | 
| FIN1         | Finch N             | North          | 32         | 1       | 
| FIN2         | Finch S             | South          | 32         | 1       | 
| KIP1         | Kipling E           | East           | 33         | 2       | 
| KIP2         | Kipling W           | West           | 33         | 2       | 
| ISL1         | Islington E         | East           | 34         | 2       | 
| ISL2         | Islington W         | West           | 34         | 2       | 
| RYK1         | Royal York E        | East           | 35         | 2       | 
| RYK2         | Royal York W        | West           | 35         | 2       | 
| OML1         | Old Mill E          | East           | 36         | 2       | 
| OML2         | Old Mill W          | West           | 36         | 2       | 
| JNE1         | Jane E              | East           | 37         | 2       | 
| JNE2         | Jane W              | West           | 37         | 2       | 
| RUN1         | Runnymede E         | East           | 38         | 2       | 
| RUN2         | Runnymede W         | West           | 38         | 2       | 
| HPK1         | High Park E         | East           | 39         | 2       | 
| HPK2         | High Park W         | West           | 39         | 2       | 
| KEL1         | Keele E             | East           | 40         | 2       | 
| KEL2         | Keele W             | West           | 40         | 2       | 
| DNW1         | Dundas West E       | East           | 41         | 2       | 
| DNW2         | Dundas West W       | West           | 41         | 2       | 
| LAN1         | Lansdowne E         | East           | 42         | 2       | 
| LAN2         | Lansdowne W         | West           | 42         | 2       | 
| DUF1         | Dufferin E          | East           | 43         | 2       | 
| DUF2         | Dufferin W          | West           | 43         | 2       | 
| OSS1         | Ossington E         | East           | 44         | 2       | 
| OSS2         | Ossington W         | West           | 44         | 2       | 
| CHR1         | Christie E          | East           | 45         | 2       | 
| CHR2         | Christie W          | West           | 45         | 2       | 
| BAT1         | Bathurst E          | East           | 46         | 2       | 
| BAT2         | Bathurst W          | West           | 46         | 2       | 
| BAU1         | Bay E               | East           | 49         | 2       | 
| BAU2         | Bay W               | West           | 49         | 2       | 
| SHE1         | Sherbourne E        | East           | 51         | 2       | 
| SHE2         | Sherbourne W        | West           | 51         | 2       | 
| CFK1         | Castle Frank E      | East           | 52         | 2       | 
| CFK2         | Castle Frank W      | West           | 52         | 2       | 
| BRD1         | Broadview E         | East           | 53         | 2       | 
| BRD2         | Broadview W         | West           | 53         | 2       | 
| CHE1         | Chester E           | East           | 54         | 2       | 
| CHE2         | Chester W           | West           | 54         | 2       | 
| PAP1         | Pape E              | East           | 55         | 2       | 
| PAP2         | Pape W              | West           | 55         | 2       | 
| DON1         | Donlands E          | East           | 56         | 2       | 
| DON2         | Donlands W          | West           | 56         | 2       | 
| GWD1         | Greenwood E         | East           | 57         | 2       | 
| GWD2         | Greenwood W         | West           | 57         | 2       | 
| COX1         | Coxwell E           | East           | 58         | 2       | 
| COX2         | Coxwell W           | West           | 58         | 2       | 
| WDB1         | Woodbine E          | East           | 59         | 2       | 
| WDB2         | Woodbine W          | West           | 59         | 2       | 
| MST1         | Main Street E       | East           | 60         | 2       | 
| MST2         | Main Street W       | West           | 60         | 2       | 
| VPK1         | Victoria Park E     | East           | 61         | 2       | 
| VPK2         | Victoria Park W     | West           | 61         | 2       | 
| WAR1         | Warden E            | East           | 62         | 2       | 
| WAR2         | Warden W            | West           | 62         | 2       | 
| KEN1         | Kennedy E           | East           | 63         | 2       | 
| KEN2         | Kennedy W           | West           | 63         | 2       | 
| BYV1         | Bayview E           | East           | 65         | 4       | 
| BYV2         | Bayview W           | West           | 65         | 4       | 
| BSS1         | Bessarion E         | East           | 66         | 4       | 
| BSS2         | Bessarion W         | West           | 66         | 4       | 
| LES1         | Leslie E            | East           | 67         | 4       | 
| LES2         | Leslie W            | West           | 67         | 4       | 
| DML1         | Don Mills E         | East           | 68         | 4       | 
| DML2         | Don Mills W         | West           | 68         | 4       | 
| BSP1         | Spadina E           | East           | 9 and 47   | 1 and 2 |  
| BSP2         | Spadina W           | West           | 9 and 47   | 1 and 2 | 
| SPA1         | Spadina N           | North          | 9 and 47   | 1 and 2 | 
| SPA2         | Spadina S           | South          | 9 and 47   | 1 and 2 | 
| SGL1         | St George E         | East           | 10 and 48  | 1 and 2 | 
| SGL2         | St George W         | West           | 10 and 48  | 1 and 2 | 
| SGU1         | St George N         | North          | 10 and 48  | 1 and 2 | 
| SGU2         | St George S         | South          | 10 and 48  | 1 and 2 | 
| BLO1         | Bloor-Yonge N       | North          | 22 and 50  | 1 and 2 | 
| BLO2         | Bloor-Yonge S       | South          | 22 and 50  | 1 and 2 | 
| YNG1         | Bloor-Yonge E       | East           | 22 and 50  | 1 and 2 | 
| YNG2         | Bloor-Yonge W       | West           | 22 and 50  | 1 and 2 | 
| SHP1         | Sheppard-Yonge N    | North          | 30 and 64  | 1 and 4 | 
| SHP2         | Sheppard-Yonge S    | South          | 30 and 64  | 1 and 4 | 
| YIE1         | Sheppard-Yonge E    | East           | 30 and 64  | 1 and 4 | 
| YIE2         | Sheppard-Yonge W    | West           | 30 and 64  | 1 and 4 | 
