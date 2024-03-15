"""
This page provides information about the application.
This is also where the data to be analyzed is uploaded.
"""

from dash import html, dcc, callback, Input, Output
import pandas as pd
import base64
import dash
import io

# register page to app with path used to call page
dash.register_page(__name__, path="/")

def parse_contents(contents, filename):
    """
    
    :params: contents: list of data from uploaded file.
    :params: filename: name of file.
    :params: date: date of upload.

    :return: DataFrame
    """
    _, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assuming user uploads a csv file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assuming user uploads an excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return None

    return df

def generate_control_card():
    """

    :return: A Div containing controls for uploading data
      and displaying graphs and tables.
    """
    return html.Div(
        id="control-card",
        children=[
            # Data Upload Dialog
            html.P("Upload Data:"),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ', 
                    html.A('Select File')
                ]),
                className="upload"
            ),
            # html.Div(
            #     className="developer-info",
            #     children=[
            #         dcc.Markdown(children=[
            #             "_Developed by Nazimuddin Shaikh_"
            #         ])
            #     ]
            # )
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
            html.H4("Antiracism Institute for Teaching and Research"),
            html.P(
                """
                The Antiracism Institute for Teaching and Research (Antiracism Institute) is a faculty-led 
                initiative that supports antiracist projects to challenge racism on individual and institutional 
                levels and contribute to systemic change at St. Cloud State University and in higher education 
                across the country. In addition, the Antiracism Institute works collaboratively with the Minnesota 
                State System initiatives and other higher education and K-12 institutions in Minnesota and across 
                the country to promote antiracist work.
                """
            ),
            html.Br(),
            html.H4("About the Dashboard"),
            html.P(
                """
                Insert introduction to application and the purpose of each 
                page. Upload data to begin.
                """
            ),
        ]
    ),
])

@callback(
    Output('store-data', 'data'),
    [
        Input('upload-data', 'contents'),
        Input('upload-data', 'filename'),
    ]
)
def update_output(contents, filename):
    if contents is not None:
        df = parse_contents(contents, filename)
        if df is not None:
            s = df["SUBJ"]
            c = df["COU_NBR"]
            t = df["SECT_NBR"]
            df["COU_CMV"] = [f"{s} {c} ({t})" for s, c, t in zip(s, c, t)] 
            return df.to_dict('records')
        else:
            return [{}]
    else:
        return [{}]
    
@callback(
        Output("upload-data", "className"),
        [
            Input("upload-data", "contents"),
            Input("store-data", "data")
        ]
)
def update_color_upload(contents, data):
    if contents and data is not None:
        return "upload-success"
    else:
        return "upload"