import plotly
plotly.tools.set_credentials_file(username='zandermoore1994', api_key='dund3fgcUIRA82LX6JxJ')
import jupyter_dashboards
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import scipy as sp
import plotly as py
import pandas
plotly.offline.init_notebook_mode()
import plotly.offline as offline

def plot_graphs(data_new):


    total=np.sum(data_new[parties].iloc[0])
    base_chart = {
        "values": [40, 10, 10, 10, 10, 10, 10],"domain": {"x": [0, .48]},"marker": {"colors": ['rgb(255, 255, 255)','rgb(255, 255, 255)','rgb(255, 255, 255)','rgb(255, 255, 255)','rgb(255, 255, 255)','rgb(255, 255, 255)','rgb(255, 255, 255)'],"line": {"width": 0}},"name": "Predictor","hole": .4,"type": "pie","direction": "clockwise", "rotation": 180,"showlegend": False,"hoverinfo": "none","textinfo": "none","textposition": "outside"}
    meter_chart = {"values": [total, data_new["CDU"][0], data_new["SPD"][0], data_new["Gruene"][0],data_new["AfD"][0],data_new["Linke"][0]],
        "labels": [" ", "CDU/CSU", "SPD", "Green", "AFD", "Die Linke"],
        "marker": {'colors': ['rgb(255, 255, 255)','rgb(0,0,0)','rgb(165,0,38)','rgb(154,205,50)','rgb(0,204,255)','rgb(153,102,255)']},
        "domain": {"x": [0, 0.48]},"name": "% Representation","hole": .3,"type": "pie",  "direction": "clockwise", "rotation": 90,
        "showlegend": False,"textinfo": "label", "textposition": "outside","hoverinfo": "none"}

    fig_1 = {"data": [base_chart, meter_chart],}
    #offline.plot(fig_1 , output_type='file', filename='SeatChart',image='png')


    timeline= data_new['Datum'][::-1]
    CDU_data=data_new['CDU'][::-1]
    SPD_data=data_new['SPD'][::-1]
    Green_data=data_new['Gruene'][::-1]
    Linke_data=data_new['Linke'][::-1]
    AFD_data=data_new['AfD'][::-1]



    CDU = go.Scatter(
    x=timeline,
    y=CDU_data,
    name = "CDU",
    line = dict(color = 'rgb(0,0,0)'),
    opacity = 0.8)

    SPD = go.Scatter(
        x=timeline,
        y=SPD_data,
        name = "SPD",
        line = dict(color = 'rgb(165,0,38)'),
        opacity = 0.8)

    Gruene = go.Scatter(
        x=timeline,
        y=Green_data,
        name = "Gruene",
        line = dict(color = 'rgb(154,205,50)'),
        opacity = 0.8)

    Linke = go.Scatter(
        x=timeline,
        y=Linke_data,
        name = "Linke",
        line = dict(color = 'rgb(0,204,255)'),
        opacity = 0.8)

    AFD = go.Scatter(
        x=timeline,
        y=AFD_data,
        name = "AfD",
        line = dict(color = 'rgb(153,102,255)'),
        opacity = 0.8)

    data2 = [CDU,SPD,Gruene,Linke,AFD]

    layout2 = dict(
        title='Evolution of Second Vote Prediction',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(),
            type='timeline'
        )
    )

    fig_2 = dict(data=data2, layout=layout2)

    offline.plot(fig_1 , output_type='file', filename='SeatChart',image='png')
    offline.plot(fig_2 , output_type='file', filename='TimeEvolution',image='png')