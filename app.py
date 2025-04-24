from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import base64
import dash
import io

# Instantiate App object
app = dash.Dash(
    __name__,
    meta_tags=[
        {
            "name": "viewport", 
            "content": "width=device-width, initial-scale=1"
        }
    ],
    use_pages=True,
)

# Add title to display on window
app.title = "EDCAD"

# Instantiate server
server = app.server
app.config.suppress_callback_exceptions = True

# All visible contents go here
app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[
                # Image & logo. Links to the landing page and erases session data.
                dcc.Link(
                    children=[
                        html.Img(src=dash.get_asset_url("Antiracism Institute Banner 2.png"))
                    ], 
                    href="/", 
                    className="orgtitle-pill"
                ),
                # Navigational links ot pages.
                html.Div(
                    id="navlinks",
                    className="navoptions",
                    children=[
                        dcc.Link("Summary Statistics", href="/pages/summary.py", className="navpills"),
                        dcc.Link("Crosstabs", href="/pages/crosstabs.py", className="navpills"),
                        dcc.Link("Time Series", href="/pages/series.py", className="navpills"),
                        dcc.Link("Equity Analysis", href="/pages/equity.py", className="navpills"),
                    ]
                )
            ],
        ),
        # Secondary banner to show meta information from uploaded file.
        html.Div(
            id="secondary-banner",
            className="secondary-banner",
        ),
        # Page contents from individual page files.
        dash.page_container,
        # Object that stores uploaded data for use in callbacks across app.
        dcc.Store(
            id="store-data",
            storage_type="session",
        ),
    ]
)

@app.callback(
    Output("secondary-banner", "children"),
    [
        Input("upload-data", "contents"),
        Input("upload-data", "filename")
    ]
)
def display_secondary_banner(contents, filename):
    """
    :params: contents: data from uploaded file
    :params: filename: filename of uploaded file

    :return: html output of years, counts and success rate from file if 
        file exists.
    """
    if contents is not None:
        return [
            html.Div(
                children=["File: ", filename]
            ),
            html.Div(
                className="sb-meta",
                children=[
                    html.Div(
                        id="years",
                        className="sb-metainfo",
                    ),
                    html.Div(
                        id="enrolled",
                        className="sb-metainfo",
                    ),
                    html.Div(
                        id="overall-success-rate",
                        className="sb-metainfo",
                    ),
                ]
            )
        ]
    else:
        return [html.Div(children=["Please upload a file."])]

@app.callback(
    Output("years", "children"),
    Input("store-data", "data")
)
def get_years_from_data(data):
    """
    :params: data: uploaded data

    :return: range of years in file
    """

    df = pd.DataFrame(data)
    years = df["FY"].unique()

    if len(years) > 1:
        return [
            html.Div([
                "Years: ", min(years), "-", max(years)
            ])
        ]
    else:
        year = years[0]
        return ["Year: ", year]
    
@app.callback(
    Output("enrolled", "children"),
    [Input("store-data", "data")]
)
def get_enrolled_count(data):
    """
    :params: data: uploaded data

    :return: counts of students
    """

    df = pd.DataFrame(data)
    return ["Enrolled: ", len(df.index)]

@app.callback(
    Output("overall-success-rate", "children"),
    [Input("store-data", "data")]
)
def get_overall_success_rate(data):
    """
    :params: data: uploaded data

    :return: overall course success rate
    """

    df = pd.DataFrame(data)
    counts = df["COURSE_SUCCESS"].value_counts()
    sr = (counts["Course Success"] / df["COURSE_SUCCESS"].count()) * 100
    formatted_sr = "{:.2f}%".format(sr)

    return ["Overall Success Rate: ", formatted_sr]

# Run the server
if __name__ == "__main__":
    app.run()
