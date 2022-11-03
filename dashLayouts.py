from dash import html, dcc, dash_table
import datetime
import plotly.express as px
import plotly.graph_objects as go
# Import module needed for curve fit
from curve_fit import fit_to_model
import numpy as np

###############################################
##          Initial Layout - Home            ##
###############################################

initial_layout = html.Div(
    children=[
    html.Header(
        id='header',
        children=[
            html.H1(id='title', children='Processos Oxidativos Avançados'),
        ]
    ),
    html.Div(
        children = [
        html.Div(
            id = 'upload-data-container',
            children=[
                html.H2('Ajuste de Curvas', id = 'upload-data-container-title'),
                html.P(children='Faça upload do seu arquivo CSV ou Excel e escolha o ajuste!', id = 'upload-data-container-description'),
                html.P('A primeira coluna do arquivo será considerada como valores de x e a segunda, como valores de y.', className = 'small-paragraph-for-info' ),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Arraste o arquivo ou ',
                        html.A('Clique para escolher')
                    ]),
                    #Multiple Uploads 
                    multiple= True
                ),
            ]
        ),

        html.Div(
            id = 'upload-img-container',
            children=[
                html.H2('Análise de Gráficos', id = 'upload-img-container-title'),
                html.P(children='Faça upload da imagem de um gráfico e colete os dados experimentais.', id ='upload-img-container-description'),
                html.P('Siga o passo a passo e exporte os dados no final.', className = 'small-paragraph-for-info' ),
                dcc.Upload(
                    id='upload-img',
                    children=html.Div([
                        'Arraste o arquivo ou ',
                        html.A('Clique para escolher')
                    ]),
                    #Multiple Uploads 
                    multiple= True
                ),
            ]
        )
        ],
    id = 'input-data-options-container'
    ),
    dcc.Store(id='user_modeling_data'),
    html.Div(id ='btn-model-options'),
    html.Div(id='output-data-uploaded'),         #div to show data analysis if user upload csv ou xlsx file
    html.Div(id='output-img-uploaded' )          #div to work with images if user upload graph image

])

###############################################
##      Curve Fit Layout - Modeling          ##
###############################################

def get_btn_model_options():
    return  html.Div(
        children=[
        html.H2("Selecione o modelo para ajuste de curva", id = "choose-model-label", className= 'btn-modeling-opt'),
        html.Button("Y(x) = ax + b", id="btn-reg_lin-model", className= 'btn-modeling-opt'),
        html.Button("E(t) = at + b(1-exp(-kt))", id="btn-siqueira-model", className= 'btn-modeling-opt'),
        html.Button("Y(x) = ax² + bx + c", id="btn-polynomial2-model", className= 'btn-modeling-opt'),
        html.Button("Y(x) = b.exp(ax)", id="btn-exponential-model", className= 'btn-modeling-opt'),
        html.Button("Y(x) = bxª", id="btn-power-model", className= 'btn-modeling-opt'),
        ], id = 'choose-model-options'
    ),

