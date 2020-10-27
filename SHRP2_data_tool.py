
# Import dependencies

import sys,os
import PySide2

dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


import PySimpleGUI as sg
import pandas as pd
import numpy as np
import datetime
import pytz
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import re
import pymongo
import linecache


# Define Functions

def TimestampConverter(date_string):
    local = pytz.timezone("America/Denver")
    naive = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    local_dt = local.localize(naive)
    utc_dt = local_dt.astimezone(pytz.utc)
    date_string = utc_dt
    return date_string

def AsLocalTimeString(utc_dt):
    local = pytz.timezone("America/Denver")
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local)
    normalized = local.normalize(local_dt)
    return normalized.strftime("%Y-%m-%d %H:%M:%S")

# Error handling code below from https://stackoverflow.com/questions/14519177/python-exception-handling-line-number

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(
        filename, 
        lineno, 
        line.strip(), 
        exc_obj
        ))
    sg.PopupScrolled('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(
        filename, 
        lineno, 
        line.strip(), 
        exc_obj
        ))

# Dropdown Lists for the GUI

time_list = [
    "",
    0, 
    1, 
    2, 
    3, 
    4, 
    5, 
    6, 
    7, 
    8, 
    9, 
    10, 
    11, 
    12, 
    13, 
    14, 
    15, 
    16,
    17, 
    18, 
    19, 
    20, 
    21, 
    22, 
    23, 
    24
    ]
    
corridor__response_dropdown_list = [
    "",
    "No information",
    "No closure",
    "Partial closure", 
    # "Center lane closed",
    # "Left lane closed",
    # "Left lanes (2+) closed",
    # "Right lane closed",
    # "Right lanes (2+ closed)",
    # "Single lane closure - unknown",
    # "Multiple lane closures - right and left",
    # "Single lane traffic",
    "All lanes closed",
    # "Alternating single lane closure",
    # "Intermittent single lane closure",
    # "Intermittent multiple lane closure",
    # "Intermittent traffic stops",
    # "Mobile lane closure",
    # "Various lane closures",
    # "Mobile lane closure and various closures",
    # "Off-ramp closure",
    # "On-ramp closure",
    # "On-ramp and off-ramp closure",
    "On-ramp or off-ramp closure",
    ]

work_zone_subtype_dropdown_list = [
    "",
    # "Bridge construction",
    # "Bridge maintenance",
    # "Electrical/Lighting work",
    # "Guardrail repair",
    # "Guardrail replacement",
    # "IT/Fiber operations",
    "Paving operations",
    "Striping Operations",
    "Road construction",
    "Road maintenance",
    "Signal work",
    # "Traffic signal installation",
    # "Tunnel maintenance"
    ]

incident_subtype_dropdown_list = [
    "",
    "Accident - multi vehicle",
    "Accident - single vehicle",
    "Mechanical",
    "Spun out/slide off",
    # "Disabled CMV",
    # "Earlier accident",
    # "Minor accident",
    # "Overturned vehicle",
    # "Overturned CMV",
    # "Jackknifed semi trailer",
    # "Stuck vehicle",
    # "Truck stuck under bridge"
    ]

weather_subtype_dropdown_list = [
    "",
    "Winter storm",
    "Blizzard",
    "Snow",
    "Hail",
    "Ice storm",
    "Ice glaze",
    "Rain and snow mixed",
    "Thunder storms",
    "Strong winds",
    "Hurricane force winds",
    "Tornado",
    "Severe weather",
    "Heavy rain",
    "Fog"
    ]

special_event_subtype_dropdown_list = [
    "",
    "Sporting event",
    # "Race event",
    "Holiday traffic",
    "Funeral procession",
    "Festival",
    "Concert",
    "Parade",
    "Procession",
    "VIP visit"
    ]

impact_type_key_list = [
    "_wz2_",
    "_inc2_",
    "_wthr2_",
    "_se2_"
    ]

impact_type_key_dict = {
    "_wz2_": work_zone_subtype_dropdown_list,
    "_inc2_": incident_subtype_dropdown_list,
    "_wthr2_": weather_subtype_dropdown_list,
    "_se2_": special_event_subtype_dropdown_list
    }



weekday_key_dict = {
    "_mon_": "Monday",
    "_tue_": "Tuesday",
    "_wed_": "Wednesday",
    "_thur_": "Thursday",
    "_fri_": "Friday",
    "_sat_": "Saturday",
    "_sun_": "Sunday"
}

# Layout for the main page of the GUI

# sg.theme("DarkBlue3")
sg.theme("DarkGrey2")
# sg.theme("Topanga")
# sg.theme("DarkTeal2")
# sg.theme("DarkTeal3")
# sg.theme("DarkTeal6")
# sg.theme("DarkTeal7")
# sg.theme("Material1")
# sg.theme("Material2")

#####################################
########## GUI LAYOUTS ##############
#####################################

tab1_layout = [
          
    [
        sg.Frame(" 1. Select your data source/corridor class: ",
            [
                [
                    sg.Radio(
                        "NPMRDS", 
                        group_id="source", 
                        key="_npmrds_", 
                        default=True, 
                        enable_events=True, 
                        size=(15,1)
                        ), 
                    sg.Radio(
                        "INRIX", 
                        group_id="source", 
                        key="_inrix_", 
                        enable_events=True, 
                        size=(7,1)
                        )
                    ],

                [
                    sg.Text(
                        "Corridor Type:", 
                        key="_cor_type_label_", 
                        text_color="gray", 
                        size=(15,1)
                        ), 
                    sg.Listbox(
                        values=("Interstate", "Freeway", "Highway"), 
                        key="_corridor_type_", 
                        size=(10,3)
                        )
                    ],

                [
                    sg.Radio(
                        "Urban", 
                        group_id="_urban_rural_", 
                        key="_urban_", 
                        default=True, 
                        size=(15,1)
                        ), 
                    sg.Radio("Rural", group_id="_urban_rural_", key="_rural_")
                    ]
                ]
            ),

        sg.Frame(" 2. Load your TMC and travel time files: ",
            [
                [
                    sg.Text(
                        'Baseline Period TMC File:', 
                        key='_TEXT1_', 
                        size=(47,1)
                        ), 
                    sg.Text(
                        'Baseline Period Travel Time File:', 
                        key='_TEXT2_'
                        )
                    ],
                [
                    sg.Input(
                        key='_INPUT_btmc_', 
                        justification="left"
                        ),
                    sg.FileBrowse(), 
                    sg.Input(key='_INPUT_btt_'), 
                    sg.FileBrowse()
                    ],
                [
                    sg.Text(
                        'Impact Period TMC File:', 
                        key='_TEXT3_', 
                        size=(47,1)
                        ),
                    sg.Text(
                        'Impact Period Travel Time File:', 
                        key='_TEXT4_'
                        )
                    ],
                [
                    sg.Input(key='_INPUT_itmc_'), 
                    sg.FileBrowse(),
                    sg.Input(key='_INPUT_itt_'), 
                    sg.FileBrowse()
                    ],   
                ]
            )
        ],

    [sg.Frame(" 3. Identify the time interval used: ",
        [
            [
                sg.Radio(
                    "5min", 
                    group_id="interval", 
                    key="_5min_", 
                    default=True, 
                    size=(3,1)
                    ),
                sg.Radio(
                    "10min", 
                    group_id="interval", 
                    key="_10min_", 
                    size=(4,1)
                    ),
                sg.Radio(
                    "15min", 
                    group_id="interval", 
                    key="_15min_", 
                    size=(4,1)
                    ),
                sg.Radio(
                    "1h", 
                    group_id="interval", 
                    key="_1h_", 
                    size=(2,1)
                    )
                ]
            ]
        ),
        
        sg.Frame(" 4. Select your destination folder for all file outputs: ",
            [
                [ 
                    sg.Input(key='_target_folder_'), 
                    sg.FolderBrowse()
                    ]
                ]
            )
        ],
    
    [
        sg.Button(
            "Run",
            key='_OK_BUTTON_1_', 
            size=(5,1)
            ), 
        sg.ProgressBar(
            100, 
            orientation="h", 
            size=(20, 20), 
            key="_prog1_"
            )
        ],
    [
        sg.Text(
            '', 
            key='_completion_text_1_', 
            size=(150, 1)
            )
        ],


    [
        sg.Text(" 5. Select the completed impact file that you created: ")
        ],
    [
        sg.Input(
            key='_imp_schedule_', 
            justification="left"
            ), 
        sg.FileBrowse()
        ],

    
    [sg.Frame(" 6. Select the impact type: ", 
        [ 
            [
                sg.Radio(
                    "Work Zone", 
                    group_id="impact", 
                    key="_wz_", 
                    default=True, 
                    enable_events=True, 
                    size=(8,1)
                    ),
                sg.Radio(
                    "Incident", 
                    group_id="impact", 
                    key="_inc_", 
                    enable_events=True, 
                    size=(6,1)
                    ),
                sg.Radio(
                    "Weather", 
                    group_id="impact", 
                    key="_wthr_", 
                    enable_events=True, 
                    size=(6,1)
                    ),
                sg.Radio(
                    "Special Event", 
                    group_id="impact", 
                    key="_se_", 
                    enable_events=True, 
                    size=(10,1)
                    )
                ]
            ]
        )
        ],
    [
        sg.Text(" 7. Select the impact subtype:"), 
        sg.Combo(
            work_zone_subtype_dropdown_list, 
            key="_subtype_combo_", 
            size=(30,1)
            )
        ],
    [
        sg.Text(" 8. Select the lane closure(s): "), 
        sg.Combo(
            corridor__response_dropdown_list, 
            key="_corresponse_combo_", 
            size=(30,1)
            )
        ],
    [
        sg.Text(
            " 9. Name your output: ", 
            size=(22,1)
            ), 
        sg.Input(
            key='_final_name_', 
            default_text="data_output", 
            size=(20, 1)
            )
        ],
    [
        sg.Button(
            "Run",
            key='_OK_BUTTON_2_', 
            size=(5,1)
            ), 
        sg.ProgressBar(
            100, 
            orientation="h", 
            size=(20, 20), 
            key="_prog2_"
            )
        ], 
    [
        sg.Text(
            '', 
            key='_completion_text_2_', 
            size=(100, 1)
            )
        ],
    [
        sg.Frame(" 10. Upload your data to the database: ",
            [
                [

                    sg.Text(
                        "Enter your database connection:", 
                        size=(31, 1)
                        ), 
                    sg.Text("Select your database collection:")
                    ],
                [
                    sg.Input(
                        key='_mongo_conn_', 
                        default_text="mongodb://localhost:27017", 
                        password_char='*', 
                        size=(35,1)
                        ), 
                    sg.Radio(
                        "Records", 
                        group_id= 
                        "collection", 
                        key="_records_", 
                        default= True, 
                        size=(10,1)
                        ), 
                    sg.Radio(
                        "Test", 
                        group_id= "collection", 
                        key="_test_"
                        )
                    ],
                [
                    sg.Button(
                        button_text="Upload", 
                        key="_upload_button_", 
                        size=(10,1)
                        ), 
                    sg.Text(
                        '', 
                        key="_mongo_conn_msg_", 
                        size=(100,1)
                        )
                    ]
                ]
            )
        ]
    ]           

########################################################################
###################### QUERY TOOL LAYOUT ###############################
########################################################################

