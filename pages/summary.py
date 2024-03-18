"""
This page provides summary statistics for a selected variable.
It tabulates and shows a count/frequency distribution.
"""

from dash import html, dcc, callback, Input, Output, State
import plotly.express as px
import dash_ag_grid as dag
import pandas as pd
import dash

# register page to app with path used to call page
dash.register_page(
    __name__, 
    path="/pages/summary.py", 
    title="Summary Statistics"
)

def generate_control_card():
    """

    :return: A Div containing controls for uploading data
      and displaying graphs and tables.
    """
    return html.Div(
        id="control-card",
        children=[
            # Variable Selection
            html.P("Select Variable:"),
            dcc.Dropdown(
                id="variable-select",
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
            html.Br(),
            html.Hr(),
            html.Br(),
            html.Button(
                "Copy Table",
                id="copy-button",
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
                max=1600, 
                step=50, 
                value=950,
                marks={x: str(x) for x in [400, 600, 800, 1000, 1200, 1400, 1600]},
                className="slider-custom"
            ),
            html.Br(),
            html.Hr(),
            html.Br(),
            html.Div(
                id="var-description",
                className="var-description",
            ),
        ],
    )

def create_summary_table(data, var, courses):

    uploaded_data = pd.DataFrame(data)

    if len(courses) > 0:
        data = uploaded_data.loc[uploaded_data['COU_CMV'].isin(courses)]
    else:
        data = uploaded_data

    table = pd.DataFrame()
    uploaded_data = pd.DataFrame(data)
    categories = uploaded_data[var].unique()
    categories.sort()
    table["Categories"] = categories
    table["Counts"] = uploaded_data[var].value_counts().sort_index(ascending=True).to_list()
    table["Proportions"] = uploaded_data[var].value_counts(normalize=True).sort_index(ascending=True).to_list()
    table["Percentages"] = table["Proportions"] * 100 
    return table.round(2)

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
            html.Div(id="desc-stats-table"),
            html.Br(),
            html.Div(id="desc-stats-graph")
        ]
    ),
    # This div ensures output is sent to clipboard
    html.Div(id="copy-output")
])

@callback(
    Output("variable-select", "options"),
    [Input("store-data", "data")]
)   
def get_all_vars(data):
    """
    add a concatenated column for course name and section and fix the filter to show that
    """
    df = pd.DataFrame(data)

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

    data_var_dict = [{'label': i, 'value': i} for i in df.columns]

    if any(d1["value"] == d2["value"] for d1 in data_var_dict for d2 in target_var_dict):
        return target_var_dict
    else:
        return data_var_dict
    
@callback(
    Output("course-filter", "options"),
    [Input("store-data", "data"),]
)
def get_courses(data):
    df = pd.DataFrame(data)
    return df["COU_CMV"].unique()

@callback(
    Output("desc-stats-table", "children"),
    [
        Input("store-data", "data"),
        Input("variable-select", "value"),
        Input("course-filter", "value")
    ]
)
def create_dash_summary_table(data,var, courses):
    table = create_summary_table(data, var, courses)
    table["Percentages"] = (table["Percentages"]/100).map("{:.2%}".format)
    return dag.AgGrid(
        id="desc-table",
        columnDefs = [{"field": i} for i in table.columns],
        rowData = table.to_dict('records'),
        columnSize="responsiveSizeToFit",
    )   

@callback(
    Output("desc-stats-graph", "children"),
    [
        Input("store-data", "data"),
        Input("variable-select", "value"),
        Input("course-filter", "value"),
        Input("figure-width", "value")
    ]
)
def create_frequency_bar_plot(data, var, courses, width):
    table = create_summary_table(data, var, courses)
    table["Categories"] = table["Categories"].astype(str)
    config = {
        "modeBarButtonsToRemove": ['lasso2d', 'select2d']
    }
    fig = px.bar(
        table, 
        x='Categories', 
        y='Percentages',
        template="plotly_white",
        text= [
            f"{percentage}  ({count})" for count, percentage in zip(
                table['Counts'], 
                (table['Percentages']/100).map("{:.2%}".format)
                )
            ],
        range_y=[0, 110],
    )
    fig.update_traces(
        textposition="outside",
        marker_color="#D31245"
    )
    fig.update_layout(width=int(width))
    return dcc.Graph(id="freq-graph", figure=fig, config=config)

@callback(
    Output("copy-output", "children"),
    Input("copy-button", "n_clicks"),
    Input("desc-table", "rowData"),
)
def custom_copy(_, data):
    dff = pd.DataFrame(data)
    return dff.to_clipboard(index=False, excel=True)

@callback(
    Output("var-description", "children"),
    [Input("variable-select", "value")]
)
def get_var_description(var):
    if var is None:
        return ["""
            Please select a variable to see its details.
        """]
    else:
        return [
            html.P(var),
            html.P("\nAdd descriptions.")
        ]