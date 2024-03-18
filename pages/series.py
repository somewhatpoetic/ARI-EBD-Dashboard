"""
This page allows visualizations to compare the differing rates of enrollment
over the FY periods.
"""

from dash import html, dcc, callback, Input, Output
import plotly.express as px
import dash_ag_grid as dag
import pandas as pd
import dash

# register page to app with path used to call page
dash.register_page(__name__, path="/pages/series.py")

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
            html.Br(),
            html.P("Select Period:"),
            dcc.Dropdown(
                id="select-time",
                options=[
                    { "label": "Year", "value": "FY"},
                    { "label": "Year and Term", "value": "YRTR"},
                    # { "label": "Fall Semesters Only","value": "fall"},
                    # { "label": "Spring Semesters Only","value": "spring"},
                ],
                value="FY"
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
                id="copy-button-series",
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
            html.Div(id="series-table"),
            html.Br(),
            html.Div(id="series-graph")
        ]
    ),
    html.Div(id="copy-output-series")
])

@callback(
    Output("series-table", "children"),
    [
        Input("store-data", "data"),
        Input("variable-select", "value"),
        Input("select-time", "value"),
        Input("course-filter", "value")
    ]
)
def create_series_table(data, var, period, courses):
    uploaded_data = pd.DataFrame(data)

    if len(courses) > 0:
        df = uploaded_data.loc[uploaded_data['COU_CMV'].isin(courses)]
    else:
        df = uploaded_data

    if var and period is not None:
        ct = pd.crosstab(
            df[period], 
            df[var], 
        ).reset_index()
        ct_dict = ct.to_dict("records")

        f_col = [{"field": ct.columns[0], "pinned": "left", "lockPinned": True}]
        all_cols = [{"field" : i } for i in ct.columns[1:]]
    
    return dag.AgGrid(
        id="series-ag-table",
        columnDefs= f_col + all_cols,
        rowData=ct_dict,
        columnSize="responsiveSizeToFit",
    )

@callback(
    Output("series-graph", "children"),
    [
        Input("store-data", "data"),
        Input("variable-select", "value"),
        Input("colorblind-button", "n_clicks"),
        Input("select-time", "value"),
        Input("course-filter", "value"),
        Input("figure-width", "value")
    ]
)
def create_series_graph(data, var, clks, period, courses, width):
    uploaded_data = pd.DataFrame(data)

    if len(courses) > 0:
        df = uploaded_data.loc[uploaded_data['COU_CMV'].isin(courses)]
    else:
        df = uploaded_data

    df[period] = df[period].astype(str)

    dt = df.groupby([period, var]).size().reset_index(name="Count")

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

    fig = px.line(
        dt, 
        x=period, 
        y="Count", 
        color=var,
        template="plotly_white",
        markers=True,
        text="Count",
        color_discrete_sequence = target_color_sequence
    )
    fig.update_traces(textposition="top left")
    fig.update_xaxes(categoryorder='category ascending')
    fig.update_layout(width=int(width))

    config = {
        "modeBarButtonsToRemove": ['lasso2d', 'select2d']
    } 
    return dcc.Graph(figure=fig, config=config)

@callback(
    Output("copy-output-series", "children"),
    Input("copy-button-series", "n_clicks"),
    Input("series-ag-table", "rowData"),
)
def custom_copy(_, data):
    dff = pd.DataFrame(data)
    return dff.to_clipboard(index=False, excel=True)