tab2_layout = [
    
    [sg.Text("Enter your database connection:")],
    [
        sg.Input(
            key='_mongo_conn2_', 
            default_text="Insert unique database access token here", 
            password_char='*'
            )
        ],

    [sg.Text("Select parameters for data retrieval from the database.")],


    [
        sg.Frame("Corridor Type(s)",
            [
                [
                    sg.Checkbox("Interstate", key="_interstate_"),
                    sg.Checkbox("Freeway", key="_freeway_"),
                    sg.Checkbox("Highway", key="_highway_")       
                    ]
                ]
            ),
        sg.Frame("Urban and/or Rural",
            [
                [
            
                    sg.Checkbox("Urban", key="_urban2_"),
                    sg.Checkbox("Rural", key="_rural2_")
                    ]
                ]
            ),


        sg.Frame("Travel Direction",
            [
                [
                    sg.Checkbox("Primary (N/E)", key="_primarydir_"),
                    sg.Checkbox("Secondary (S/W)", key="_secondarydir_")
                    ]
                ]
            ),
    
        sg.Frame("Corridor ID",
            [
                [
                    sg.Combo(["All"],
                    key="_corridorselector_", default_value="All", size=(15,1)),
                    sg.Button("Refresh List", key="_refresh_", size=(16,1))  
                    ]
                ], 
            size=(50,3)
            )
        ], 

    [
        sg.Frame("Impact Type(s)",
            [
                [        
                    sg.Checkbox("Work Zone", key="_wz2_", enable_events=True),
                    sg.Checkbox("Incident", key="_inc2_", enable_events=True),
                    sg.Checkbox("Weather", key="_wthr2_", enable_events=True),
                    sg.Checkbox("Special Event", key="_se2_", enable_events=True),
                    sg.Checkbox("None", key="_none2_", enable_events=True)
                    ]
                ]
            ),
    # I need to replace these with checklists


        sg.Frame("Impact Subtype",
            [
                [
                    sg.Combo(
                        "", 
                        key="_sub_query_", 
                        size=(30,1)
                        ) 
                    ]
                ]
            )
        ],

    [
        sg.Frame("Corridor Response",
            [
                [
                    sg.Combo(corridor__response_dropdown_list, key="_corresp_query_") 
                    ]
                ]
            )
        ],

    [
        sg.Frame("Date Range(s)",
            [
                [
                
                    sg.Input(
                        key="_start_date_inp_", 
                        size=(17,1), 
                        justification="left"
                        ), 
                    sg.CalendarButton(
                        button_text="Start Date", 
                        target="_start_date_inp_", 
                        size=(10,1)
                        ), 
                    sg.Input(
                        key="_end_date_inp_", 
                        size=(17,1)
                        ), 
                    sg.CalendarButton(
                        button_text="End Date", 
                        target="_end_date_inp_", 
                        size=(10,1)
                        )
                    ]
                ]
            ),

        sg.Frame("Days of the Week", 
            [
                [
                    sg.Checkbox(
                        "Mon", 
                        key="_mon_", 
                        enable_events=True, 
                        default=True
                        ),
                    sg.Checkbox(
                        "Tue", 
                        key="_tue_", 
                        enable_events=True, 
                        default=True
                        ),
                    sg.Checkbox(
                        "Wed", 
                        key="_wed_", 
                        enable_events=True, 
                        default=True
                        ),
                    sg.Checkbox(
                        "Thur", 
                        key="_thur_", 
                        enable_events=True, 
                        default=True
                        ),
                    sg.Checkbox(
                        "Fri", 
                        key="_fri_", 
                        enable_events=True, 
                        default=True
                        ),
                    sg.Checkbox(
                        "Sat", 
                        key="_sat_", 
                        enable_events=True, 
                        default=True
                        ),
                    sg.Checkbox(
                        "Sun", 
                        key="_sun_", 
                        enable_events=True, 
                        default=True
                        )
                    ]
                ]
            )
        ],

    [sg.Text("Select the destination for your exported dataset: ")],
    [
        sg.Input(
            key='_query_dest_', 
            justification="left"
            ),
        sg.FolderBrowse(size=(10,1))
        ],
    [sg.Text("Enter the name you would like to give the new data set: ")],
    [
        sg.Input(
            key='_output_name_', 
            default_text="new_query"
            )
        ],
    [sg.Text("Export from the database: ")],
    [
        sg.OK(
            key='_OK_BUTTON_4_', 
            size=(5,1)
            ),
        sg.ProgressBar(
            100, 
            orientation="h", 
            size=(20, 20), 
            key="_prog3_"
            )
        ],
    [
        sg.Text(
            "", 
            key="_query_result_msg_", 
            size=(100, 1)
            )
        ],
    ]      

tab3_layout = [
    [sg.Text("Select the data file you would like to analyze:")],
    [
        sg.Input(
            key='_graph_input_file_', 
            justification="left"
            ), 
        sg.FileBrowse()
        ],
    [sg.Text("Select parameters for analysis.")],
    
    [
        sg.Frame("Horizontal Axis",
            [
                [
                    sg.Radio(
                        "Corridor Type", 
                        group_id="x_axis", 
                        key="_graph_x_corr_type_", 
                        default=True, 
                        enable_events=True, 
                        size=(10,1)
                        ),
                    sg.Radio(
                        "Corridor Subtype", 
                        group_id="x_axis", 
                        key="_graph_x_corr_subtype_", 
                        enable_events=True, 
                        size=(14,1)
                        ),
                    sg.Radio(
                        "Impact Type", 
                        group_id="x_axis", 
                        key="_graph_x_imp_type_", 
                        enable_events=True, 
                        size=(10,1)
                        ),
                    sg.Radio(
                        "Impact Subtype", 
                        group_id="x_axis", 
                        key="_graph_x_imp_subtype_", 
                        enable_events=True, size=(14,1)
                        ),
                    sg.Radio(
                        "Lane Closure(s)", 
                        group_id="x_axis", 
                        key="_graph_x_corr_resp_", 
                        enable_events=True, size=(17,1)
                        ),
                    sg.Radio(
                        "Time of Day", 
                        group_id="x_axis", 
                        key="_graph_x_time_day_", 
                        enable_events=True, 
                        size=(17,1)
                        )
                    ]
                ]
            )
        ],

    [
        sg.Frame(" Time Period 1: ", 
            [
                [
                    sg.Text("Start Hour:"), 
                    sg.Combo(
                        time_list, 
                        key="_period_1_start_", 
                        default_value="", 
                        size=(3,1), 
                        enable_events=True
                        ), 
                    sg.Text("End Hour:"), 
                    sg.Combo(
                        time_list, 
                        key="_period_1_end_", 
                        default_value="", 
                        size=(3,1), 
                        enable_events=True
                        )
                    ]
                ]
            ),
        
        sg.Frame(" Time Period 2: ", 
            [
                [
                    sg.Text("Start Hour:"), 
                    sg.Combo(
                        time_list, 
                        key="_period_2_start_", 
                        default_value="", 
                        size=(3,1), 
                        enable_events=True
                        ), 
                    sg.Text("End Hour:"), 
                    sg.Combo(
                        time_list, 
                        key="_period_2_end_", 
                        default_value="", 
                        size=(3,1), 
                        enable_events=True
                        )
                    ]
                ]
            ),
        ],

    [
        sg.Frame("Color",
            [
                [
                    sg.Radio(
                        "None", 
                        group_id="color", 
                        key="_graph_col_none_", 
                        default=True, 
                        enable_events=True, 
                        size=(10,1)
                        ),
                    sg.Radio(
                        "Urban Class", 
                        group_id="color", 
                        key="_graph_col_urban_class_", 
                        enable_events=True, 
                        size=(14,1)
                        ),
                    sg.Radio(
                        "Impact Type", 
                        group_id="color", 
                        key="_graph_col_imp_type_", 
                        enable_events=True, 
                        size=(10,1)
                        ),
                    sg.Radio(
                        "Impact Subtype", 
                        group_id="color", 
                        key="_graph_col_imp_subtype_", 
                        enable_events=True, 
                        size=(14,1)
                        ),
                    sg.Radio(
                        "Lane Closure(s)", 
                        group_id="color", 
                        key="_graph_col_corr_resp_", 
                        enable_events=True, 
                        size=(17,1)
                        )
                    ]
                ]
            )
        ],
    [sg.Text("Select your destination folder for all file outputs:")], 
    [
        sg.Input(key='_target_folder_graph_'), 
        sg.FolderBrowse()
        ],
    [
        sg.Text(
            "Enter the name you would like to give to the ECDF graph:", 
            size=(43,1)
            ), 
        sg.Input(
            key='_final_ECDF_name_', 
            default_text="cdf_comparison_graph", 
            size=(20, 1)
            )
        ],
    [
        sg.Text(
            "Enter the name you would like to give to the violin plot graph:", 
            size=(43,1)
            ), 
        sg.Input(
            key='_final_boxplot_name_', 
            default_text="violin_plot_graph", 
            size=(20, 1)
            )
        ],
    [
        sg.Button(
            "Generate Graphs", 
            key="_graph_gen_", 
            size=(15,1)
            )
        ]
    ]

tab5_layout = [
    [sg.Text(
        "Use this interface to select entries that you would like to"\
        " remove from the database. Be as specific as possible to avoid deleting too many entries."
        )
        ],
    [
        sg.Text("Enter your database connection:")
        ],
    [
        sg.Input(
            key='_mongo_conn3_', 
            default_text="mongodb://localhost:27017", 
            password_char='*',
            )
        ],

    [sg.Text("Select parameters for data removal from the database.")],

    [
        sg.Frame("Corridor Type(s)",
            [
                [
                    sg.Checkbox(
                        "Interstate", 
                        key="_interstate2_"
                        ),
                    sg.Checkbox(
                        "Freeway", 
                        key="_freeway2_"
                        ),
                    sg.Checkbox(
                        "Highway", 
                        key="_highway2_"
                        )       
                    ]
                ]
            )
        ],

    [
        sg.Frame("Urban and/or Rural",
            [
                [       
                    sg.Checkbox(
                        "Urban", 
                        key="_urban3_"
                        ),
                    sg.Checkbox(
                        "Rural", 
                        key="_rural3_"
                        )
                    ]
                ]
            )
        ],

    [
        sg.Frame("Corridor ID",
            [
                [
                    sg.Combo(
                        [
                            "All"
                            ], 
                        key="_corridorselector2_", 
                        default_value="All", 
                        size=(15,1)
                        ),
                    sg.Button(
                        "Refresh List", 
                        key="_refresh2_", 
                        size=(16,1)
                        )  
                    ]
                ], 
                size=(50,3)
            )
        ], 

    [
        sg.Frame("Impact Type(s)",
            [
                [     
                    sg.Radio(
                        "None", 
                        key="_none3_", 
                        enable_events=True, 
                        default = True, 
                        group_id = "impact_removal"
                        ),
                    sg.Radio(
                        "Work Zone", 
                        key="_wz3_", 
                        enable_events=True,  
                        group_id = "impact_removal"
                        ),
                    sg.Radio(
                        "Incident", 
                        key="_inc3_", 
                        enable_events=True, 
                        group_id = "impact_removal"
                        ),
                    sg.Radio(
                        "Weather", 
                        key="_wthr3_", 
                        enable_events=True, 
                        group_id = "impact_removal"
                        ),
                    sg.Radio(
                        "Special Event", 
                        key="_se3_", 
                        enable_events=True, 
                        group_id = "impact_removal"
                        )
                    ]
                ]
            )
        ],

    [
        sg.Frame("Impact Subtype",
            [
                [
                    sg.Combo(
                        work_zone_subtype_dropdown_list, 
                        key="_sub_query2_", 
                        size=(30,1)
                        ) 
                    ]
                ]
            )
        ],

    [
        sg.Frame("Corridor Response",
            [
                [
                    sg.Combo(
                        corridor__response_dropdown_list, 
                        key="_corresp_query2_"
                        ) 
                    ]
                ]
            )
        ],

    [
        sg.Frame("Travel Direction",
            [
                [          
                    sg.Checkbox(
                        "Primary (N/E)", 
                        key="_primarydir2_"
                        ),
                    sg.Checkbox(
                        "Secondary (S/W)", 
                        key="_secondarydir2_"
                        )
                    ]
                ]
            )
        ],

    [
        sg.Frame("Date Range(s)",
            [
                [         
                    sg.Input(
                        key="_start_date_inp2_", 
                        size=(17,1), 
                        justification="left"
                        ), 
                    sg.CalendarButton(
                        button_text="Start Date", 
                        target="_start_date_inp2_", 
                        size=(10,1)
                        ), 
                    sg.Input(
                        key="_end_date_inp2_", 
                        size=(17,1)
                        ), 
                    sg.CalendarButton(
                        button_text="End Date", 
                        target="_end_date_inp2_", 
                        size=(10,1)
                        )
                    ]
                ]
            )
        ],
    [
        sg.Text("Uploaded Timestamp (Use local time): "), 
        sg.Input(
            key="_timestamp_input_", 
            size=(17,1), 
            justification="left"
            ), 
        sg.CalendarButton(
            button_text="Time Stamp", 
            target="_timestamp_input_", 
            size=(10,1)
            )
        ],
    [sg.Text("Export from the database: ")],
    [
        sg.Button(
            "Delete Entries",
            key='_delete_button_', 
            size=(11,1)
            )
        ],
    [
        sg.Text(
            "", 
            key="_delete_result_msg_", 
            size=(100, 1)
            )
        ],
    ]

