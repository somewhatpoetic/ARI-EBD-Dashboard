"""
This page displays crosstabulations between two selected variables.
It also shows a heatmap for better visualization.
"""

from dash import html, dcc, callback, Input, Output
import plotly.express as px
import dash_ag_grid as dag
import pandas as pd
import math
import dash

# register page to app with path used to call page
dash.register_page(
    __name__, 
    path="/pages/crosstabs.py"
)

def get_target_var_dict():
    target_var_dict = [
        # {"label" : "Fiscal Year", "value" : "FY"},
        # {"label" : "Term", "value" : "TERM_NAME"},
        # {"label" : "Term Type", "value" : "TermType"},
        # {"label" : "Delivery Method", "value" : "DELIVERY_METHOD"},
        # {"label" : "Grade", "value" : "GRADE"},
        # {"label" : "Course Success", "value" : "COURSE_SUCCESS"},
        # {"label" : "Admission Category", "value" : "ADMISSION_CATEGORY"},
        # {"label" : "Age Category", "value" : "AGE_CATEGORY"},
        # {"label" : "Student Classification", "value" : "STUDENT_CLASSIFICATION"},
        # {"label" : "Student Level", "value" : "STUDENT_LEVEL"},
        # {"label" : "New or Continuing Student", "value" : "NEW_CONTINUING_STUDENT"},
        # {"label" : "Student Load", "value" : "STUDENT_LOAD"},
        # {"label" : "Gender", "value" : "STUDENT_GENDER"},
        # {"label" : "Underrepresented Classification", "value" : "UNDERREPRESENTED_DESC"},
        # {"label" : "First Generation (Federal)", "value" : "FIRST_GEN_FED_DESC"},
        # {"label" : "First Generation (Minnesota)", "value" : "FIRST_GEN_MN_DESC"},
        # {"label" : "Pell Eligibility", "value" : "PELL_ELG_DESC"},
        # {"label" : "Pell Recipience", "value" : "PELL_RECPT_DESC"},
        # {"label" : "Reported Race/Ethnicity", "value" : "REPORTING_RACE_ETHNICITY"},
        # {"label" : "Student of Color Classification", "value" : "STUDENT_OF_COLOR_DESC"},
    ] 
    return target_var_dict

def generate_control_card():
    """

    :return: A Div containing controls for uploading data
      and displaying graphs and tables.
    """
    return html.Div(
        id="control-card",
        children=[
            # Variable Selection
            html.Div(id="variable-selection"),

            # Variable Selection
            html.P("Select Rows:"),
            dcc.Dropdown(
                id="variable-select-1",
                options=[]
            ),
            # Variable Selection
            html.Br(),
            html.P("Select Columns:"),
            dcc.Dropdown(
                id="variable-select-2",
                options=[]
            ),
            # Course Filtering
            html.Br(),
            html.P("Filter Courses:"),
            dcc.Dropdown(
                id="course-filter",
                options=[], 
                multi=True,
                value=[]
            ),
            # Show totals option
            html.Br(),
            html.Button(
                "Show Totals",
                id="toggle-totals",
                n_clicks=0
            ),
            html.Br(),
            html.Br(),
            html.Hr(),
            html.Br(),
            html.P("Adjust Graph Width:"),
            dcc.Slider(
                id="figure-width", 
                min=400, 
                max=1000, 
                step=50, 
                value=950,
                marks={x: str(x) for x in [400, 500, 600, 700, 800, 900, 1000]},
                className="slider-custom"
            ),
            html.Br(),
            html.Hr(),
            html.Br(),
            html.Button(
                "Copy Table",
                id="copy-button-cts",
                n_clicks=0
            ),
            html.Br(),
            html.Br(),
            html.Button(
                "Colorblind Mode",
                id="colorblind-button",
                n_clicks=0,
            ),
        ],
    )

# all content goes here
layout = html.Div([
    html.Div(
        id="left-column",
        className="three columns",
        children=[
            generate_control_card()
        ]
    ),
    html.Div(
        id="right-column",
        className="nine columns",
        children=[
            html.Br(),
            html.Div(id="crosstabs"), 
            html.Br(),
            html.Div(id="grouped-bar"),
        ]
    ),
    html.Div(id="copy-output-cts")
])

