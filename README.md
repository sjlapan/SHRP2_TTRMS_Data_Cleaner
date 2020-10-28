# SHRP2 Travel Time Reliability Monitoring System (Colorado)
CDOT's implementation of the Strategic Highway Research Program 2 (SHRP2) Travel Time Reliability Monitoring System (TTRMS).

## Table of Contents
* [Overview](https://github.com/sjlapan/SHRP2_TTRMS_Data_Cleaner/blob/master/README.md#overview)
* [Technologies](https://github.com/sjlapan/SHRP2_TTRMS_Data_Cleaner/blob/master/README.md#technologies)
* [User Guide](https://github.com/sjlapan/SHRP2_TTRMS_Data_Cleaner/blob/master/README.md#user-guide)
* [Acknowledgments](https://github.com/sjlapan/SHRP2_TTRMS_Data_Cleaner/blob/master/README.md#acknowledgements)

## Overview
This application was developed by Navjoy Inc. in partnership with the Colorado Department of Transportation (CDOT).

Navjoy compiled travel time data for corridors with four sources of non-recurring congestion: active work zones, traffic incidents, special events, and severe weather. Travel time data were compiled from the RITIS Probe Data Analytics Massive Data Downloader, and impact dates, locations, and subtypes were compiled from various CDOT databases.

This application is made up of four components:

* A data cleaner
* A database query tool
* A graph generator
* A database cleaning tool

Note: The MongoDB database used for this project cannot be accessed without a secure link. However, a full export of the data has been provided in a .CSV file in this repository, along with several examples of the source files used from RITIS (see Data folder). The outputs folder also contains examples of various outputs from the TTRMS.

For more information on CDOT's implementation of SHRP2, see the report included in this repository.

A full guide for use of the TTRMS is provided below. For additional information, send inquiries to slapan@navjoyinc.com.

## Technologies
* Python 3.7.4

### Libraries
* datetime 4.3
* numpy 1.18.2
* pandas 1.1.2
* plotly 4.9.0
* pymongo 3.9.0
* PySide2 5.15.0a1.dev1582817568
* PySimpleGUI 4.16.0
* pytz 2019.3

## User Guide
### Collecting Data

The TTRMS uses travel time data compiled from the RITIS Probe Data Analytics Massive Data Downloader. It can accept data sourced from INRIX and from the United States Federal Highway Administration's (FHWA) National Performance Management Research Data Set (NPMRDS), which have slightly different metadata available for corridor segments. For more information on the segmentation used in these data sets, see the full report included within this repository.

#### Impacted Period Selection
Selection of the data should always begin with time and location data for a specific event (work zone, incident, weather, or special event). As this information is added to the TTRMS manually, any source/format can be used. However, the subtypes for each impact category have been selected to match the classification scheme used by CDOT in their Event Audit database, and may not be appropriate for all use cases.

Once users have identified the location and date/time of an event, they must find the corresponding TMC segments in the RITIS platform. It is best to select the smallest possible length of the corridor encompassing the event location to ensure that the effect on travel times is captured. Users must then select the appropriate date(s) and start/end times for the impact, as well as the time interval to be used for the averaging of travel times. For CDOT's database, we used the following convention:

* 1 hour intervals for work zones
* 15 minute intervals for weather events
* 15 minute intervals for special events
* 5 minute intervals for incidents.

One these parameters are set, users may export the data, which will include a travel time file with the average travel time for each interval requested, and a TMC metadata file. 

#### Baseline Period Selection
Users should then use the same TMC segments and time interval selection to pull data for a period of time prior to the impact event. We recommend using no less than 1 month of data for this baseline period, as the travel times will be averaged by the interval and day of the week (e.g. the average travel time at 18:00 on a Friday). At this point, the user should have four files: one travel time file and TMC file for the impacted period and for the baseline period.
### Launching the Application

The application can be launched by calling the .PY file from the command line after setting the working directory. The GUI will default to the Data Cleaner tab at launch.

### Data Cleaner

![Data Cleaner GUI](https://github.com/sjlapan/SHRP2_TTRMS_Data_Cleaner/tree/master/Images/ttrms_data_cleaner.png)

### Database Query Tool

### Graph Generator

### Database Cleaner


## Acknowledgments
All code written by Stewart LaPan. The SHRP2 final report was composed by Justin Healey and Devin Joslin. Special thanks to Ethan Alexander and Marc Russell for their data collection efforts, and to Emily Gerson and Jim MacCrea for their assistance with editing and formatting of the final report. Many thanks to CDOT, the Federal Highway Adminstration, and the Denver Regional Council of Governments for all guidance and feedback provided.