layout=[
    [
        sg.TabGroup(
            [
                [
                    sg.Tab(
                        "Data Cleaner", 
                        tab1_layout
                        ), 
                    sg.Tab(
                        "Database Queries", 
                        tab2_layout
                        ), 
                    sg.Tab(
                        "Graph Generator", 
                        tab3_layout
                        ), 
                    sg.Tab(
                        "Database Cleaner", 
                        tab5_layout
                        )
                    ]
                ]
            )
        ]
    ]

window = sg.Window('SHRP2 TTRMS',
                   resizable=True)

# List of elements to enable or disable

time_key_list = [
    "_period_1_start_", 
    "_period_1_end_", 
    "_period_2_start_", 
    "_period_2_end_"
    ]

key_list = [
    "_corridor_type_", 
    "_urban_", 
    "_rural_"
    ]

corridor_type_list = [
    "_graph_col_none_", 
    "_graph_col_urban_class_",
    "_graph_col_imp_type_", 
    "_graph_col_imp_subtype_",
    "_graph_col_corr_resp_"
    ]

corridor_subtype_list = ["_graph_col_urban_class_"]

impact_type_col_list = ["_graph_col_imp_type_"]

impact_subtype_list = [
    "_graph_col_urban_class_", 
    "_graph_col_imp_type_", 
    "_graph_col_imp_subtype_"
    ]

corr_response_list = [
    "_graph_col_urban_class_", 
    "_graph_col_imp_type_", 
    "_graph_col_imp_subtype_", 
    "_graph_col_corr_resp_"
    ]

window.Layout(layout).Finalize()

for key in time_key_list:
    window[key].update(disabled=True)
for key in key_list:
    window[key].update(disabled=True)
for key in corridor_type_list:
    window[key].update(disabled=False)
for key in corridor_subtype_list:
    window[key].update(disabled=False)
for key in impact_type_col_list:
    window[key].update(disabled=False)
for key in impact_subtype_list:
    window[key].update(disabled=False)
for key in corr_response_list:
    window[key].update(disabled=False)

########################################################################
########################################################################
########################### EVENT LOOPS ################################
########################################################################
########################################################################

