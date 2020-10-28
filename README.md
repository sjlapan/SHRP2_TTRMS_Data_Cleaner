# SHRP2 Travel Time Reliability Monitoring System (Colorado)
CDOT's implementation of the Strategic Highway Research Program 2 (SHRP2) Travel Time Reliability Monitoring System (TTRMS).

## Table of Contents
* [Overview] (https://github.com/sjlapan/SHRP2_TTRMS_Data_Cleaner/blob/master/README.md#overview)
* [Technologies] (https://github.com/sjlapan/SHRP2_TTRMS_Data_Cleaner/blob/master/README.md#technologies)
* [User Guide] (https://github.com/sjlapan/SHRP2_TTRMS_Data_Cleaner/blob/master/README.md#user-guide)
* [Acknowledgments] (https://github.com/sjlapan/SHRP2_TTRMS_Data_Cleaner/blob/master/README.md#acknowledgements)

## Overview
This application was developed by Navjoy Inc. in partnership with the Colorado Department of Transportation (CDOT).

Navjoy compiled travel time data for corridors with four sources of non-recurring congestion: active work zones, traffic incidents, special events, and severe weather. Travel time data were compiled from the RITIS Probe Data Analytics Massive Data Downloader, and impact dates, locations, and subtypes were compiled from various CDOT databases.

This application is made up of four components:

* A data cleaner
* A database query tool
* A graph generator
* A database cleaning tool

For more information on CDOT's implementation of SHRP2, see the report included in this repository.

A full guide for use of the TTRMS is provided below.

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


### User Guide


## Acknowledgments
All code written by Stewart LaPan. The SHRP2 final report was composed by Justin Healey and Devin Joslin. Special thanks to Ethan Alexander and Marc Russell for their data collection efforts, and to Emily Gerson and Jim MacCrea for their assistance with editing and formatting of the final report. Many thanks to CDOT, the Federal Highway Adminstration, and the Denver Regional Council of Governments for all guidance and feedback provided.