@callback(
    Output("variable-select-1", "options"),
    [Input("store-data", "data")]
)   
def get_all_vars(data):
    df = pd.DataFrame(data)

    target_var_dict = get_target_var_dict()
    data_var_dict = [{'label': i, 'value': i} for i in df.columns]

    if any(d1["value"] == d2["value"] for d1 in data_var_dict for d2 in target_var_dict):
        return target_var_dict
    else:
        return data_var_dict
    
@callback(
    Output("variable-select-2", "options"),
    [Input("store-data", "data")]
)   
def get_all_vars(data):
    df = pd.DataFrame(data)

    target_var_dict = get_target_var_dict()
    data_var_dict = [{'label': i, 'value': i} for i in df.columns]

    if any(d1["value"] == d2["value"] for d1 in data_var_dict for d2 in target_var_dict):
        return target_var_dict
    else:
        return data_var_dict
    
@callback(
    Output("crosstabs", "children"),
    [
        Input("store-data", "data"),
        Input("variable-select-1", "value"),
        Input("variable-select-2", "value"),
        Input("toggle-totals", "n_clicks"),
        Input("course-filter", "value")
    ]
)
def create_crosstab(data, var1, var2, clks, courses):
    uploaded_data = pd.DataFrame(data)

    if len(courses) > 0:
        df = uploaded_data.loc[uploaded_data['COU_CMV'].isin(courses)]
    else:
        df = uploaded_data

    ct = pd.crosstab(
        df[var1], 
        df[var2], 
        margins= True if clks % 2 == 1 else False
    ).reset_index()
    ct_dict = ct.to_dict("records")

    f_col = [{"field": ct.columns[0], "pinned": "left", "lockPinned": True}]
    all_cols = [{"field" : i } for i in ct.columns[1:]]

    return dag.AgGrid(
        id="cts",
        columnDefs=f_col + all_cols,
        rowData=ct_dict,
        columnSize="responsiveSizeToFit",
    )

@callback(
    Output("grouped-bar", "children"),
    [
        Input("store-data", "data"),
        Input("variable-select-1", "value"),
        Input("variable-select-2", "value"),
        Input("colorblind-button", "n_clicks"),
        Input("course-filter", "value"),
        Input("figure-width", "value")
    ]
)
def create_groupedbar(data, var1, var2, clks, courses, width):
    uploaded_data = pd.DataFrame(data)

    if len(courses) > 0:
        df = uploaded_data.loc[uploaded_data['COU_CMV'].isin(courses)]
    else:
        df = uploaded_data
    
    df[var1] = df[var1].astype(str)
    df[var2] = df[var2].astype(str)

    max_num = max(df.groupby([var1, var2]).size().reset_index(name="counts")["counts"])
    upper_ylim = (math.ceil(max_num * (10**-2)) / (10**-2)) + 2

    if clks % 2 == 0:
        target_color_sequence = [ 
            "#9e0e34", "#d31245", "#db416a", 
            "#e0597c", "#e988a2", "#eda0b4", 
            "#f1b7c7", "#f6cfd9",
        ]
    else:
        target_color_sequence = [
            '#377eb8', '#ff7f00', '#4daf4a',
            '#f781bf', '#a65628', '#984ea3',
            '#999999', '#e41a1c',
        ]
    
    if var1 and var2 is not None:
        fig = px.histogram(
            df, 
            x=var1, 
            color=var2, 
            barmode="group",
            template="plotly_white",
            text_auto=True,
            range_y=[0, upper_ylim],
            color_discrete_sequence=target_color_sequence
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            yaxis_title_text="Count",
            width=int(width)
        )

    config = {
        "modeBarButtonsToRemove": ['lasso2d', 'select2d']
    }    

    return dcc.Graph(figure=fig, config=config)

@callback(
    Output("toggle-totals", "style"),
    [Input("toggle-totals", "n_clicks")]
)
def psuedo_select(clks):
    clks += 1
    style = {
        "background" : "#D31245",
        "color" : "#fff",
        "border-color" : "#D31245"
    }
    return style if clks % 2 == 0 else {}

@callback(
    Output("copy-output-cts", "children"),
    Input("copy-button-cts", "n_clicks"),
    Input("cts", "rowData"),
)
def custom_copy(_, data):
    dff = pd.DataFrame(data)
    return dff.to_clipboard(index=False, excel=True)

@callback(
    Output("colorblind-button", "style"),
    [Input("colorblind-button", "n_clicks")]
)
def psuedo_select(clks):
    clks += 1
    style = {
        "background" : "#D31245",
        "color" : "#fff",
        "border-color" : "#D31245"
    }
    return style if clks % 2 == 0 else {}