# Event Loop
while True:
    event, values = window.Read()
    
    if event == "_cancel_1_" or event is None:
        break
    
    # Enable or disable fields depending on which data source is selected by 
    # the user.
    
    elif event == "_inrix_":
        if values["_inrix_"] == True:
            window["_cor_type_label_"].update(text_color="white")
            # window["_urban_"].update(text_color="white")
            # window["_rural_"].update(text_color="white")
            # window["_corridor_type_"].Update(visible=True)
            for key in key_list:
                window.Element(key).Update(disabled=False)
                # window.Element(key).Enable()
        else:
            window["_cor_type_label_"].update(text_color="gray")
            # window["_urban_"].update(text_color="gray")
            # window["_rural_"].update(text_color="gray")
            # window["_corridor_type_"].Update(visible=False)
            for key in key_list:
                window.Element(key).Update(disabled=True)
                # window.Element(key).Disable()
    elif event == "_npmrds_":
        if values["_npmrds_"] == True:    
            window["_cor_type_label_"].update(text_color="gray")
            for key in key_list:
                window[key].update(disabled=True)
        else:
                window["_cor_type_label_"].update(text_color="white")
                for key in key_list:
                    window.Element(key).Update(disabled=True)

    # Subtype Conditions for main tab

    elif event == "_wz_":
        if values["_wz_"] == True:
            window.FindElement("_subtype_combo_").Update(
                values=work_zone_subtype_dropdown_list
                )
    elif event == "_inc_":
        if values["_inc_"] == True:
            window.FindElement("_subtype_combo_").Update(
                values=incident_subtype_dropdown_list
                )
    elif event == "_wthr_":
        if values["_wthr_"] == True:
            window.FindElement("_subtype_combo_").Update(
                values=weather_subtype_dropdown_list
                )
    elif event == "_se_":
        if values["_se_"] == True:
            window.FindElement("_subtype_combo_").Update(
                values=special_event_subtype_dropdown_list
                )

    # Subtype Conditions for Cleaner Tab
    
    elif event == "_wz3_":
        if values["_wz3_"] == True:
            window.FindElement("_sub_query2_").Update(
                values=work_zone_subtype_dropdown_list
                )
    elif event == "_inc3_":
        if values["_inc3_"] == True:
            window.FindElement("_sub_query2_").Update(
                values=incident_subtype_dropdown_list
                )
    elif event == "_wthr3_":
        if values["_wthr3_"] == True:
            window.FindElement("_sub_query2_").Update(
                values=weather_subtype_dropdown_list
                )
    elif event == "_se3_":
        if values["_se3_"] == True:
            window.FindElement("_sub_query2_").Update(
                values=special_event_subtype_dropdown_list
                )
    
    # Button conditions for graphing tab to ensure that the user cannot create
    # strange combos.

    elif event == "_graph_x_corr_type_":
        if values["_graph_x_corr_type_"] == True:
            for key in corridor_type_list:
               window.Element(key).Update(disabled=False)
            for key in time_key_list:
                window.Element(key).Update(disabled=True)
    elif event == "_graph_x_corr_subtype_":
        if values["_graph_x_corr_subtype_"] == True:
            for key in corridor_type_list:
               window.Element(key).Update(disabled=False)
            for key in corridor_subtype_list:
                window.Element(key).Update(disabled=True)
            for key in time_key_list:
                window.Element(key).Update(disabled=True)
    elif event == "_graph_x_imp_type_":
        if values["_graph_x_imp_type_"] == True:
            for key in corridor_type_list:
               window.Element(key).Update(disabled=False)
            for key in impact_type_col_list:
                window.Element(key).Update(disabled=True)
            for key in time_key_list:
                window.Element(key).Update(disabled=True)
    elif event == "_graph_x_imp_subtype_":
        if values["_graph_x_imp_subtype_"] == True:
            for key in corridor_type_list:
               window.Element(key).Update(disabled=False)
            for key in impact_subtype_list:
                window.Element(key).Update(disabled=True)
            for key in time_key_list:
                window.Element(key).Update(disabled=True)
    elif event == "_graph_x_corr_resp_":
        if values["_graph_x_corr_resp_"] == True:
            for key in corridor_type_list:
               window.Element(key).Update(disabled=False)
            for key in corr_response_list:
                window.Element(key).Update(disabled=True)
            for key in time_key_list:
                window.Element(key).Update(disabled=True)
    elif event == "_graph_x_time_day_":
            for key in corridor_type_list:
               window.Element(key).Update(disabled=False)
            for key in time_key_list:
                window.Element(key).Update(disabled=False)

    ########################################################################
    ############## DATA CLEANING LOOP PT I #################################
    ########################################################################

    elif event == '_OK_BUTTON_1_':

        window["_completion_text_1_"].update("")

        try:
            # Progress bar update
            for i in range(10):
                window["_prog1_"].update_bar(i+1)

            # Read in source files from either INRIX or NPMRDS

            try:
                old_tmc = values["_INPUT_btmc_"]
                print(old_tmc)
                TMC_ID_baseline = pd.read_csv(old_tmc, encoding="utf-8")
            except Exception:
                print(
                    "There is something wrong with one of the files selected." \
                        " Please Try Again")

            try:
                new_tmc = values["_INPUT_itmc_"]
                print(new_tmc)
                TMC_ID_impact = pd.read_csv(new_tmc, encoding="utf-8")
            except Exception:
                print(
                    "There is something wrong with one of the files selected." \
                        " Please Try Again")

            try:
                old_csv = values["_INPUT_btt_"]
                print(old_csv)
                corridor_baseline = pd.read_csv(old_csv, encoding="utf-8")
            except Exception:
                print(
                    "There is something wrong with one of the files selected." \
                        " Please Try Again")        

            # Progress bar update
            for i in range(20):
                window["_prog1_"].update_bar(i+1)

            try:
                new_csv = values["_INPUT_itt_"]
                print(new_csv)
                corridor_impact = pd.read_csv(new_csv, encoding="utf-8")
            except Exception:
                print(
                    "There is something wrong with one of the files selected." \
                        " Please Try Again")

            # Tell the program what time interval you used to generate your data
            # It will read this number in later.

            if values["_5min_"] == True:
                interval_input = "5min"
            elif values["_10min_"] == True:
                interval_input = "10min"
            elif values["_15min_"] == True:
                interval_input = "15min"
            else:
                interval_input = "1h"

            # Extract just the tmc codes and length from one of the two sets
            
            TMC_ID_baseline.rename(columns = {"miles": "baseline_miles"}, inplace=True)
                
            # Prevent the duplicate index entry issue. Sometimes, INRIX spits out 
            # TMC metadata files with duplicate rows. This will drop them.
            # It seems like the date objects are part of the problem here.
            TMC_ID_baseline.drop(
                columns=["active_start_date", "active_end_date"], 
                axis=1, 
                inplace=True
                )
            TMC_ID_impact.drop(
                columns=["active_start_date", "active_end_date"], 
                axis=1, 
                inplace=True
                )

            TMC_ID_baseline.drop_duplicates(
                keep="first", 
                inplace = True
                )
            
            TMC_ID_impact.drop_duplicates(
                keep="first", 
                inplace=True
                )

            # Progress bar update
            for i in range(30):
                window["_prog1_"].update_bar(i+1)

            # Create a dataframe to compare lengths

            shared_tmc = pd.merge(
                TMC_ID_impact, 
                TMC_ID_baseline, 
                on="tmc", 
                how="outer"
                )

            # Get rid of any NaNs

            shared_tmc.miles.fillna(0, inplace=True)
            shared_tmc.baseline_miles.fillna(0, inplace=True)
            
            # Intitialize the segment length difference counter and count of different TMCs

            total_length_difference = 0
            bad_id_count = 0
            baseline_total = 0
            impact_total = 0

            length_list = [baseline_total, impact_total]

            # Check the lengths to make sure they match
            
            for index, row in shared_tmc.iterrows():
                if row["miles"] != row["baseline_miles"]:    
                    baseline_total += row["baseline_miles"]
                    impact_total += row["miles"]
                    bad_id_count = bad_id_count + 1
       
            total_length_difference = abs(impact_total - baseline_total)
            
            if total_length_difference != 0:
                if total_length_difference >= 1:
                    sg.Popup("The total difference in TMC segment lengths between the two" \
                        " time periods is {} miles across {} segments.".format(
                            total_length_difference, 
                            bad_id_count
                            )
                        )
                else:
                    length_in_feet = total_length_difference * 5280
                    sg.Popup("The total difference in TMC segment lengths between the two" \
                        " time periods is {} feet across {} segments.".format(
                            length_in_feet, 
                            bad_id_count
                            )
                        )
           
            # Rename your tmc column for the merge

            TMC_ID_baseline.rename(columns={"tmc": "tmc_code"}, inplace=True)
            TMC_ID_impact.rename(columns={"tmc": "tmc_code"}, inplace=True)
            
            # Merge travel time data to the tmc metadata
            
            baseline_merged = pd.merge(
                corridor_baseline, TMC_ID_baseline, how="right", on="tmc_code"
                )


            impact_merged = pd.merge(corridor_impact, TMC_ID_impact,
                                    how="right", on="tmc_code")
        
            # Check value counts here too, to see if length difference persists.

            impact_counts = impact_merged.tmc_code.value_counts().tolist()
            total_count = max(impact_counts)
            impact_dict = impact_merged.tmc_code.value_counts().to_dict()
            impact_list = list(impact_dict.items())
            warning_string = f"The following TMC segments are missing" \
                " data for some time intervals: "
            missing_count = 0

            for x in impact_list:
                if x[1] != max(impact_counts):
                    number = x[1]
                    warning_string += f"\n {x[0]}: {total_count - number}"\
                        f" intervals out of {total_count}"
                    missing_count += 1
            warning_string += "\n The TTRMS will attempt to fill in gaps" \
                " with the mean travel time for these segments."
                    
            if missing_count != 0:
                sg.Popup(f"{warning_string}")

            # Progress bar update
            for i in range(40):
                window["_prog1_"].update_bar(i+1)

            # Convert date time to the proper data type

            baseline_merged["date_time"] = pd.to_datetime(
                baseline_merged["measurement_tstamp"]
                )
                
            impact_merged["date_time"] = pd.to_datetime(
                impact_merged["measurement_tstamp"]
                )
            

            interval_int_dictionary = {
                "5min": 288,
                "10min": 144,
                "15min": 96,
                "1h": 24
                }
            selected_interval = interval_int_dictionary[interval_input]

            # Progress bar update
            for i in range(50):
                window["_prog1_"].update_bar(i+1)

            # Create the time range "spine" for the dataframe
            # It'll expand it to include a row for every time interval covered,
            # for each TMC segment.

            baseline_start_date = (min(baseline_merged.date_time))
            baseline_end_date = (max(baseline_merged.date_time))
            impact_start_date = (min(impact_merged.date_time))
            impact_end_date = (max(impact_merged.date_time))

            baseline_interval = pd.date_range(
                start=baseline_start_date, 
                end=baseline_end_date, 
                freq=interval_input
                )

            impact_interval = pd.date_range(
                start=impact_start_date, 
                end=impact_end_date, 
                freq=interval_input
                )

            # This creates a template dataframe that contains all TMC codes for all 
            # time intervals.
            
            tmc_template_ref_df = pd.DataFrame(
                {
                    "tmc_code": np.repeat(
                        TMC_ID_baseline["tmc_code"], 
                        len(baseline_interval)
                        ),
                    "date_time": np.tile(
                        baseline_interval, 
                        len(TMC_ID_baseline)
                        )
                    }
                )

            tmc_template_imp_df = pd.DataFrame(
                {
                    "tmc_code": np.repeat(TMC_ID_impact["tmc_code"], 
                        len(impact_interval)
                        ),
                    "date_time": np.tile(
                        impact_interval, 
                        len(TMC_ID_impact)
                        )
                    }
                )

            # Merge them so that the dataframe has the full range of time intervals 
            # for each TMC segment, even if data were missing.

            expanded_ref_df = pd.merge(
                tmc_template_ref_df, 
                baseline_merged, 
                on=[
                    "tmc_code", 
                    "date_time"
                    ], 
                how="left"
                )

            expanded_imp_df = pd.merge(
                tmc_template_imp_df, 
                impact_merged, 
                on=[
                    "tmc_code", "date_time"
                    ], 
                how="left"
                )

            # Progress bar update
            for i in range(60):
                window["_prog1_"].update_bar(i+1)
                   
            # Create conversion dictionary for weekday names
            day_names = {
                0: "Monday",
                1: "Tuesday",
                2: "Wednesday",
                3: "Thursday",
                4: "Friday",
                5: "Saturday",
                6: "Sunday"
                }

            # Create column with day of the week name
            expanded_ref_df["day_string"] = expanded_ref_df["date_time"].apply(
                lambda time: time.dayofweek
                )

            expanded_ref_df["day_string"].replace(day_names, inplace=True)

            expanded_imp_df["day_string"] = expanded_imp_df["date_time"].apply(
                lambda time: time.dayofweek
                )

            expanded_imp_df["day_string"].replace(day_names, inplace=True)

            # Get the month/day in one column
            expanded_ref_df["month_day"] = expanded_ref_df["date_time"].apply(
                lambda time: time.strftime("%m/%d")
                )

            expanded_imp_df["month_day"] = expanded_imp_df["date_time"].apply(
                lambda time: time.strftime("%m/%d")
                )

            # Get the month/year in one column
            expanded_ref_df["month_year"] = expanded_ref_df["date_time"].apply(
                lambda time: time.strftime("%m/%Y")
                )

            expanded_imp_df["month_year"] = expanded_imp_df["date_time"].apply(
                lambda time: time.strftime("%m/%Y")
                )

            # Progress bar update
            for i in range(70):
                window["_prog1_"].update_bar(i+1)

            # Get the year in one column
            expanded_ref_df["year"] = expanded_ref_df["date_time"].apply(
                lambda time: time.year
                )

            expanded_imp_df["year"] = expanded_imp_df["date_time"].apply(
                lambda time: time.year
                )

            # Get the time interval in its own column

            expanded_ref_df["interval"] = expanded_ref_df["date_time"].apply(
                lambda time: time.strftime("%H:%M")
                )

            expanded_imp_df["interval"] = expanded_imp_df["date_time"].apply(
                lambda time: time.strftime("%H:%M")
                )

            # Clean dataframe differently based on which source was selected.
            
            if values["_npmrds_"] == True:
                # Clean up dataframes by selecting only the columns needed

                expanded_ref_df = expanded_ref_df[[
                    "year", 
                    "tmc_code", 
                    "baseline_miles", 
                    "road", 
                    "direction", 
                    "f_system", 
                    "urban_code", 
                    "day_string", 
                    "interval", 
                    "travel_time_minutes",
                    "month_day",
                    "date_time", 
                    "month_year"
                    ]]

                expanded_imp_df = expanded_imp_df[[
                    "year", 
                    "tmc_code", 
                    "miles", 
                    "road", 
                    "direction", 
                    "f_system", 
                    "urban_code", 
                    "day_string", 
                    "interval", 
                    "travel_time_minutes",
                    "month_day",
                    "date_time", 
                    "month_year"
                    ]]

                # Create a new urban/rural classification field for the reference dataset
                expanded_ref_df["urban_rural"] = "Urban"
                
                expanded_ref_df.loc[
                    expanded_ref_df.urban_code == 99999, 
                    "urban_rural"
                    ] = "Rural"
                
                # Create a new urban/rural classification field for the impact dataset
                expanded_imp_df["urban_rural"] = "Urban"
                
                expanded_imp_df.loc[
                    expanded_imp_df.urban_code == 99999, 
                    "urban_rural"
                    ] = "Rural"
                
                # Dictionaries to convert the codes of new fields

                f_system_dict = {
                    1: "Interstate",
                    2: "Freeway",
                    3: "Highway",
                    4: "Minor_Arterial",
                    5: "Major_Collector",
                    6: "Minor_Collector",
                    7: "Local"
                    }

                # Apply dictionaries to reference dataset

                expanded_ref_df["f_system"] = expanded_ref_df["f_system"].map(
                    f_system_dict
                    )

                # Apply dictionaries to impact dataset

                expanded_imp_df["f_system"] = expanded_imp_df["f_system"].map(
                    f_system_dict
                    )

            else:
                # INRIX doesn't provide functional class or urban designation, so
                # here we add it by using the inputs from the GUI.
                # Fill in the corridor type column based on the user selection.

                expanded_ref_df["f_system"] = values["_corridor_type_"][0]
                expanded_imp_df["f_system"] = values["_corridor_type_"][0]

                # Fill in the urban code based on user selection

                if values["_urban_"] == True:
                    expanded_ref_df["urban_rural"] = "Urban"
                    expanded_imp_df["urban_rural"] = "Urban"
                else:
                    expanded_ref_df["urban_rural"] = "Rural"
                    expanded_imp_df["urban_rural"] = "Rural"
                    
            # Get mean hourly travel times for each segment
           
            mean_tt_ref = expanded_ref_df.groupby(
                "tmc_code").mean()

            mean_tt_imp = expanded_imp_df.groupby(
                "tmc_code").mean()
            
            # Progress bar update
            for i in range(80):
                window["_prog1_"].update_bar(i+1)

            # Reset the indices

            expanded_ref_df.set_index(
                ["tmc_code"], 
                inplace=True
                )

            expanded_imp_df.set_index(
                ["tmc_code"], 
                inplace=True
                )
            
            TMC_ID_baseline.set_index(
                ["tmc_code"], 
                inplace=True
                )

            TMC_ID_impact.set_index(
                ["tmc_code"], 
                inplace=True
                )

            # Fill gaps with mean values.

            filled_ref_df = expanded_ref_df.copy()
            
            filled_ref_df["travel_time_minutes"].fillna(
                mean_tt_ref["travel_time_minutes"], 
                inplace=True
                )

            filled_ref_df["baseline_miles"].fillna(
                mean_tt_ref["baseline_miles"], 
                inplace=True
                )

            try:
                filled_ref_df["road"].fillna(
                    TMC_ID_baseline["road"], 
                    inplace=True
                    )

                filled_ref_df["direction"].fillna(
                    TMC_ID_baseline["direction"], 
                    inplace=True
                    )

            except Exception as e: 
                sg.Popup("It appears that there are duplicate entries for one or more" \
                    " TMC segments in the INRIX source files. Please remove duplicates and" \
                    " try again.")
            
            filled_ref_df.reset_index(inplace=True)
            
            filled_imp_df = expanded_imp_df.copy()

            filled_imp_df["travel_time_minutes"].fillna(
                mean_tt_imp["travel_time_minutes"], 
                inplace=True
                )

            filled_imp_df["miles"].fillna(
                mean_tt_imp["miles"], 
                inplace=True
                )

            filled_imp_df["road"].fillna(
                TMC_ID_impact["road"], 
                inplace=True
                )

            filled_imp_df["direction"].fillna(
                TMC_ID_impact["direction"], 
                inplace=True
                )

            filled_imp_df.reset_index(inplace=True)
            
            
            # Progress bar update
            for i in range(90):
                window["_prog1_"].update_bar(i+1)

            # Rename baseline and impact data

            baseline_data = filled_ref_df.copy()

            impact_data = filled_imp_df.copy()

            ####### NPMRDS ADDITIONS #######

            # Get total travel time in either direction
            # If the data is from NPMRDS, 
            # the program will drop the urban_code column.

            if values["_npmrds_"] == True:
                baseline_total_tt = baseline_data.groupby([
                    "road", 
                    "direction", 
                    "month_year",  
                    "year", 
                    "f_system", 
                    "urban_rural", 
                    "month_day", 
                    "interval", 
                    "day_string"
                    ]).sum()

                baseline_total_tt.reset_index(inplace=True)
                baseline_total_tt.drop(columns=["urban_code"], axis=1, inplace=True)

                impact_total_tt = impact_data.groupby([
                    "road", 
                    "direction", 
                    "year", 
                    "f_system", 
                    "urban_rural", 
                    "month_day", 
                    "interval", 
                    "day_string", 
                    "date_time"
                    ]).sum()

                impact_total_tt.reset_index(inplace=True)
                impact_total_tt.drop(
                    columns=["urban_code"], 
                    axis=1, 
                    inplace=True
                    )
            else:
                baseline_total_tt = baseline_data.groupby([
                    "road", 
                    "direction", 
                    "month_year",  
                    "year", 
                    "f_system", 
                    "urban_rural", 
                    "month_day", 
                    "interval", 
                    "day_string"
                    ]).sum()

                baseline_total_tt.reset_index(inplace=True)

                impact_total_tt = impact_data.groupby([
                    "road", 
                    "direction", 
                    "year", 
                    "f_system", 
                    "urban_rural", 
                    "month_day", 
                    "interval", 
                    "day_string", 
                    "date_time"
                    ]).sum()

                impact_total_tt.reset_index(inplace=True)
            
            # Export baseline and impact period total travel time sheets.
            # For now, it allows the user to start from the midpoint if they need
            # to reprocess anything.

            baseline_total_tt.to_excel(
                f"{values['_target_folder_']}/baseline_total_travel_time.xls"
                )
            
            impact_total_tt.to_excel(
                f"{values['_target_folder_']}/impact_total_travel_time.xls"
                )

            # Generate template .xls to add construction activities to and
            # export it into the working directory.

            impact_schedule_template = impact_total_tt[[
                "road", 
                "direction", 
                "f_system", 
                "urban_rural",
                "date_time",
                "year",
                "month_day",
                "interval"
                ]]

            impact_schedule_template["impact_present"] = ""
            impact_schedule_template["impact_subtype"] = ""
            impact_schedule_template["corridor_response"] = ""
            impact_schedule_template.to_excel(
                f"{values['_target_folder_']}/impact_period_template.xls"
                )

            # Progress bar update
            for i in range(100):
                window["_prog1_"].update_bar(i+1)
            
            # Loop completion message
            window["_completion_text_1_"].update(
                "Check your folder for the file 'impact_period_template.xls'. In the" \
                " 'impact_present' column, type 'yes' for the impacted time" \
                " intervals. Save this file under a new name.")
        except Exception as e:

            # Error handling 

            window["_completion_text_1_"].update(
                "Something went wrong, please try again."
                )

            window["_prog1_"].update_bar(0)
            print(e)
            PrintException()

