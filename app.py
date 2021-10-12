import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from PIL import Image
import slack_sdk

#
########################## SLACK TOKEN ######################################################################

slack_token = "ENTER SLACK TOKEN HERE"  # Onramp

client = slack_sdk.WebClient(token=slack_token)  # sets up our connection
# client.chat_postMessage(channel="#bitcoin-table", text = "Hello")  #Testing sending a message


labels = [
    "",
    "<b>Year<b>",
    "<b>Start Price<b>",
    "<b>End Price<b>",
    "<b>% Change<b>",
    "",
]

######## Pre Set Bitcoin Data
"""
This data is not really used, we use the data from the csv file, however these lists are used for some length values further down
"""
years_b = [
    "2010",
    "2011",
    "2012",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018",
    "2019",
    "2020",
    "2021 YTD",
]
start_price_b = [
    "0.003",
    "0.30",
    "4.72",
    "13.5",
    "758",
    "320",
    "430",
    "968",
    "13,860",
    "3,689",
    "7,184",
    "28,775",
]
end_price_b = [
    "0.30",
    "4.72",
    "13.5",
    "758",
    "320",
    "430",
    "968",
    "13,860",
    "3,689",
    "7,184",
    "28,775",
]
percent_change_b = [
    "+9,000%",
    "+1,473%",
    "+186%",
    "+5,507%",
    "-58%",
    "+35%",
    "+125%",
    "+1,331%",
    "-73%",
    "+95%",
    "+301%",
]
empty_row = []


##################################################### READ IN HISTORIC DATA FROM CSV ########################################################
"""
If we want different tables for more assets, just need to fill in the csv file with historical data,
the code for seperate assets is already done, change choice to asset of choice
"""
choice = "bitcoin"

years = []
start_price = []
end_price = []
percent_change = []

df_historic = pd.read_csv("historic_data.csv")
df_historic = df_historic.set_index("Assets")

dict_historic = df_historic.to_dict(orient="index")

# Format the data into lists with proper formatting
for year in years_b:
    if not pd.isna(dict_historic[choice][year + "-s"]):
        start_price.append(dict_historic[choice][year + "-s"])
        years.append(year)
    if not pd.isna(dict_historic[choice][year + "-e"]):
        end_price.append(dict_historic[choice][year + "-e"])

# calculating the percent change
for i in range(len(end_price)):
    # Some numbers have commas so this makes them into foats
    try:
        num1 = float(start_price[i].replace(",", ""))
    except:
        num1 = start_price[i]
    try:
        num2 = float(end_price[i].replace(",", ""))
    except:
        num2 = end_price[i]

    # percent_change.append(
    change = round((((num2 - num1) / num1) * 100))
    # print(change)
    if change > 0:
        change = "+" + "{:,}".format(change)
        change += "%"
    elif change < 0:
        change = "{:,}".format(change)
        change += "%"
    percent_change.append(change)


crypto_color = dict_historic[choice]["color"]



################################################ GETTING LAST YEARS DATA #####################################################################
"""
This portion uses coincap API to get the data for 2021, we only fetch this data because 
all the historic data should already be in the csv, this lets us only make one API
"""
start_time = datetime(2021, 1, 1, 0, 0)
end_time = datetime(2022, 1, 1, 0, 0)
# now = datetime.now().replace(hour=0, minute=0)


baseId = choice
quoteId = "tether"


# Use while loop because sometimes API throws error, but if you try it again it will eventually send the data
while True:

    url = (
        "https://api.coincap.io/v2/candles?exchange=binance&interval=d1"
        f"&baseId={baseId}&quoteId={quoteId}"
        f"&start={datetime.timestamp(start_time) * 1000}"
        f"&end={datetime.timestamp(end_time) * 1000}"
    )

    response = requests.get(url)
    if response.status_code > 300:
        print("Data Exception, trying again")
        continue
        raise Exception("Invalid response code returned: " + str(response.status_code))

    res = response.json()
    if not res["data"]:
        raise Exception("No response body returned for: " + baseId)
    break


# gets the data from the API and puts into dataframe
df = pd.DataFrame(res["data"])
df["period"] = pd.to_datetime(df["period"], unit="ms", origin="unix")

#Use this later for the sourcing
dt_object = datetime.now().replace(microsecond=0)

# Gets the last days of data and formats the percent properly
latest_price = float(res["data"][-1]["close"])
percent_change_latest = (
    (latest_price / float(start_price[-1].replace(",", ""))) - 1
) * 100
percent_change_latest = round(percent_change_latest)


# format the string properly to have % symbol and negative sign
if percent_change_latest > 0:
    percent_change_latest = "+" + str(percent_change_latest)
    percent_change_latest += "%"
