"""
This page is where equity analysis is performed.

A table is generated that showcases the percentage difference in equity, 
given a base equity threshold or level to compare to.

It displays a graph that visualizes this difference.
"""

from dash import html, dcc, callback, Input, Output
import plotly.express as px
import dash_ag_grid as dag
import pandas as pd
import numpy as np
import math
import dash

# register page to app with path used to call page
dash.register_page(__name__, path="/pages/equity.py")

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
            # Institution Success Rate User Input
            html.Br(),
            html.P("Institution Success Rate (%):"),
            dcc.Input(
                id="threshold", 
                type="number", 
                value=90
            ),
            html.Br(),
            html.Br(),
            html.Button(
                "Show Rate in Table",
                id="show-isr",
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
            html.Button(
                "Copy Table",
                id="copy-button-eq",
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

def create_success_rate_table(data, value, threshold, courses, isr):
    """
    
    :params: data: upload data in dict format.
    :params: value: selected variable.
    :params: threshold: user entered threhold.
    :params: courses: a list of courses.

    :return: DataFrame
    """
    # Convert dictionary to a DataFrame
    uploaded_data = pd.DataFrame(data)

    if len(courses) > 0:
        df = uploaded_data.loc[uploaded_data['COU_CMV'].isin(courses)]
    else:
        df = uploaded_data

    # Create an empty DataFrame for the main table
    main_table = pd.DataFrame()

    # Get unique values and sort alphabetically
    categories = df[value].unique()
    categories.sort()

    # Assign all calculated values to variables into empty df
    main_table["Categories"] = categories
    main_table["Counts"] = df[value].value_counts().sort_index(ascending=True).to_list()
    main_table["Course Success"] = df.groupby(value)["COURSE_SUCCESS"].apply(lambda x: (x == "Course Success").sum()).to_list()
    main_table["Course Success Rate (%)"] = (main_table["Course Success"] / main_table["Counts"]) * 100

    if isr % 2 != 0 :
        main_table["Institution Success Rate (%)"] = [threshold] * len(main_table["Categories"])

    main_table["Equity Gap (%)"] = main_table["Course Success Rate (%)"] - threshold

    return main_table.round(2)


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
            html.Div(id="equity-gap-table"),
            html.Br(),
            html.Div(id="equity-gap-graph")
        ]
    ),
    html.Div(id="copy-output-eq")
])

@callback(
    Output("equity-gap-table", "children"),
    [
        Input("store-data", "data"),
        Input("variable-select", "value"),
        Input("threshold", "value"),
        Input("course-filter", "value"),
        Input("show-isr", "n_clicks")
    ]
)
def create_success_dash_table(data, value, threshold, courses, clks):
    main_table = create_success_rate_table(data, value, threshold, courses, clks)

    # Convert the DataFrame to a Dash DataTable
    return dag.AgGrid(
        id="eq-gap-table",
        columnDefs=[{"field" : i} for i in main_table.columns],
        rowData=main_table.to_dict("records"),
        columnSize="responsiveSizeToFit",
    )

@callback(
    Output("equity-gap-graph", "children"),
    [
        Input("store-data", "data"),
        Input("variable-select", "value"),
        Input("threshold", "value"),
        Input("course-filter", "value"),
        Input("colorblind-button", "n_clicks"),
        Input("figure-width", "value")
    ]
)
def create_equity_graph(data, value, threshold, courses, clks, width):
    main_table = create_success_rate_table(data, value, threshold, courses, 0)

    if clks % 2 == 1:
        main_table["Color"] = np.where(main_table["Equity Gap (%)"] < 0, '#E1BE6A', '#40B0A6')
    else:    
        main_table["Color"] = np.where(main_table["Equity Gap (%)"] < 0, '#D31245', '#A6B0B7')

    max_eq = max(main_table["Equity Gap (%)"])
    min_eq = min(main_table["Equity Gap (%)"])

    if abs(max_eq) > abs(min_eq):
        upper_ylim = math.ceil(max_eq) + 4
        lower_ylim = -upper_ylim
    else:
        lower_ylim = math.floor(min_eq) - 4
        upper_ylim = -lower_ylim
    
    fig = px.bar(
        main_table, 
        y="Equity Gap (%)", 
        x="Categories",
        barmode="relative",
        template="plotly_white",
        text_auto=True,
        range_y=[lower_ylim, upper_ylim]
    )
    fig.add_hline(
        y=0, 
        line_width=1, 
        line_dash="solid", 
        line_color="black"
    )
    fig.update_traces(
        marker_color=main_table["Color"],
        textposition="outside"
    )
    fig.update_layout(width=int(width))
    config = {
        "modeBarButtonsToRemove": ['lasso2d', 'select2d']
    }
    return dcc.Graph(figure=fig, config=config)

@callback(
    Output("copy-output-eq", "children"),
    Input("copy-button-eq", "n_clicks"),
    Input("eq-gap-table", "rowData"),
)
def custom_copy(_, data):
    dff = pd.DataFrame(data)
    return dff.to_clipboard(index=False, excel=True)

@callback(
    Output("show-isr", "style"),
    [Input("show-isr", "n_clicks")]
)
def psuedo_select(clks):
    clks += 1
    style = {
        "background" : "#D31245",
        "color" : "#fff",
        "border-color" : "#D31245"
    }
    return style if clks % 2 == 0 else {}