#######################################################################
#######################################################################
#####################  Cleaner Part II LOOP ###########################
#######################################################################

    elif event == '_OK_BUTTON_2_':
        
        # Reset message window

        window["_completion_text_2_"].update("")
        
        try:

            # Progress bar update
            for i in range(10):
                window["_prog2_"].update_bar(i+1)

            # Import the completed schedule file

            try:
                impact_input = values["_imp_schedule_"]
                print(impact_input)
                impact_schedule = pd.read_excel(f"{impact_input}", index_col=0)
            
            except Exception:
                print("There is something wrong with the file selected." \
                    " Please Try Again.")

            # Reading these in rather than feeding them forward internally allows the 
            # user to start up the program from the halfway point if completing the 
            # schedule document takes a while.
            
            # Need to wrap these in a try loop.        
            baseline_total_tt = pd.read_excel(
                f"{values['_target_folder_']}/baseline_total_travel_time.xls"
                )

            impact_total_tt = pd.read_excel(
                f"{values['_target_folder_']}/impact_total_travel_time.xls"
                )

            # Get year and corridor variables for graphing
            
            baseline_month_year = baseline_total_tt.month_year.value_counts().index.tolist()[0]
            baseline_year = baseline_total_tt.year.value_counts().index.tolist()[0]
            impact_year = impact_total_tt.year.value_counts().index.tolist()[0]
            corridor = baseline_total_tt.road.value_counts().index.tolist()[0]

            # Progress bar update
            for i in range(20):
                window["_prog2_"].update_bar(i+1)

            # Average the baseline data by day of the week and time interval

            mean_baseline_tt = baseline_total_tt.groupby([
                "road", 
                "direction", 
                "day_string", 
                "interval"
                ]).mean()

            mean_baseline_tt.reset_index(inplace=True)
        
            # Rename columns for merge
            
            mean_baseline_tt.rename(
                columns = {"travel_time_minutes": "baseline_mean_TT"}, 
                inplace=True
                )
            
            # Progress bar update
            for i in range(30):
                window["_prog2_"].update_bar(i+1)

            # Merge the dataframes

            merged_df = impact_total_tt.merge(
                mean_baseline_tt, 
                on=[
                    "road", 
                    "direction", 
                    "day_string", 
                    "interval"
                    ], 
                how="left", 
                validate="m:1"
                )
            
            merged_df.drop(
                columns=["year_x", "year_y"], 
                inplace=True
                )

            print(merged_df.head())

            # Calculate % Change

            merged_df["percent_change"] = merged_df.apply(
                lambda row: ((row["travel_time_minutes"] 
                            - row["baseline_mean_TT"])
                            / row["baseline_mean_TT"]) 
                            * 100, 
                axis=1
                )

            # Progress bar update
            for i in range(40):
                window["_prog2_"].update_bar(i+1)

            # Progress bar update
            for i in range(50):
                window["_prog2_"].update_bar(i+1)

            # Change type of date_time for merge

            merged_df.date_time = merged_df.date_time.astype("str")
         
            # Progress bar update
            for i in range(60):
                window["_prog2_"].update_bar(i+1)

            # Add a column stating the data source

            if values["_npmrds_"] == True:
                merged_df["source"] = "NPMRDS"
            else:
                merged_df["source"] = "INRIX"
                       
            print(merged_df.columns)
            # Coerce all text entries in impact schedule to be lowercase
            impact_schedule.impact_present = impact_schedule.impact_present.str.lower()
            
            # Merge dataframe with schedule.

            full_df = merged_df.merge(
                impact_schedule, 
                on= [
                    "road", 
                    "direction", 
                    "f_system", 
                    "urban_rural", 
                    "month_day", 
                    "interval"
                    ], 
                how = "left"
                )
            
            # Add a Class column

            full_df["class"] = (
                full_df["urban_rural"] 
                + " " 
                + full_df["f_system"]
                )

            # Sort Fields
            full_df = full_df[[
                "source",
                "road", 
                "direction", 
                "f_system",  
                "urban_rural",
                "class", 
                "miles",
                # "reference_period", 
                "year", 
                "month_day", 
                "interval", 
                "day_string", 
                "date_time_x", 
                "travel_time_minutes",    
                "baseline_mean_TT", 
                "percent_change", 
                "impact_present", 
                "impact_subtype", 
                "corridor_response"
                ]]
            
            full_df.rename(columns={"date_time_x": "date_time"}, inplace=True)
            
            # The next line of code fills in any blanks left in the template with "no"
            full_df["impact_present"].fillna("no", inplace=True) 
            
            # Progress bar update
            for i in range(70):
                window["_prog2_"].update_bar(i+1)

            # Create an impact type column and fill it in based on user selection.

            full_df.impact_type = ""

            # Filling in impact type, subtype, and corridor response.

            if values["_wz_"] == True:
                full_df.loc[
                    full_df.impact_present == "yes", 
                    "impact_type"
                    ] = "work zone"
                
            elif values["_inc_"] == True:
                full_df.loc[
                    full_df.impact_present == "yes", 
                    "impact_type"
                    ] = "incident"
                
            elif values["_se_"] == True:
                full_df.loc[
                    full_df.impact_present == "yes", 
                    "impact_type"
                    ] = "special event"
                
            else:
                full_df.loc[
                    full_df.impact_present == "yes", 
                    "impact_type"
                    ] = "weather"
                          
            full_df.loc[
                full_df.impact_present == "no", 
                "impact_type"
                ] = "None"
                
            if values["_subtype_combo_"] != "":
                full_df.loc[
                    full_df.impact_present == "yes", 
                    "impact_subtype"
                    ] = values["_subtype_combo_"]            
            
            full_df.loc[
                full_df.impact_present == "no", 
                "impact_subtype"
                ] = "None"
            
            if values["_corresponse_combo_"] != "":
                full_df.loc[
                    full_df.impact_present == "yes", 
                    "corridor_response"
                    ] = values["_corresponse_combo_"]
                
            full_df.loc[
                full_df.impact_present == "no", 
                "corridor_response"
                ] = "None"
                   
            full_df["reference_period"] = baseline_total_tt.month_year.value_counts().index.tolist()[0]
            
            # Grab the user input to name the file you are about to export.

            final_frame = values["_final_name_"]

            # Export your file.

            full_df.to_csv(f"{values['_target_folder_']}/{final_frame}.csv")

            ################# GRAPHS ###############################################
            ############ Generate Graphs ###########################################

            # Grab some variables

            directions = full_df.direction.value_counts().index.tolist()
            period_start = min(full_df.date_time)
            period_end = max(full_df.date_time)
            imp_type = values["_subtype_combo_"]
            corridor_response = values["_corresponse_combo_"]

            # Throw out a popup if there's something weird about the travel direction 
            # count.

            if len(directions) > 2:
                sg.Popup("You have more than two travel directions in your data set." \
                    " Please check your data and try again.")
            elif len(directions) <2:
                sg.Popup("You have fewer than two travel directions in your data set." \
                    " Please check your data and try again.")

            # Sort your travel directions
            
            if directions[0] in ["NORTHBOUND", "EASTBOUND"]:
                primary_full = full_df.loc[full_df.direction == directions[0]]
                primary_dir = directions[0].title()
                secondary_full = full_df.loc[full_df.direction == directions[1]]
                secondary_dir = directions[1].title()
            else:
                primary_full = full_df.loc[full_df.direction == directions[1]]
                primary_dir = directions[1].title()
                secondary_full = full_df.loc[full_df.direction == directions[0]]
                secondary_dir = directions[0].title()

            primary_impact_times = primary_full.copy()
            secondary_impact_times = secondary_full.copy()

            # Show only travel times for active impact periods

            primary_impact_times.travel_time_minutes = np.where(
                (primary_impact_times.impact_present == "no") | 
                (primary_impact_times.impact_present == "No"), 
                "", 
                primary_impact_times.travel_time_minutes
                )

            secondary_impact_times.travel_time_minutes = np.where(
                (secondary_impact_times.impact_present == "no") | 
                (secondary_impact_times.impact_present == "No"), 
                "", 
                secondary_impact_times.travel_time_minutes
                )

            # Show only % Change for active impact periods
            primary_impact_times.percent_change = np.where(
                (primary_impact_times.impact_present == "no") | 
                (primary_impact_times.impact_present == "No"), 
                "", 
                primary_impact_times.percent_change
                )

            secondary_impact_times.percent_change = np.where(
                (secondary_impact_times.impact_present == "no") | 
                (secondary_impact_times.impact_present == "No"), 
                "", 
                secondary_impact_times.percent_change
                )

            # Progress bar update
            for i in range(80):
                window["_prog2_"].update_bar(i+1)

            # Conditional plot output: Only create graph for direction(s) with 
            # impacted periods present.
            if "yes" in primary_impact_times.impact_present.value_counts().index.tolist():
                # Primary Dir Travel Time Graph
                x_axis_primary = primary_full["date_time"]
                baseline_primary = primary_full["baseline_mean_TT"]

                layout1 = go.Layout(xaxis=dict(title="Date_Time"),
                    xaxis_rangeslider_visible = True)

                fig1 = make_subplots(
                    rows=2, 
                    cols=1,
                    shared_xaxes=True,      
                    vertical_spacing = 0.02
                    )

                fig1.update_layout(
                    xaxis2_rangeslider_visible = True
                    )

                fig1.update_layout(
                    title_text=f"{corridor} Travel Times {primary_dir.title()}" \
                        f" with {corridor_response}" \
                        f" due to {imp_type} ({period_start} - {period_end})")

                # This is the one where I need to change the tool tip
                ref_year=primary_full["reference_period"]
                day_name = primary_full["day_string"]
                interval = primary_full["interval"]
                
                fig1.add_trace(go.Bar(
                    x=x_axis_primary,
                    y= primary_impact_times.percent_change,
                    name= "% Change",
                    yaxis= "y2",
                    meta= primary_full["corridor_response"],
                    customdata= primary_full["impact_subtype"],
                    hovertemplate= "%{x}<br> Percent Change: %{y}%" \
                        "<br> Subtype: %{customdata}" \
                        "<br> Corridor Response: %{meta}",
                    marker_color="lightsalmon"                  
                    ),
                    row=2, 
                    col=1
                    )
                
                fig1.add_trace(go.Scatter(
                    x=x_axis_primary,
                    y=baseline_primary,
                    name= f"{baseline_month_year} Mean Travel Times",
                    line_color="dimgray",
                    text=primary_full["reference_period"],
                    
                    hovertemplate= "Reference Period: %{text}" \
                        "<br> Average Travel Time: %{y} minutes",
                    yaxis= "y1"                  
                    ),
                    row=1, 
                    col=1
                    )

                fig1.add_trace(go.Scatter(
                    x=x_axis_primary,
                    y=primary_impact_times.travel_time_minutes,
                    name= f"{impact_year} Impacted Travel Times",
                    meta= primary_full["corridor_response"],
                    customdata= primary_full["impact_subtype"],
                    hovertemplate= "Date/Time: %{x} <br> Travel Time: %{y} minutes" \
                        "<br> Subtype: %{customdata} <br> Corridor Response: %{meta}",
                    line_color="red",
                    yaxis= "y1",
                    connectgaps=False                    
                    ),
                    row=1, 
                    col=1
                    )
                
                fig1.update_yaxes(
                    title_text="Travel Time (minutes)", 
                    anchor="y1",
                    secondary_y=False
                    )
                fig1.update_yaxes(
                    title_text="% Change", 
                    row=2, 
                    col=1
                    )

                # Add customization of the graph title to reflect actual travel direction

                plotly.offline.plot(fig1, 
                    filename= f"{values['_target_folder_']}/{primary_dir}_graph.html")

            if "yes" in secondary_impact_times.impact_present.value_counts().index.tolist():
                # Secondary Dir Travel Time Graph

                x_axis_secondary = secondary_full["date_time"]
                baseline_secondary = secondary_full["baseline_mean_TT"]

                layout2 = go.Layout(xaxis=dict(title="Date_Time"),
                    xaxis_rangeslider_visible = True)

                fig2 = make_subplots(
                    rows=2, 
                    cols=1,
                    shared_xaxes=True,
                    vertical_spacing = 0.02)

                fig2.update_layout(
                    xaxis2_rangeslider_visible=True
                    )

                fig2.update_layout(
                    title_text=f"{corridor} Travel Times {secondary_dir.title()}" \
                        f" with {corridor_response}" \
                        f" due to {imp_type} ({period_start} - {period_end})")

                fig2.add_trace(go.Bar(
                    x=x_axis_secondary,
                    y= secondary_impact_times.percent_change,
                    name= "% Change",
                    yaxis= "y2",
                    meta= secondary_full["corridor_response"],
                    customdata= secondary_full["impact_subtype"],
                    hovertemplate= "%{x}<br> Percent Change: %{y}%" \
                        "<br> Subtype: %{customdata}" \
                        "<br> Corridor Response: %{meta}",
                    marker_color="lightsalmon"),
                    row=2, 
                    col =1
                    )
                
                fig2.add_trace(go.Scatter(
                    x=x_axis_secondary,
                    y=baseline_secondary,
                    name= f"{baseline_month_year} Mean Travel Times",
                    text=primary_full["reference_period"],
                    hovertemplate= "Reference Period: %{text}" \
                        "<br> Average Travel Time: %{y} minutes",
                    line_color="dimgray",
                    yaxis= "y1"),
                    row=1, 
                    col=1
                    )

                fig2.add_trace(go.Scatter(
                    x=x_axis_secondary,
                    y=secondary_impact_times.travel_time_minutes,
                    name= f"{impact_year} Impacted Travel Times",
                    meta= secondary_full["corridor_response"],
                    customdata= secondary_full["impact_subtype"],
                    hovertemplate= "Date/Time: %{x} <br> Travel Time: %{y} minutes" \
                        "<br> Subtype: %{customdata} <br> Corridor Response: %{meta}",
                    line_color="red",
                    yaxis= "y1",
                    connectgaps=False
                    ),
                    row=1, 
                    col=1
                    )
                
                fig2.update_yaxes(title_text="Travel Time (minutes)", anchor="y1",
                    secondary_y=False)
                fig2.update_yaxes(title_text="% Change", 
                    row=2, 
                    col=1
                    )

                # Add customization of the graph title to reflect actual travel direction.
                plotly.offline.plot(fig2, 
                    filename= f"{values['_target_folder_']}/{secondary_dir}_graph.html")

            # Progress bar update
            for i in range(90):
                window["_prog2_"].update_bar(i+1)
         
            # PDFs and CDFs

            # Select only rows for periods with active impacts.
            impacted_primary = primary_impact_times.loc[
                primary_impact_times["impact_present"].isin(["Yes", "yes"])
                ]
            
            impacted_secondary = secondary_impact_times.loc[
                secondary_impact_times["impact_present"].isin(["Yes", "yes"])
                ]
            
            impacted_primary.travel_time_minutes = pd.to_numeric(
                impacted_primary.travel_time_minutes, 
                errors='coerce'
                )

            impacted_secondary.travel_time_minutes = pd.to_numeric(
                impacted_secondary.travel_time_minutes, 
                errors='coerce'
                )

            x1 = np.sort(impacted_primary["travel_time_minutes"])

            meta1 = impacted_primary["corridor_response"]

            customdata1 = impacted_primary["impact_subtype"]

            x2 = np.sort(impacted_primary["baseline_mean_TT"])

            y1 = np.arange(1, len(x1) + 1)/(float(len(x1)))

            y2 = np.arange(1, len(x2) + 1)/(float(len(x2)))

            x3 = np.sort(impacted_secondary["travel_time_minutes"])

            meta2 = impacted_secondary["corridor_response"]

            customdata2 = impacted_secondary["impact_subtype"]

            x4 = np.sort(impacted_secondary["baseline_mean_TT"])

            y3 = np.arange(1,len(x3) + 1)/(float(len(x3)))

            y4 = np.arange(1, len(x4) + 1)/(float(len(x4)))

            layout3 = go.Layout(
                xaxis=dict(title="Travel Time"),
                yaxis=dict(title="Cumulative Density")
                )
   
            # Conditional plot output: Only create CDF for direction(s) with impacted periods present.
            
            if ("yes" in impacted_primary.impact_present.value_counts().index.tolist() 
                    and "yes" in impacted_secondary.impact_present.value_counts().index.tolist()):
                fig3 = make_subplots(
                    rows=1, 
                    cols=2,
                    subplot_titles= [
                        f"{corridor} Travel Times CDF {primary_dir.title()}," \
                            f" {corridor_response}, {imp_type}", 
                        f"{corridor} Travel Times CDF {secondary_dir.title()}," \
                            f" {corridor_response}, {imp_type}"
                        ]
                    )

                fig3.add_trace(go.Scatter(
                    x=x1,
                    y=y1,
                    name="Impacted Travel Times",
                    line_color="orange",
                    legendgroup="impact_group",
                    meta= meta1,
                    customdata= customdata1,
                    hovertemplate="Travel Time: %{x} minutes" \
                        "<br> Cumulative Probability: %{y}" \
                        "<br> Subtype: %{customdata} <br> Corridor Response: %{meta}",
                    ),
                    row=1, 
                    col=1
                    )
                fig3.add_trace(go.Scatter(
                    x=x2,
                    y=y2,
                    name="Baseline Mean Travel Times",
                    line_color="blue",
                    legendgroup="base_group",
                    hovertemplate="Travel Time: %{x} minutes" \
                        "<br> Cumulative Probability: %{y}",
                    ),
                    row=1, 
                    col=1
                    )

                fig3.add_trace(go.Scatter(
                    x=x3,
                    y=y3,
                    name="Impacted Travel Times",
                    line_color="orange",
                    showlegend=False,
                    legendgroup="impact_group",
                    meta= meta2,
                    customdata= customdata2,
                    hovertemplate="Travel Time: %{x} minutes" \
                        "<br> Cumulative Probability: %{y}" \
                        "<br> Subtype: %{customdata} <br> Corridor Response: %{meta}",
                    ),
                    row=1, 
                    col=2
                    )
                fig3.add_trace(go.Scatter(
                    x=x4,
                    y=y4,
                    name="Baseline Mean Travel Times",
                    line_color="blue",
                    showlegend=False,
                    legendgroup="base_group",
                    hovertemplate="Travel Time: %{x} minutes" \
                        "<br> Cumulative Probability: %{y}",
                    ),
                    row=1, 
                    col=2
                    )
          
            elif ("yes" in impacted_primary.impact_present.value_counts().index.tolist() 
                    and "yes" not in impacted_secondary.impact_present.value_counts().index.tolist()):
                fig3 = make_subplots(
                    rows=1, 
                    cols=1,
                    subplot_titles= f"{corridor} Travel Times CDF {primary_dir.title()}," \
                        f" {corridor_response}, {imp_type}"
                    )
                
                fig3.add_trace(go.Scatter(
                    x=x1,
                    y=y1,
                    name="Impacted Travel Times",
                    line_color="orange",
                    legendgroup="impact_group",
                    meta= meta1,
                    customdata= customdata1,
                    hovertemplate="Travel Time: %{x} minutes" \
                        "<br> Cumulative Probability: %{y}" \
                        "<br> Subtype: %{customdata}" \
                        "<br> Corridor Response: %{meta}",
                    ),
                    row=1, 
                    col=1
                    )

                fig3.add_trace(go.Scatter(
                    x=x2,
                    y=y2,
                    name="Baseline Mean Travel Times",
                    line_color="blue",
                    legendgroup="base_group",
                    hovertemplate="Travel Time: %{x} minutes" \
                        "<br> Cumulative Probability: %{y}",
                    ),
                    row=1, 
                    col=1
                    )

            else:    
                fig3 = make_subplots(
                    rows=1, 
                    cols=1,                   
                    subplot_titles= #[ 
                        f"{corridor} Travel Times CDF {secondary_dir.title()}," \
                            f" {corridor_response}, {imp_type}"
                        #]
                    )

                fig3.add_trace(go.Scatter(
                    x=x3,
                    y=y3,
                    name="Impacted Travel Times",
                    line_color="orange",
                    showlegend=False,
                    legendgroup="impact_group",
                    meta= meta2,
                    customdata= customdata2,
                    hovertemplate="Travel Time: %{x} minutes" \
                        "<br> Cumulative Probability: %{y}" \
                        "<br> Subtype: %{customdata}" \
                        "<br> Corridor Response: %{meta}",
                    ),
                    row=1, 
                    col=1
                    )

                fig3.add_trace(go.Scatter(
                    x=x4,
                    y=y4,
                    name="Baseline Mean Travel Times",
                    line_color="blue",
                    showlegend=False,
                    legendgroup="base_group",
                    hovertemplate="Travel Time: %{x} minutes \
                        <br> Cumulative Probability: %{y}",
                    ),
                    row=1, 
                    col=1
                    )

            fig3.update_yaxes(tick0 = 0.0, dtick = 0.05)
            fig3.update_yaxes(title_text="Cumulative Probability")
            fig3.update_xaxes(title_text="Travel Time (Minutes)")
            plotly.offline.plot(
                fig3, 
                filename=f"{values['_target_folder_']}/plotlyCDF.html")
            ########################################################################
            
             # Progress bar update
            
            for i in range(100):
                window["_prog2_"].update_bar(i+1)
            
            # Generate completion message

            window["_completion_text_2_"].update("Entries and charts exported to" \
                " destination folder. Review the charts before uploading your data to" \
                " the database.")
              
        except Exception as e:
            
            # Error handling
            
            window["_completion_text_2_"].update(
                "Something went wrong, please try again."
                )

            window["_prog2_"].update_bar(0)
            
            PrintException()
    
    elif event == "_upload_button_":

        try:
            while True:
                
                answer = sg.popup_ok_cancel("Are you sure you want to upload?")
                
                if answer == "Cancel":
                   
                   break
                
                else:
                
                    # Timestamp your entry.
                    
                    full_df["uploaded_timestamp"] = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                        )

                    # Convert times to UTC for storage in the database.
                    full_df.date_time = full_df.date_time.astype("str")
                    full_df.date_time = full_df.date_time.map(
                        lambda x: TimestampConverter(x)
                        )
                    
                    full_df.uploaded_timestamp = full_df.uploaded_timestamp.map(
                        lambda x: TimestampConverter(x)
                        )

                    window["_mongo_conn_msg_"].update("")
                    # Mongo connection.
                    
                    conn = str(values["_mongo_conn_"])


                    # Pass connection to the pymongo instance.
                    client = pymongo.MongoClient(conn)

                    # Connect to database

                    db = client.SHRP2_db

                    # Pass connection to the pymongo instance
                    client = pymongo.MongoClient(conn)

                    # Connect to database
                    # Note: May need to add a settings menu to select the database and 
                    # collection.

                    db = client.SHRP2_db
                
                    # Add records to database.

                    if values["_records_"] == True:
                        collection = db.records
                        
                    else:
                        collection = db.test

                    collection.insert_many(full_df.to_dict(orient="records"))
                    full_df = full_df[0:0]

                    window["_mongo_conn_msg_"].update("Entries added to the" \
                        " database.")
                    break
        except Exception as e:
            window["_mongo_conn_msg_"].update("Something went wrong. Check your" \
                " connection string.")
            # Error handling
            PrintException()
            