elif percent_change_latest < 0:
    percent_change_latest = "-" + str(percent_change_latest)
    percent_change_latest += "%"

percent_change.append(percent_change_latest)
latest_price = "{:,}".format(round(latest_price))
end_price.append(latest_price)

start_price = ["$" + str(x) for x in start_price]
end_price = ["$" + str(x) for x in end_price]

################################################################# GRAPHING ###########################################################################
"""
The graphing is done using plotly. This creates a plotly table. 
First we do the coloring and styling, quite a process for custom text coloring
Then the actual figure is created 
Lastly the annotations are set
"""
onramp_col = "#00EEAD"
red = "#FF600E"
# Coloring
text_color = []
text_color.append(["white"])
text_color.append(["white"])
text_color.append(["white"])
text_color.append(["white"])
text_color.append(
    [
        onramp_col,
        onramp_col,
        onramp_col,
        onramp_col,
        red,
        onramp_col,
        onramp_col,
        onramp_col,
        red,
        onramp_col,
        onramp_col,
    ]
)
last_price_check = latest_price.replace(",", "")
last_price_check = last_price_check.replace("%", "")
if float(last_price_check) > 0:
    text_color.append([onramp_col])
else:
    text_color.append([red])


# creating the figure
fig = go.Figure(
    data=[
        go.Table(
            columnwidth=[40, 80, 80, 80, 80, 40],
            header=dict(
                values=labels,
                line_color="rgba(0, 0, 0, 0)",
                fill_color=[
                    "rgba(0, 0, 0, 0)",
                    "#424949",
                    "#424949",
                    "#424949",
                    "#424949",
                    "rgba(0, 0, 0, 0)",
                ],
                align="left",
                font=dict(color="white", size=22),
                height=32,
            ),
            cells=dict(
                values=[
                    empty_row,
                    years,
                    start_price,
                    end_price,
                    percent_change,
                    empty_row,
                ],
                line_color="rgba(0, 0, 0, 0)",
                font=dict(color=text_color, size=19),
                align="left",
                height=40,
                fill_color="rgba(0, 0, 0, 0)",
            ),
        )
    ]
)


fig.update_layout(
    {
        "plot_bgcolor": "rgba(0, 0, 0, 0)",  # Transparent
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
    },
    height=1100,
    # font = dict(family = 'roboto')
)

# Sets the background image
img = Image.open("Background.jpg")
fig.add_layout_image(
    dict(
        source=img,
        xref="paper",
        yref="paper",
        x=1,
        y=0.2,
        sizex=1,
        sizey=1,
        xanchor="right",
        yanchor="bottom",
        layer="below",
    )
)

fig.update_layout(margin=dict(l=1, r=1, t=300, b=1))


# Adds the Bitcoin Returns text at the top
fig.add_annotation(
    x=0.096,
    y=1.07,
    xref="paper",
    yref="paper",
    text=choice.capitalize(),
    showarrow=False,
    font=dict(size=30, color=crypto_color),
)

# Adds Returns 2010-2021 at the top
# since text positioning is absolute longer words need to be accounted for, this was designed initially just for bitcoin
shift = len(choice) - len("Bitcoin")
fig.add_annotation(
    x=0.214 + shift * 0.035,
    y=1.07,
    xref="paper",
    yref="paper",
    text="Returns: 2010-2021",
    showarrow=False,
    font=dict(size=30, color="white"),
)

# adds dashed line
fig.add_annotation(
    x=0.106,
    y=0.34,
    xref="paper",
    yref="paper",
    text="------------------------------------------------------------------------------------------------------------------------------------------------------------------------------",
    showarrow=False,
    font=dict(size=10, color="#424949"),
)
# Adds sourcing
fig.add_annotation(
    x=0.106,
    y=0.30,
    xref="paper",
    yref="paper",
    text="<i>" + "Data Source: CoinCap API, Binance as of " + str(dt_object) + " CDT"
    "</i>",
    showarrow=False,
    font=dict(size=12, color="white"),
)

# adds arrow
arrow_shift = len(years_b) - len(years)
fig.add_annotation(
    x=0.095,
    y=0.377 + arrow_shift * 0.05,
    xref="paper",
    yref="paper",
    showarrow=True,
    font=dict(family="Courier New, monospace", size=16, color="#ffffff"),
    align="center",
    arrowhead=2,
    arrowsize=2,
    arrowwidth=2,
    arrowcolor=crypto_color,
    ax=-50,
    ay=0,
    opacity=0.8,
)


# makes the figure into a png
fig.write_image("bitcoin_returns.png", height=1100, width=1000)


# Sends the file into the slack channel
result = client.files_upload(
    channels="onramp-social-content",
    initial_comment="Updated " + choice.capitalize() + "Table (TESTING) :smile:",
    file="bitcoin_returns.png",
)