def get_data_results(df, filename, date, model):
    x_column, y_column = list(df.columns)
    df_results, df_line = fit_to_model(df, x_column= x_column, y_column= y_column, model = model)
    
    fig = px.line(df_line, x="line_x", y="line_y")
    fig.add_trace(go.Scatter(x= df[x_column], y=df[y_column], mode='markers', name='Pontos Experimentais'))
    fig.update_layout(
        title=f"Ajuste ao modelo {model}",
        xaxis_title= x_column,
        yaxis_title= y_column,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    return html.Div(children=[

        html.Div(
            id='graph-result',
            children=[
            dcc.Graph(
                id="results",
                figure=fig
            ),
        ]),

        html.Div(id = 'results-container',
            className = "data-table-container",
            children = [
                html.Div(
                    id='data-loaded', 
                    children=[
                    html.H2('Resultados'),
                    html.H3(filename),
                    html.H5(datetime.datetime.fromtimestamp(date)),
                    ]
                ),
                html.Div(
                    id='table-of-results',
                    children=[
                        dash_table.DataTable(
                            df_results.to_dict('records'),
                            [{'name': i, 'id': i} for i in df_results.columns],
                            export_format="xlsx"
                        ),
                    ]
                )
            ]
        ),

    ])

###############################################
##    Working with Images Layout - Graph     ##
###############################################

def plot_image_on_axes(contents):
    GS=100
    fig = go.Figure()
    # Add image
    img_width = 1400
    img_height = 1000
    scale_factor = 0.5

    fig.add_traces(
        px.scatter(
            x=np.repeat(np.linspace(0, img_width * scale_factor, GS), GS), y=np.tile(np.linspace(0, img_height * scale_factor, GS), GS)
        )
        .update_traces(marker_color="rgba(0,0,0,0)")
        .data
    )

    # Configure axes
    fig.update_xaxes(
        visible=False,
        range=[0, img_width * scale_factor]
    )

    fig.update_yaxes(
        visible=False,
        range=[0, img_height * scale_factor],
        # the scaleanchor attribute ensures that the aspect ratio stays constant
        scaleanchor="x"
    )

    # Add image
    fig.add_layout_image(
        dict(
            x=0,
            sizex=img_width * scale_factor,
            y=img_height * scale_factor,
            sizey=img_height * scale_factor,
            xref="x",
            yref="y",
            opacity=1.0,
            layer="below",
            sizing="stretch",
            source=contents)
    )

    # Configure other layout
    fig.update_layout(
        width=img_width * scale_factor,
        height=img_height * scale_factor,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )

    return html.Div(children=[

        dcc.Store(id='user_graph_param_data'),
        html.Div(
            id='img-on-axes-result',
            children=[
            dcc.Graph(
                id="user-img",
                figure=fig
            )
        ]),
        html.Div(
            id = 'img-axis-coordinates-input',
            className = "data-table-container",
            children = [
                html.H2('  Primeiro passo'),
                html.P('1) Na primeira linha da tabela abaixo, digite o ponto onde os eixos X e Y se cruzam. Você deve clicar na célula da tabela para digitar.', className = "small-paragraph-for-info"),
                html.P('2) Na segunda linha, digite os valores máximos do eixo X e do eixo Y.', className = "small-paragraph-for-info"),
                html.P('3) Clique onde os eixos se cruzam, na imagem do gráfico', className = "small-paragraph-for-info-bold"),
                html.P('4) Clique no valor máximo do eixo X', className = "small-paragraph-for-info-bold"),
                html.P('5) Clique no valor máximo do eixo Y', className = "small-paragraph-for-info-bold"),
                html.P('', className = "small-paragraph-for-info"),
                html.P('Quando terminar, clique no botão continuar. Certifique-se que completar os passos de 3 a 5.', className = "small-paragraph-for-info"),
                dash_table.DataTable(
                    id='user-graph-param-input',
                    columns=[{
                        'name': f'{c}',
                        'id': f'{i}',
                        #'deletable': True,
                        'renamable': True
                    } for i,c in [('x','X0 e Xmax'),('y','Y0 e Ymax')]],
                    data=[{"x":"","y":""},{"x":"","y":""}],
                    editable=True,
                    row_deletable=True
                ),
                html.Div(id = 'continue-btn-container', children=[ html.Button('Continuar', id = 'show-step-two-btn') ])
            ]
        ),
        html.Div(id = 'img-results-container', className = "data-table-container", children=[html.H3("Segundo passo")])
    ])

def step_one_concluded():
    return html.H3('Primeiro passo concluído')

def get_step_two_elements():
    return  [
                html.H2(''),
                html.H2("Segundo passo"),
                html.P("Clique nos pontos do gráfico. Você pode exportar os dados quando terminar", className = "small-paragraph-for-info"),
                dash_table.DataTable(
                    id='transform-results-data-table',
                    columns=[{
                        'name': f'{c}',
                        'id': f'{i}',
                        #'deletable': True,
                        'renamable': True
                    } for i,c in [('transf-x','x'),('transf-y','y')]],
                    data=[],
                    export_format="xlsx",
                    editable=True,
                    row_deletable=True
                )
    ]