########################################################################
########################################################################
##################### QUERY TOOL LOOP ##################################
########################################################################

# Loop to refresh the Corridor ID list with a database query.
    
    elif event == '_refresh_':
        
        try:
            print("Reading Button")
            # Mongo connection
            conn = values["_mongo_conn2_"]
            # Pass connection to the pymongo instance
            client = pymongo.MongoClient(conn)
            # Connect to database
            db = client.SHRP2_db
            # Pass connection to the pymongo instance
            client = pymongo.MongoClient(conn)
            # Connect to database
            db = client.SHRP2_db
            # Connection to collection
            records = db.records

            # Prepare empty lists to update for the query

            ID_cor_type_list = []
            
            ID_urban_list = []

            ID_query_dict = {}

            # corridor type selection
            if values["_interstate_"] == True:
                ID_cor_type_list.append("Interstate")
            if values["_freeway_"] == True:
                ID_cor_type_list.append("Freeway")
            if values["_highway_"] == True:
                ID_cor_type_list.append("Highway")

            if len(ID_cor_type_list) > 0:
                ID_query_dict.update({
                    "f_system": {
                    "$in": ID_cor_type_list
                    }
                    })
            
            # Urban or rural selection
            if values["_urban2_"] == True:
                ID_urban_list.append("Urban")
            if values["_rural2_"] == True:
                ID_urban_list.append("Rural")

            if len(ID_urban_list) > 0:
                ID_query_dict.update({
                    "urban_rural": {
                    "$in": ID_urban_list
                    }
                    })

            # Build query

            ID_query = records.find(ID_query_dict)
            print("Finding query results")
            if records.count_documents(ID_query_dict) > 0:

                ID_test_df = pd.DataFrame(list(ID_query))

                print(ID_test_df.dtypes)

                corridor_list = ID_test_df.road.value_counts().index.tolist()

                corridor_list[:0] = ["All"]

                window.FindElement("_corridorselector_").Update(
                    values=corridor_list
                    )

        except Exception as e:           
            print(e)
            PrintException()
        
