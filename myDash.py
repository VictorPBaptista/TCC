import base64
import io
import gunicorn
import pandas as pd

import dashLayouts as dl

from dash import Dash, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


app = Dash(__name__,suppress_callback_exceptions=True)

server = app.server

app.layout = dl.initial_layout

###############################################
##    Function to parse Input Contents       ##
###############################################

#1) Function to parse content from uploaded xlsx or csv file to pandas dataframe
def parse_data_contents(contents, filename, date):
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
            df = pd.read_excel(
                io.BytesIO(decoded),
                decimal=','
                )
    except Exception as e:
        print(e)
        return dl.html.Div([
            'There was an error processing this file.'
        ])

    return df

###############################################
##              CallBack Section             ##
###############################################

#0.0) Remove Initial Layout from Screen after user upload any data
@app.callback(Output("input-data-options-container", "children"),
              Input("btn-model-options", "children"),
              Input('output-img-uploaded', 'children'),
              prevent_initial_call =True)
def clear_input_container(modeling_options_children, img_children):
    empty_children = []
    return empty_children

#     ----------------------------------
#1.0) ------> Modeling CallBacks <------
#     ----------------------------------

#1.1) Upload data and parse content into json object
@app.callback(Output('user_modeling_data', 'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              prevent_initial_call=True)
def get_user_data_input(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        dfs = [
            parse_data_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        df, f, d = dfs[0], list_of_names[0], list_of_dates[0]
        return (df.to_json(date_format='iso', orient='split'), f, d)

#1.2) Show buttons for user to choose modeling options
@app.callback(Output("btn-model-options", "children"),
              Input("user_modeling_data", "data"),
              prevent_initial_call =True)
def update_btn_model_options(data):
    children = dl.get_btn_model_options()
    return children

#1.3) Show curve fit Results and change model according to user choice
@app.callback(Output("output-data-uploaded", "children"),
              Input("btn-siqueira-model","n_clicks"),
              Input("btn-reg_lin-model", "n_clicks"),
              Input("btn-polynomial2-model","n_clicks"),
              Input("btn-exponential-model","n_clicks"),
              Input("btn-power-model","n_clicks"),
              State("user_modeling_data","data"),
              prevent_initial_call =True)
def update_output(btn1, btn2, btn3, btn4, btn5, data):
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    if button_id == 'btn-reg_lin-model':
        data_frame, f, d = data 
        df = pd.read_json(data_frame, orient='split')
        children = dl.get_data_results(df, f, d, model = 'Y(x) = ax + b')
    if button_id == 'btn-polynomial2-model':
        data_frame, f, d = data 
        df = pd.read_json(data_frame, orient='split')
        children = dl.get_data_results(df, f, d, model = 'Y(x) = ax² + bx + c')
    if button_id == 'btn-siqueira-model':
        data_frame, f, d = data 
        df = pd.read_json(data_frame, orient='split')
        children = dl.get_data_results(df, f, d, model = 'E(t) = at +b(1-exp(-kt))')
    if button_id == 'btn-exponential-model':
        data_frame, f, d = data 
        df = pd.read_json(data_frame, orient='split')
        children = dl.get_data_results(df, f, d, model = 'Y(x) = b.exp(ax)')
    if button_id == 'btn-power-model':
        data_frame, f, d = data 
        df = pd.read_json(data_frame, orient='split')
        children = dl.get_data_results(df, f, d, model = 'Y(x) = bxª')
    return children

#     --------------------------------------------
#2.0) ------> Working with Image CallBacks <------
#     --------------------------------------------

#   SETP 1 - USER INPUT: user must type X0, Xmax and Y0, Ymax
#2.1) Plot image on figure object
@app.callback(Output('output-img-uploaded', 'children'),
              Input('upload-img', 'contents'),
              prevent_initial_call = True)
def update_image_output(list_of_contents):
    if list_of_contents is not None:
        children = [
            dl.plot_image_on_axes(c) for c in list_of_contents
        ]
        return children

#2.1.1) Delete Step 1 instructions
@app.callback(Output('step1', 'children'),
              Input('show-step-two-btn', 'n_clicks'),
              prevent_initial_call = True)
def delete_step_one(n_clicks):
    empty_children = []
    return empty_children

#2.1.2) Step1 - Show completed status
@app.callback(Output('step1-concluded-status', 'children'),
              Input('show-step-two-btn', 'n_clicks'),
              prevent_initial_call = True)
def show_step1_status_completed(n_clicks):
    return dl.step_one_concluded()

#2.1.3) Show Step 2 instructions
@app.callback(Output('step2', 'children'),
              Input('show-step-two-btn', 'n_clicks'),
              prevent_initial_call = True)
def show_step_two(n_clicks):
    return dl.get_step_two()

#2.1.4) Step2 - Remove previous Div with user tip
@app.callback(Output('step2-gui-user-tip', 'children'),
              Input('show-step-two-btn', 'n_clicks'),
              prevent_initial_call = True)
def remove_previous_step2_tip(n_clicks):
    return []


#   SETP 2 - USER INPUT: Click event for getting data from image
#2.2) Step 2 - Setting Callback for click event: use this to get Img data
@app.callback(Output('user-graph-param-input', 'data'),
              Input('user-img', "clickData"),
              State('user-graph-param-input', 'data'),
              State('user-graph-param-input', 'columns'),
              prevent_initial_call = True)
def step_one_click_event(clickData, rows, columns):
    if not clickData:
        raise PreventUpdate
    rows.append({c['id']: r for c,r in zip(columns,[ round(clickData["points"][0]['x'], 3), round(clickData["points"][0]['y'], 3) ])})
    return rows

#2.2.1) Save user inputs into json object
@app.callback(Output('user_graph_param_data', 'data'),
              Input("show-step-three-btn", "n_clicks"),
              State('user-graph-param-input', 'data'),
              prevent_initial_call = True)
def get_user_graph_input_data(n_clicks, rows):
    temp_d = {'x':[],'y':[]}
    
    counter = 0
    for row in rows:
        counter+=1
        temp_d['x'].append(row['x'])
        temp_d['y'].append(row['y'])

    return pd.DataFrame(temp_d).to_json(date_format='iso', orient='split')

#2.2.2) Delete Step 2 instructions
@app.callback(Output('step2-elements-container', 'children'),
              Input('show-step-three-btn', 'n_clicks'),
              prevent_initial_call = True)
def delete_step_two(n_clicks):
    return dl.step_two_concluded()

#2.2.3) Show Step 3 instructions
@app.callback(Output('img-results-container', 'children'),
              Input('show-step-three-btn', 'n_clicks'),
              prevent_initial_call = True)
def show_step_three(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    else:
        return dl.get_step_three()

#2.2.4) Delete Data Table container
@app.callback(Output('inputs-data-table', 'children'),
              Input('show-step-three-btn', 'n_clicks'),
              prevent_initial_call = True)
def delete_step_two(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    else:
        return []


#   SETP 3 - CALCULATE EXPERIMENTAL DATA: calculate experimental data by user click evente and export results
#2.3) Transform click event coordinates data
@app.callback(Output('transform-results-data-table', 'data'),
              Input("user-img", "clickData"),
              State('transform-results-data-table', 'data'),
              State('transform-results-data-table', 'columns'),
              State('user_graph_param_data', 'data'),
              prevent_initial_call = True)
def transform_data(clickData, rows, columns, step_one_data):
    #Append new row in table with user click event
    if not clickData:
        raise PreventUpdate
    
    df = pd.read_json(step_one_data, orient='split')
    x_column, y_column = list(df.columns)
    
    x_min_distance = df[x_column][2] - df[x_column][0]
    y_min_distance = df[y_column][2] - df[y_column][0]
    
    x_max_distance = df[x_column][3] - x_min_distance
    y_max_distance = df[y_column][4] - y_min_distance
    
    x_divide_factor = x_max_distance/df[x_column][1]
    y_divide_factor = y_max_distance/df[y_column][1]
    
    rows.append({
        c['id']: r for c,r in zip(
            columns,
            [
                round((clickData["points"][0]['x']-x_min_distance)/x_divide_factor, 3), 
                round((clickData["points"][0]['y']-y_min_distance)/y_divide_factor, 3)
            ]
        )
    })
    return rows

if __name__ == '__main__':
    app.run_server(debug=True)