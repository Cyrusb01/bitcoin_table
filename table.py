# import plotly 
# import bt 

import requests
# import pandas as pd
# from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import plotly.graph_objects as go
from PIL import Image
import slack

slack_token = "xoxb-2494974236230-2494977536086-Ag9YR6pDVxASp0U9ol8rkY1S"
client = slack.WebClient(token = "xoxb-2494974236230-2494977536086-Ag9YR6pDVxASp0U9ol8rkY1S")
# client.chat_postMessage(channel="#bitcoin-table", text = "Hello")

img = Image.open("Background.jpg")

# data = bt.get("btc-usd", start = "2021-01-01")
labels = ["", "<b>Year<b>", "<b>Start Price<b>", "<b>End Price<b>", "<b>% Change<b>", ""]
years = [ "2010", "2011", "2012", "2013", "2014","2015", "2016", "2017", "2018", "2019", "2020", "2021 YTD"]
start_price = [ "0.003", "0.30", "4.72", "13.5", "758", "320", "430", "968", "13,860", "3,689", "7,184", "28,775"]
end_price = [ "0.30", "4.72", "13.5", "758", "320", "430", "968", "13,860", "3,689", "7,184", "28,775"]
percent_change = ["+9,000%", "+1,473%", "+186%", "+5,507%", "-58%", "+35%", "+125%", "+1,331%", "-73%", "+95%", "+301%"]
empty_row = []

start_time = datetime(2021, 1, 1, 0, 0)
now = datetime.now().replace(hour=0, minute=0)


baseId = "bitcoin"
quoteId = "tether"

while True:
    url = (
            "https://api.coincap.io/v2/candles?exchange=binance&interval=d1"
            f"&baseId={baseId}&quoteId={quoteId}"
            f"&start={datetime.timestamp(start_time) * 1000}"
            f"&end={datetime.timestamp(now) * 1000}"
    )

    response = requests.get(url)
    if response.status_code > 300:
        print("Data Exception, trying again")
        continue
        raise Exception("Invalid response code returned: " + str(response.status_code))
        
    res = response.json()
    if not res["data"]:
        raise Exception("No response body returned for: " + symbol)
    break




unix_time = int(res["data"][-1]['period'])/1000
# print(unix_time)
date_time = datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d')
#Gets the last days of data and formats the percent properly
latest_price = float(res["data"][-1]['close'])
percent_change_latest = ((latest_price/float(start_price[-1].replace(",", '')))- 1) *100
percent_change_latest = round(percent_change_latest)

if percent_change_latest > 0:
    percent_change_latest = "+" + str(percent_change_latest)
    percent_change_latest += "%"
elif percent_change_latest < 0:
    percent_change_latest = "-" + str(percent_change_latest)
    percent_change_latest += "%"

percent_change.append(percent_change_latest)
latest_price = "{:,}".format(round(latest_price))
end_price.append(latest_price)



onramp_col = "#00EEAD"
red = "#FF600E"
#Coloring
text_color = []
text_color.append(["white"])
text_color.append(["white"])
text_color.append(["white"])
text_color.append(["white"])
text_color.append([onramp_col, onramp_col, onramp_col, onramp_col, red, onramp_col, onramp_col, onramp_col, red, onramp_col, onramp_col])
last_price_check = latest_price.replace(",", '')
last_price_check = last_price_check.replace("%", '')
if float(last_price_check) > 0:
    text_color.append([onramp_col])
else:
    text_color.append([red])
# text_color.append(["green"]*12)
# text_color.append(["wte"]*12)

fig = go.Figure(
    data=[
        go.Table(
            columnwidth = [40, 80,80, 80, 80, 40],
            header=dict(
                values= labels,
                line_color="rgba(0, 0, 0, 0)",
                fill_color=["rgba(0, 0, 0, 0)", "#424949", "#424949", "#424949", "#424949", "rgba(0, 0, 0, 0)"],
                align="left",
                font=dict(color="white", size=22),
                height = 32
            ),
            cells=dict(
                values=[empty_row, years, start_price, end_price, percent_change, empty_row],
                line_color="rgba(0, 0, 0, 0)",
                font=dict(color= text_color, size=19),
                align = "left",
                height=40,
                fill_color = "rgba(0, 0, 0, 0)",
            ),
        )
    ]
)
fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",  # Transparent
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
        },
        height = 1100,
        # font = dict(family = 'roboto')
)
fig.add_layout_image(
        dict(
            source=img,
            xref="paper",
            yref="paper",
            x=1,
            y=0.2,
            sizex=1,
            sizey= 1,
            xanchor="right",
            yanchor="bottom",
            layer = "below"
        )
)
fig.update_layout(margin=dict(l=1, r=1, t=300, b=1))


#Adds the Bitcoin Returns text at the top
fig.add_annotation(
            x=.096,
            y=1.07,
            xref="paper",
            yref="paper",
            text="Bitcoin",
            showarrow=False,
            font=dict(
            size=30,
            color="#f2a900"
            ))

fig.add_annotation(
            x=.214,
            y=1.07,
            xref="paper",
            yref="paper",
            text="Returns: 2010-2021",
            showarrow=False,
            font=dict(
            size=30,
            color="white"
            ))

fig.add_annotation(
            x=.106,
            y= .34,
            xref="paper",
            yref="paper",
            text= '------------------------------------------------------------------------------------------------------------------------------------------------------------------------------',
            showarrow=False,
            font=dict(
            size=10,
            color="#424949"
            ))

fig.add_annotation(
            x=.106,
            y= .30,
            xref="paper",
            yref="paper",
            text= '<i>' + "Data Source: CoinCap API, Binance as of " + date_time + '</i>',
            showarrow=False,
            font=dict(
            size=10,
            color="white"
            ))

fig.add_annotation(
        x=.095,
        y=.377,
        xref="paper",
        yref="paper",
        showarrow=True,
        font=dict(
            family="Courier New, monospace",
            size=16,
            color="#ffffff"
            ),
        align="center",
        arrowhead=2,
        arrowsize=2,
        arrowwidth=2,
        arrowcolor="#f2a900",
        ax=-50,
        ay=0,
        opacity=0.8
        )
# fig.update_layout(xaxi)
# fig.show()

fig.write_image("bitcoin_returns.png", height = 1100, width = 1000)

result = client.files_upload(
    channels="bitcoin-table",
    initial_comment="Updated Bitcoin Table :smile:",
    file="bitcoin_returns.png",
)