# Database Query Event Loop

    elif event == '_OK_BUTTON_4_':
        # Progress bar update
        
        # Reset result message.

        window["_query_result_msg_"].update(" ")
        
        for i in range(10):
            window["_prog3_"].update_bar(i+1)

        try:
            
            # Mongo connection.
            conn = values["_mongo_conn2_"]
            # Pass connection to the pymongo instance.
            client = pymongo.MongoClient(conn)
            # Connect to database.
            db = client.SHRP2_db
            # Pass connection to the pymongo instance.
            client = pymongo.MongoClient(conn)
            # Connect to database.
            db = client.SHRP2_db
            # Connection to collection.
            records = db.records

        except Exception as e:
            print(e)
            PrintException()

        for i in range(40):
            window["_prog3_"].update_bar(i+1)

        try:
            
            window["_query_result_msg_"].update(" ")
            # variables for collection
            
            cor_type_list = []
            travel_dir_list = []
            impact_type_list = []
            urban_list = []
            day_list = []

            query_dict = {}

            # Handle all possible combinations of start and end date entries.

            if (values["_start_date_inp_"]  != "" or 
                    values["_end_date_inp_"] != ""):

                if (values["_start_date_inp_"]  != "" and 
                        values["_end_date_inp_"] == ""):

                    start_date = TimestampConverter(values["_start_date_inp_"])
                    print(start_date)
                    query_dict.update({
                        "date_time": {
                            "$gte": start_date
                            }
                        })

                elif (values["_end_date_inp_"] != "" and 
                        values["_start_date_inp_"] == ""):

                    end_date = TimestampConverter(values["_end_date_inp_"])
                    print(end_date)
                    query_dict.update({
                        "date_time": {
                            "$lt": end_date
                            }
                        })

                elif (values["_start_date_inp_"]  != "" and 
                        values["_end_date_inp_"] != ""):

                    start_date = TimestampConverter(values["_start_date_inp_"])
                    end_date = TimestampConverter(values["_end_date_inp_"])
                    query_dict.update({
                        "date_time": {
                            "$gte": start_date,
                            "$lt": end_date
                            }
                        })
                else: 
                    break
            
            for i in range(50):
                window["_prog3_"].update_bar(i+1)

            # Filter day of the week with the string day names
            for key, value in weekday_key_dict.items():
                if values[key] == True:
                    day_list.append(value)

            query_dict.update({
                "day_string": {
                    "$in": day_list
                    }
            })

            # corridor type selection
            if values["_interstate_"] == True:
                cor_type_list.append("Interstate")

            if values["_freeway_"] == True:
                cor_type_list.append("Freeway")

            if values["_highway_"] == True:
                cor_type_list.append("Highway")

            if len(cor_type_list) > 0:
                query_dict.update({
                    "f_system": {
                    "$in": cor_type_list
                    }
                    })

            # Corridor ID selection

            if values["_corridorselector_"] != "All":
                query_dict.update({
                    "road": values["_corridorselector_"]
                    })

            # Impact Type selection

            if values["_wz2_"] == True:
                impact_type_list.append("work zone")
            if values["_inc2_"] == True:
                impact_type_list.append("incident")
            if values["_wthr2_"] == True:
                impact_type_list.append("weather")
            if values["_se2_"] == True:
                impact_type_list.append("special event")
            if values["_none2_"] == True:
                impact_type_list.append("None")
            
            if len(impact_type_list) > 0:
                query_dict.update({
                    "impact_type": {
                        "$in": impact_type_list
                        }
                    })

            # Impact subtype selection

            for i in range(60):
                window["_prog3_"].update_bar(i+1)

            if values["_sub_query_"] != "":
                query_dict.update({
                    "impact_subtype": values["_sub_query_"]
                    })

            # Corridor response selection
            
            if values["_corresp_query_"] != "":
                query_dict.update({
                    "corridor_response": values["_corresp_query_"]
                    })
            # Urban or rural selection
            if values["_urban2_"] == True:
                urban_list.append("Urban")
            if values["_rural2_"] == True:
                urban_list.append("Rural")

            if len(urban_list) > 0:
                query_dict.update({
                    "urban_rural": {
                    "$in": urban_list
                    }
                    })

            # travel selection
            if values["_primarydir_"] == True:
                travel_dir_list.append("NORTHBOUND")
                travel_dir_list.append("EASTBOUND")

            if values["_secondarydir_"] == True:
                travel_dir_list.append("SOUTHBOUND")
                travel_dir_list.append("WESTBOUND")

            if len(travel_dir_list) > 0:
                query_dict.update({
                    "direction": {
                    "$in": travel_dir_list
                    }
                    })

            for i in range(70):
                window["_prog3_"].update_bar(i+1)

            # Build query

            query = records.find(query_dict)
           
            if records.count_documents(query_dict) > 0:
                test_df = pd.DataFrame(list(query))
                print(test_df.dtypes)
                # Need to convert the timestamps back into local

                test_df.date_time = test_df.date_time.map(
                    lambda x: AsLocalTimeString(x)
                    )

                for i in range(80):
                    window["_prog3_"].update_bar(i+1)

                
                try:
                    test_df.uploaded_timestamp = test_df.uploaded_timestamp.map(
                        lambda x: AsLocalTimeString(x)
                        )
                except Exception as e:
                    PrintException()

                for i in range(90):
                    window["_prog3_"].update_bar(i+1)

                test_df.to_csv(
                    f"{values['_query_dest_']}/{values['_output_name_']}.csv",
                    index = False
                    )

                print(test_df.head(3))

                for i in range(100):
                    window["_prog3_"].update_bar(i+1)

                window["_query_result_msg_"].update("Your query results"\
                    " have been exported.")
            else:
                window["_query_result_msg_"].update("No entries match"\
                    " those criteria. Please try again.")
            
        except Exception as e:
            # Error handling
            window["_prog2_"].update_bar(0)
            print(e)
            PrintException()

########################################################################
########################################################################
################ DELETION TOOL LOOP ####################################
########################################################################

# Loop to refresh the Corridor ID list with a database query
    
    elif event == '_refresh2_':
        
        try:
            print("Reading Button")
            # Mongo connection.
            conn = values["_mongo_conn3_"]
            # Pass connection to the pymongo instance.
            client = pymongo.MongoClient(conn)
            # Connect to database.
            db = client.SHRP2_db
            # Pass connection to the pymongo instance.
            client = pymongo.MongoClient(conn)
            # Connect to database.
            db = client.SHRP2_db
            # Connection to collection.
            records = db.records

            # Prepare empty lists to update for the query.

            ID_cor_type_list = []
            
            ID_urban_list = []

            ID_query_dict = {}

            # corridor type selection.
            if values["_interstate2_"] == True:
                ID_cor_type_list.append("Interstate")
            if values["_freeway2_"] == True:
                ID_cor_type_list.append("Freeway")
            if values["_highway2_"] == True:
                ID_cor_type_list.append("Highway")

            if len(ID_cor_type_list) > 0:
                ID_query_dict.update({
                    "f_system": {
                    "$in": ID_cor_type_list
                    }
                    })
            
            # Urban or rural selection
            if values["_urban3_"] == True:
                ID_urban_list.append("Urban")
            if values["_rural3_"] == True:
                ID_urban_list.append("Rural")

            if len(ID_urban_list) > 0:
                ID_query_dict.update({
                    "urban_rural": {
                        "$in": ID_urban_list
                        }
                    })

            # Build query

            ID_query = records.find(ID_query_dict)
            print("Finding query results")
            if records.count_documents(ID_query_dict) > 0:

                ID_test_df = pd.DataFrame(list(ID_query))

                print(ID_test_df.dtypes)

                corridor_list = ID_test_df.road.value_counts().index.tolist()

                corridor_list[:0] = ["All"]

                window.FindElement("_corridorselector2_").Update(
                    values=corridor_list
                    )
        except Exception as e:
            print(e)
            PrintException()
        
# Database Delete Event Loop

    elif event == '_delete_button_':
        
        # Reset result message
        window["_delete_result_msg_"].update("")

        try:
            while True:
                answer = sg.popup_ok_cancel("Are you sure you want to delete records" \
                    " matching these criteria?")
                if answer == "Cancel":
                    break
                else:
                    # try:
                    
                    # Mongo connection
                    conn = values["_mongo_conn3_"]
                    # Pass connection to the pymongo instance
                    client = pymongo.MongoClient(conn)
                    # Connect to database
                    db = client.SHRP2_db
                    # Connection to collection
                    records = db.records

                    # variables for collection
                    
                    cor_type_list2 = []
                    travel_dir_list2 = []
                    impact_type_list2 = []
                    urban_list2 = []

                    query_dict2 = {}

                    
                    # Handle all possible combinations of start and end date entries.

                    if (values["_start_date_inp2_"]  != "" or 
                            values["_end_date_inp2_"] != ""):

                        if (values["_start_date_inp2_"]  != "" and 
                                values["_end_date_inp2_"] == ""):
                            
                            start_date = TimestampConverter(values["_start_date_inp2_"])
                            print(start_date)
                            query_dict2.update({
                                "date_time": {
                                    "$gte": start_date
                                    }
                                })

                        elif (values["_end_date_inp2_"] != "" and 
                                values["_start_date_inp2_"] == ""):

                            end_date = TimestampConverter(values["_end_date_inp2_"])
                            print(end_date)
                            query_dict2.update({
                                "date_time": {
                                    "$lt": end_date
                                    }
                                })

                        elif (values["_start_date_inp2_"]  != "" and 
                                values["_end_date_inp2_"] != ""):

                            start_date = TimestampConverter(values["_start_date_inp2_"])
                            end_date = TimestampConverter(values["_end_date_inp2_"])
                            query_dict2.update({
                                "date_time": {
                                    "$gte": start_date,
                                    "$lt": end_date
                                    }
                                })
                        else: 
                            break

                    # Filter by timestamp
                    if values["_timestamp_input_"] != "":
                        uploadtime = TimestampConverter(values["_timestamp_input_"])
                        query_dict2.update({
                            "uploaded_timestamp": {
                                "$eq": uploadtime
                                }
                            })

                    # corridor type selection
                    if values["_interstate2_"] == True:
                        cor_type_list2.append("Interstate")
                    if values["_freeway2_"] == True:
                        cor_type_list2.append("Freeway")
                    if values["_highway2_"] == True:
                        cor_type_list2.append("Highway")

                    if len(cor_type_list2) > 0:
                        query_dict2.update({
                            "f_system": {
                                "$in": cor_type_list2
                                }
                            })

                    # Corridor ID selection

                    if values["_corridorselector2_"] != "All":
                        query_dict2.update({
                            "road": values["_corridorselector"]
                            })

                    # Impact Type selection

                    if values["_wz3_"] == True:
                        impact_type_list2.append("work zone")

                    if values["_inc3_"] == True:
                        impact_type_list2.append("incident")

                    if values["_wthr3_"] == True:
                        impact_type_list2.append("weather")

                    if values["_se3_"] == True:
                        impact_type_list2.append("special event")

                    if values["_none3_"] == True:
                        impact_type_list2.append("None")
                    
                    if len(impact_type_list2) > 0:
                        query_dict2.update({
                            "impact_type": {
                                "$in": impact_type_list2
                                }
                            })

                    # Impact subtype selection

                    if values["_sub_query2_"] != "":
                        query_dict2.update({
                            "impact_subtype": values["_sub_query_"]
                            })

                    # Corridor response selection
                    
                    if values["_corresp_query2_"] != "":
                        query_dict2.update({
                            "corridor_response": values["_corresp_query_"]
                            })
                    # Urban or rural selection
                    if values["_urban3_"] == True:
                        urban_list2.append("Urban")

                    if values["_rural3_"] == True:
                        urban_list2.append("Rural")

                    if len(urban_list2) > 0:
                        query_dict2.update({
                            "urban_rural": {
                            "$in": urban_list2
                            }
                            })

                    # travel selection
                    if values["_primarydir2_"] == True:
                        travel_dir_list2.append("NORTHBOUND")
                        travel_dir_list2.append("EASTBOUND")

                    if values["_secondarydir2_"] == True:
                        travel_dir_list2.append("SOUTHBOUND")
                        travel_dir_list2.append("WESTBOUND")

                    if len(travel_dir_list2) > 0:
                        query_dict2.update({
                            "direction": {
                                "$in": travel_dir_list2
                                }
                            })
                    # Time stamp

                    if values["_timestamp_input_"]  != "":
                        stamp = TimestampConverter(values["_timestamp_input_"])
                        query_dict2.update({
                            "uploaded_timestamp": {
                                "$eq": stamp
                                }
                            })

                    # Build query
                
                    if records.count_documents(query_dict2) > 0:
                        query2 = records.delete_many(query_dict2)
                        window["_delete_result_msg_"].update(f"{query2.deleted_count} records have" \
                            " been deleted.")
                    else:
                        window["_delete_result_msg_"].update("No entries match those criteria." \
                            " Please try again.")
                        
                    break
        except Exception as e:
            PrintException()

