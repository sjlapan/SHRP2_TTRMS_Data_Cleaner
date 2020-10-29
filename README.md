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
* datetime 4.3.0
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

Once users have identified the location and date/time of an event, they must find the corresponding TMC segments in the RITIS platform. It is best to select the smallest possible length of the corridor encompassing the event location to ensure that the effect on travel times is captured. __**Both directions of travel must be selected**__, even if the impact event only occurred for one. Users must then select the appropriate date(s) and start/end times for the impact, as well as the time interval to be used for the averaging of travel times. For CDOT's database, we used the following convention:

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

![Data Cleaner GUI](/Images/ttrms_data_cleaner.png)

Users must first select one of two data sources: INRIX and NPMRDS. If INRIX is selected, the user must then manually select the corridor functional class (Interstate, Freeway, or Highway) and urban classification (this information is already included in the NPMRDS files).

Users must then input the two travel time files and the two TMC files into the appropriate file selection fields, then select the time interval used in their files. Once these selections have been made, the user can choose their output folder and select **Run**.

Once this step has been completing, there should be three new files in the output folder: travel time tables for the baseline and impacted periods and an impact period template (seen below).
![Schedule Template](/Images/schedule_template_fresh.png)

The impact period template must then be filled out manually by the user. Users will enter "yes" in the "impact_present" column for all intervals where the impact was "active." If the impact occurred for both directions of travel, this will need to be done twice, as the time intervals repeat for the secondary travel direction. An example of the filled out spreadsheet can be seen below.
![Completed Schedule Template](/Images/schedule_template_filled.png)

Once the timeline has been filled out, users must then select the edited file in the next file browse input. Users may then manually select the impact type, subtype, and the resulting lane closure(s) if this information is available. Users may then name their output file and select **Run**. This will add 3-4 .HTML files to the output folder: a .CSV containing the formatted data, a plot of travel times and percent change in travel time over time for each relevant direction of travel, and cumulative distribution function(s) (CDF). Examples of both can be seen below.
![Travel Time Visualization](/Images/travel_time_plot.png)

![Travel Time CDF](/Images/travel_time_cdf.png)

Users should inspect these visualizations to determine whether or not the data make sense. If baseline travel times appear to have erroneous fluctuations or if impacted period travel times are not at the appropriate scale, the user may want to attempt to add or remove some TMC segments from their analysis and try again.

If the user determines that the data are reasonable, they may then upload them to a MongoDB database by adding a secure database connection string to the input box and selecting one of two Collection options (Records or Test), then selecting **Upload**. By default, the connection string input is set to connect to the local host. For more information on setting up and connecting to a database in MongoDB, see [this guide](https://docs.mongodb.com/manual/installation/).

### Database Query Tool
![Database Query Tool](/Images/ttrms_data_query.png)

The database query tab can be used to pull data from a database using a secure connection string. If the default settings are used, clicking **Ok** will return a .CSV with the full database contents. Alternatively, users can filter their output to include specific corridor types and classes, travel directions, impact types, etc. If users would like to only compare impacts for a specific corridor, the Corridor ID list can be refreshed to show which corridors in the database are available given your other search parameters.

The .CSV that you export can then be used for the graph generator, as described below.

### Graph Generator
![Graph Generator](/Images/ttrms_chart_generator.png)

To use the graph generator, users must select any export from the database (it will only accept .CSV as a format). Users can then select up to two categorical bariables to compare in a violin plot. The first variabel determines which categories are displayed on the horizontal axis, and the second further subdivides the data using the default Plotly color palette, which will be detailed in the legend of the chart. 

Users may then select their output folder and choose to **Generate Graphs**. This will create two .HTML files which can then be viewed in any standard web browser.
![Violin Plot](/Images/violin_plot.png)
![CDF Comparison](/Images/percent_change_cdf.png)

The CDF plot will plot a line for each combination of the variables selected. Depending on which variables are selected, this can often result in a dense overlay of multiple curves. Each line can be toggled on/off by clicking on its label in the figure legend.

### Database Cleaner
MongoDB's Compass interface does not allow users to easily filter for and remove records in bulk, so this tab was added to provide this functionality. These filters construct a query just as the query tool would, but remove all records returned from the database rather than writing them to a file. Users should provide as much detail as possible to ensure that they are only removing the intended records.

## Acknowledgments
All code written by Stewart LaPan. The SHRP2 final report was composed by Justin Healey and Devin Joslin. Special thanks to Ethan Alexander and Marc Russell for their data collection efforts, and to Emily Gerson and Jim MacCrea for their assistance with editing and formatting of the final report. Many thanks to CDOT, the Federal Highway Adminstration, and the Denver Regional Council of Governments for all guidance and feedback provided.
