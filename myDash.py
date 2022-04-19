import base64
import datetime
import io
import gunicorn

from curve_fit import fit_to_model
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

app = Dash(__name__)

server = app.server

app.layout = html.Div(
    children=[
    html.Header(
        id='header',
        children=[
            html.H1(id='title', children='Processos Oxidativos Avançados'),
        ]
    ),
    html.Div(
        id = 'upload-container',
        children=[
            html.P(children='Por favor, faça upload dos dados. Use arquivos csv ou xlsx' ),
            dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Arraste o arquivo ou ',
                html.A('Clique para escolher')
        ]),
        # Allow multiple files to be uploaded
        multiple=True
    )
    ]),
    dcc.Store(id='user_data'),
    html.Div(id='output-data-upload'),

    html.Div(id = 'download-container',
        children = [
            html.Button("Download CSV", id="btn_csv", disabled=True),
            dcc.Download(id="download-dataframe-csv"),
        ]
    ),    

])


def get_results(df, filename, date):
    column1, column2 = list(df.columns)
    df_results, df_line = fit_to_model(df, column1= column1, column2= column2)
    
    fig = px.line(df_line, x="line_x", y="line_y")
    fig.add_trace(go.Scatter(x= df[column1], y=df[column2], mode='markers', name='Pontos Experimentais'))
    fig.update_layout(
        title="Ajuste ao modelo E(t) = at +b(1-exp(-kt))",
        xaxis_title="Unidade de Tempo",
        yaxis_title="Conversão (%)",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
        
    return html.Div(children=[
        html.Div(
            id='data-loaded', 
            children=[
            html.H4('Dados recebidos'),
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),
            dash_table.DataTable(
                df.to_dict('records'),
                [{'name': i, 'id': i} for i in df.columns]
            ),
        ]),

        html.Div(
            id='graph-result',
            children=[
            dcc.Graph(
                id="results",
                figure=fig
            ),
        ]),

        html.Div(
            id='table-of-results',
            children=[
            dash_table.DataTable(
                df_results.to_dict('records'),
                [{'name': i, 'id': i} for i in df_results.columns]
            ),
        ]),

    ])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')),
                sep=';',
                decimal=','
                )
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


@app.callback(Output('user_data', 'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              prevent_initial_call=True)
def get_user_data_input(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        dfs = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        df, f, d = dfs[0], list_of_names[0], list_of_dates[0]
        return (df.to_json(date_format='iso', orient='split'), f, d)


@app.callback(Output("output-data-upload", "children"),Input("user_data", "data"), prevent_initial_call =True)
def update_output(data):
    data_frame, f, d = data 
    df = pd.read_json(data_frame, orient='split')
    children = get_results(df, f, d)
    return children

@app.callback(Output("btn_csv", "disabled"),Input("output-data-upload", "children"), prevent_initial_call =True)
def update_output(children):
    return False

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State("user_data","data"),
    prevent_initial_call=True)
def download_results(n_clicks, data):
    data_frame, f, d = data 
    df = pd.read_json(data_frame, orient='split')
    column1, column2 = list(df.columns)
    df_results = fit_to_model(df, column1= column1, column2= column2)[0]
    return dcc.send_data_frame(df_results.to_csv, "resultadosPOA.csv", sep=";", decimal=",")


if __name__ == '__main__':
    app.run_server(debug=True)