########################################################################
#################### GRAPHING TOOL LOOPS ###############################
######################################################################## 
    
    elif event == "_graph_gen_":

        try:

            try:
                graph_file_path = values["_graph_input_file_"]
                graphing_df = pd.read_csv(graph_file_path, encoding="utf-8")
                graphing_df.interval = pd.to_datetime(
                    graphing_df["interval"], 
                    format= "%H:%M"
                    ).dt.hour
                print(graphing_df.head())
            except Exception:
                sg.Popup("File not found.")
            dest_folder = values['_target_folder_graph_']
            box_fig = go.Figure()
            cdf_fig = go.Figure()
            
            if values["_graph_x_corr_type_"] == True:
                x_axis_variable = "f_system"
                box_fig.update_xaxes(title_text = "Corridor Type")
                x_category = "Corridor Type"
            elif values["_graph_x_corr_subtype_"] == True:
                x_axis_variable = "class"
                box_fig.update_xaxes(title_text = "Corridor Subtype")
                x_category = "Corridor Subtype"
            elif values["_graph_x_imp_type_"] == True:
                x_axis_variable = "impact_type"
                box_fig.update_xaxes(title_text = "Impact Type")
                x_category = "Impact Type"
            elif values["_graph_x_imp_subtype_"] == True:
                x_axis_variable = "impact_subtype"
                box_fig.update_xaxes(title_text = "Impact Subype")
                x_category = "Impact Subtype"
            elif values["_graph_x_corr_resp_"] == True:
                x_axis_variable = "corridor_response"
                box_fig.update_xaxes(title_text = "Lane Closure(s)")
                x_category = "Lane Closure(s)"

            elif values["_graph_x_time_day_"] == True:
                # Need to grab the interval times from the input.
                
                period_1_start = values["_period_1_start_"]
                period_1_end = values["_period_1_end_"]
                period_2_start = values["_period_2_start_"]
                period_2_end = values["_period_2_end_"]

                # Subset the dataframe.
                graphing_df = graphing_df[
                    (graphing_df.interval >= period_1_start) &
                    (graphing_df.interval <= period_1_end) |
                    (graphing_df.interval >= period_2_start) &
                    (graphing_df.interval <= period_2_end)
                    ]
                
                # Need to add new column that classifies the data by time period and make that the x variable.
                graphing_df["time_range"] = ""
                graphing_df.loc[
                    (graphing_df.interval >= period_1_start) &
                    (graphing_df.interval <= period_1_end), "time_range"
                    ] = f"{period_1_start}:00 - {period_1_end}:00"

                graphing_df.loc[
                    (graphing_df.interval >= period_2_start) &
                    (graphing_df.interval <= period_2_end), "time_range"
                    ] = f"{period_2_start}:00 - {period_2_end}:00"
                print(graphing_df.time_range.value_counts())
                # Set your variables.
                x_axis_variable = "time_range"
                box_fig.update_xaxes(title_text = "Time of Day")
                x_category = "Time of Day"
                
            if values["_graph_col_urban_class_"] == True:
                color_variable = "urban_rural"
                color_category = "Urban Class"
            elif values["_graph_col_imp_type_"] == True:
                color_variable = "impact_type"
                color_category = "Impact Type"
            elif values["_graph_col_imp_subtype_"] == True:
                color_variable = "impact_subtype"
                color_category = "Impact Subtype"
            else:
                color_variable = "corridor_response"
                color_category = "Lane Closure(s)"

            hexcodes = [""
                "#00E5C4",
                "#01E5D8",
                "#02DEE6",
                "#03CBE6",
                "#04B8E7",
                "#06A5E7",
                "#0791E8",
                "#087FE8",
                "#096CE9",
                "#0B59E9",
                "#0C47EA",
                "#0D34EA",
                "#0E22EB",
                "#1010EB",
                "#2411EC",
                "#3812EC",
                "#4D14ED",
                "#6115EE",
                "#7516EE",
                "#8917EF",
                "#9C19EF",
                "#B01AF0",
                "#C41BF0",
                "#D71DF1",
                "#EA1EF1",
                "#F21FE6",
                "#F221D5",
                "#F322C3",
                "#F324B1",
                "#F425A0",
                "#F4268F",
                "#F5287E",
                "#F5296D",
                "#F62A5C",
                "#F72C4B",
                "#F72D3B",
                "#F8332F",
                "#F84630",
                "#F95932",
                "#F96B33",
                "#FA7E34",
                "#FA9036",
                "#FBA337",
                "#FBB539",
                "#FCC63A",
                "#FCD83C",
                "#FDEA3D",
                "#FDFB3F",
                "#F0FE40",
                "#DFFF41",
                ]

            # violin_color_index = 0
            line_color_index = 0
            cdf_divisor = (len(graphing_df[x_axis_variable].unique())*(len(
                                        graphing_df[color_variable].unique())))
            print(len(graphing_df[x_axis_variable].unique()))
            print(len(graphing_df[color_variable].unique()))
            print(f"The cdf_divisor is {cdf_divisor}")
            if values["_graph_col_none_"] != True:
                
                for i,color in enumerate(graphing_df[color_variable].unique()):
                    # violin_color_index += round(
                    #     int(
                    #         len(hexcodes)/len(graphing_df[color_variable].unique())
                    #         )
                    #     )
                    box_fig.add_trace(go.Violin(
                        x=graphing_df[x_axis_variable][graphing_df[color_variable] == color],
                        y=graphing_df["percent_change"][graphing_df[color_variable] == color],
                        name = color,
                        # marker = dict(
                        #     color = hexcodes[violin_color_index]
                        #     ),
                        box_visible=True,
                        meanline_visible=True,                    
                        ))

                box_fig.update_layout(violinmode="group")   
                # box_fig.update_layout(boxmode="group")
                box_fig.update_yaxes(title_text = "Percent Change (%)")
                box_fig.update_layout(title_text = f"Percent Change in Travel Time by" \
                    f" {x_category} and {color_category}",                      
                    )
            
                # Generate CDFs.
                for i, category in enumerate(graphing_df[x_axis_variable].unique()):
                
                    for j, color in enumerate(
                            graphing_df[color_variable][graphing_df[x_axis_variable] == category].unique()
                            ):
                    
                        line_color_index += round(int(len(hexcodes)/cdf_divisor))
                        sub_df = graphing_df[(graphing_df[color_variable] == color) &
                            (graphing_df[x_axis_variable] == category)
                            ]

                        x = np.sort(sub_df["percent_change"])               
                        
                        y = np.arange(1, len(x) + 1)/(float(len(x)))
                        cdf_fig.add_trace(go.Scatter(
                            mode="lines",
                            # line = dict(
                            #     color = hexcodes[line_color_index]
                            # ),
                            connectgaps=True,
                            x=x,
                            y=y,
                            hovertemplate="Percent Change (%): %{x} <br> Cumulative" \
                                " Probability: %{y}",
                            name= f"{category}, {color}",
                            ))
            else:
                
                box_fig.add_trace(go.Violin(
                    x=graphing_df[x_axis_variable],
                    y=graphing_df["percent_change"],
                    box_visible=True,
                    meanline_visible=True,
                    # notched=True
                    ))

                box_fig.update_layout(violinmode="group")
                # box_fig.update_layout(boxmode="group")
                box_fig.update_yaxes(title_text = "Percent Change (%)")

                box_fig.update_layout(title_text = f"Percent Change in Travel Time" \
                    f" by {x_category}"
                    )

                for i, category in enumerate(graphing_df[x_axis_variable].unique()):
                    x= np.sort(graphing_df["percent_change"][graphing_df[x_axis_variable] == category])
                    y = np.arange(1, len(x) + 1)/(float(len(x)))
                    
                    cdf_fig.add_trace(go.Scatter(
                        mode="lines",
                        connectgaps=True,
                        x=x,
                        y=y,
                        hovertemplate="Percent Change (%): %{x} <br> Cumulative" \
                            " Probability: %{y}",
                        name= category,         
                        ))

            cdf_fig.update_yaxes(tick0 = 0.0, dtick = 0.05)

            cdf_fig.update_xaxes(title_text = "Percent Change in Travel Time (%)")

            cdf_fig.update_yaxes(title_text = "Cumulative Distribution Value (%)")

            cdf_fig.update_layout(title_text = f"Cumulative Distribution Functions of" \
                f" Percent Change in Travel Time by {x_category}")

            cdf_name = values["_final_ECDF_name_"]

            box_name = values["_final_boxplot_name_"]

            plotly.offline.plot(cdf_fig, filename = f"{dest_folder}/{cdf_name}.html")

            plotly.offline.plot(box_fig, filename= f"{dest_folder}/{box_name}.html")

        except Exception as e:
            print(e)
            PrintException()

        # For some reason, the following block of code kills the OK button if it's 
        # included first. Doesn't seem to cause problems down here, though.

    elif event == "_wz2_" or "_inc2_" or "_wthr2_" or "_se2_":
        try:
            if sum([
                    values["_wz2_"], 
                    values["_inc2_"], 
                    values["_wthr2_"], 
                    values["_se2_"]
                    ]) > 1:

                window["_sub_query_"].update(disabled=True)

            elif sum([
                    values["_wz2_"], 
                    values["_inc2_"], 
                    values["_wthr2_"], 
                    values["_se2_"]
                    ]) == 1:
                    
                window["_sub_query_"].update(disabled=False)
                
                # Subtype Conditions for Query Tab
                # The subtype list automatically updates if you reduce your toggle 
                # from multiple impact types to one.
                
                if event in impact_type_key_list:
                    for key, value in impact_type_key_dict.items():
                        if values[key] == True:
                            window.FindElement("_sub_query_").Update(values=value)

            else:
                window["_sub_query_"].update(disabled=False)

        except Exception as e:
            print(e)
            PrintException()

window.close()