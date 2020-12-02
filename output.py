import os
import matplotlib.pyplot as plt
import squarify
import pandas as pd
import plotly.express as px
from bokeh.models import Circle, MultiLine, ColumnDataSource
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

file_path = os.getcwd() + '/champion.json'
df = pd.read_json(file_path, orient='index')
perCharacter = {}
for character in df['stats'].keys():
    statsPerLevel = {}
    statKeys = list(df['stats'][character].keys())
    statValues = list(df['stats'][character].values())
    for statIndex in range(len(statKeys)):
        stat = statKeys[statIndex]
        perlevelIndex = stat.find('perlevel')
        if perlevelIndex != -1:
            perLevelKey = stat[:perlevelIndex]  # find the per level key
            perLevelVal = statValues[statIndex]
            baseValue = statValues[statKeys.index(perLevelKey)]
            levels = {}
            for level in range(1, 19):
                if (level == 1):
                    levels[level] = baseValue
                else:
                    levels[level] = ((level-1) * perLevelVal) + baseValue
            statsPerLevel[perLevelKey] = levels
    perCharacter[character] = statsPerLevel

characterPlaceholder = []
statPlaceholder = []
levelPlaceholder = []
valuePlaceholder = []
charKeys = list(perCharacter.keys())
charVals = list(perCharacter.values())

for c in range(len(charKeys)):
    for k in charVals[c].keys():
        for level in range(1, 19):
            statPlaceholder.append(k)
            levelPlaceholder.append(level)
            characterPlaceholder.append(charKeys[c])
    statsPerLevel = list(charVals[c].values())
    for l in statsPerLevel:
        for v in l.values():
            valuePlaceholder.append(v)

# initialize to hp


def filterByStat(statName, charName):
    shownCharacter = []
    shownLevel = []
    shownVal = []
    shownStat = []
    for c in range(len(statPlaceholder)):
        if (charName == '' or characterPlaceholder[c] == charName):
            if (statPlaceholder[c] == statName):
                shownStat.append(statPlaceholder[c])
                shownCharacter.append(characterPlaceholder[c])
                shownLevel.append(levelPlaceholder[c])
                shownVal.append(valuePlaceholder[c])
    return {'shownCharacter': shownCharacter, 'shownLevel': shownLevel, 'shownVal': shownVal, 'shownStat': shownStat}


init = filterByStat('hp', '')
newDf1 = pd.DataFrame(
    dict(
        character=init['shownCharacter'],
        stat=init['shownStat'],
        levels=init['shownLevel'],
        values=init['shownVal'],
    )
)

fig1 = px.line(newDf1, x='levels', y='values', color='character',
               title='Champion Base Stats From League of Legends', hover_data=["stat"])
fig1.update_layout(
    xaxis_title="Level",
    yaxis_title="Stat Value",
)

# dropdown buttons to filter for stats
dropdownButtons = []
for key in list(df['stats']['Aatrox'].keys()):
    if ('perlevel' not in key):
        xVal = []
        yVal = []
        for i in df['stats'].keys():
            init = filterByStat(key, i)
            xVal.append(init['shownLevel'])
            yVal.append(init['shownVal'])
        if (len(yVal[0]) > 1):
            dropdownButtons.append(dict(label=key,
                                        method="update",
                                        args=[
                                            {'x': xVal, 'y': yVal,
                                                'values': yVal, 'names': xVal},
                                            {"title": 'Level vs. ' +
                                                key, "yAxis": key}
                                        ]))

fig1.update_layout(updatemenus=[
    dict(
        type="buttons",
        buttons=list([
            dict(
                args=["mode", 'lines'],
                label="Show Lines Only",
                method="restyle"
            ),
            dict(
                args=["mode", 'markers'],
                label="Show Scatter Only",
                method="restyle"
            ),
            dict(
                args=["mode", 'lines+markers'],
                label="Show Scatter + Lines",
                method="restyle"
            ),
        ]),
    ),
    dict(
        buttons=dropdownButtons,
        pad={"r": 35, "t": 140},
    ),
],
)

characters = []
partypes = []
difficulties = []

for i in range(len(df['partype'].keys())):
    keys = df['partype'].keys()
    values = df['partype'][i]
    difficulty = df['info'][i]['difficulty']
    characters.append(keys[i])
    partypes.append(values)
    difficulties.append(difficulty)

newDf = pd.DataFrame(
    dict(
        characters=characters,
        partypes=partypes,
        difficulties=difficulties,
    )
)
fig2 = px.sunburst(newDf, path=['partypes', 'difficulties', 'characters'],
                   values='difficulties', title='Difficulties by Partypes')

fig2.update_layout(updatemenus=[
    dict(
        type="buttons",
        direction="left",
        buttons=list([
            dict(
                args=["type", 'sunburst'],
                label="Radial",
                method="restyle"
            ),
            dict(
                args=["type", 'treemap'],
                label="Treemap",
                method="restyle"
            ),
        ]),
    ),
],
)

characters = []
initialVals = []
initialKeys = []
for character in df['stats'].keys():
    statKeys = list(df['stats'][character].keys())
    statValues = list(df['stats'][character].values())
    for statIndex in range(len(statKeys)):
        stat = statKeys[statIndex]
        perlevelIndex = stat.find('perlevel')
        if perlevelIndex == -1:
            characters.append(character)
            initialKeys.append(statKeys[statIndex])
            initialVals.append(statValues[statIndex])
newDf = pd.DataFrame(
    dict(
        characters=characters,
        initialVals=initialVals,
        statKeys=initialKeys,
    )
)
fig3 = px.bar(newDf, x='characters', y='initialVals',
              color='statKeys', title='Initial Stats Per Character')
fig3.update_layout(
    xaxis_title="Characters",
    yaxis_title="Initial Stat Values",
)
with open('p_graph.html', 'a') as f:
    f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write(fig3.to_html(full_html=False, include_plotlyjs='cdn'))
