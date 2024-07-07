import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import os
import base64

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for the tree view
sample_files = [
    {'label': 'Folder 1', 'value': 'folder1', 'children': [
        {'label': 'File 1.1', 'value': 'file1_1'},
        {'label': 'File 1.2', 'value': 'file1_2'}
    ]},
    {'label': 'Folder 2', 'value': 'folder2', 'children': [
        {'label': 'File 2.1', 'value': 'file2_1'}
    ]}
]

# Layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4("File Explorer"),
            dcc.TreeSelect(
                id='file-tree',
                value=[],
                options=sample_files,
                multi=True,
                style={'width': '100%'}
            ),
            html.Br(),
            dbc.Button("Add File", id="add-file-button", color="primary"),
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=True
            )
        ], width=3, style={'borderRight': '1px solid #ddd'}),
        dbc.Col([
            html.H4("Chat"),
            dcc.Textarea(
                id='chat-log',
                style={'width': '100%', 'height': '400px'},
                readOnly=True
            ),
            dcc.Input(id='user-input', type='text', style={'width': '85%'}),
            dbc.Button("Send", id='send-button', color="primary", style={'width': '10%'})
        ], width=6),
        dbc.Col([
            html.H4("Right Panel")
            # Add any additional components for the right panel here
        ], width=3, style={'borderLeft': '1px solid #ddd'})
    ])
], fluid=True)

# Callbacks to handle interactions
@app.callback(
    Output('chat-log', 'value'),
    Input('send-button', 'n_clicks'),
    State('user-input', 'value'),
    State('chat-log', 'value')
)
def update_chat_log(n_clicks, user_input, chat_log):
    if n_clicks is None or user_input is None:
        raise dash.exceptions.PreventUpdate
    return chat_log + '\n' + user_input

@app.callback(
    Output('file-tree', 'options'),
    Input('upload-data', 'filename'),
    Input('upload-data', 'contents'),
    State('file-tree', 'options')
)
def update_file_tree(filenames, filecontents, current_tree):
    if filenames is None or filecontents is None:
        raise dash.exceptions.PreventUpdate

    new_files = []
    for name, content in zip(filenames, filecontents):
        data = content.encode("utf8").split(b";base64,")[1]
        with open(os.path.join("uploads", name), "wb") as fp:
            fp.write(base64.decodebytes(data))
        new_files.append({'label': name, 'value': name})

    current_tree.append({'label': 'New Folder', 'value': 'new_folder', 'children': new_files})
    return current_tree

# Run the app
if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run_server(debug=True)
