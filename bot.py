import discord
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi
from discord.ext import commands
from requests.models import HTTPError
import io, toml


config = toml.load('./config.toml')


## CONSTANTS
TOKEN = config["discord"]["token"]
ALPACA_KEY_ID = config["alpaca"]["id"]
ALPACA_KEY_SECRET = config["alpaca"]["secret"]

plt.rcParams.update({'xtick.labelsize' : 'small',
                     'ytick.labelsize' : 'small',
                     'figure.figsize' : [16,9]})

api = tradeapi.REST(ALPACA_KEY_ID, ALPACA_KEY_SECRET, base_url='https://paper-api.alpaca.markets', api_version='v2') # or use ENV Vars shown below
account = api.get_account()
api.list_positions()

bot = commands.Bot(command_prefix='>')

@bot.command()
async def positions(context):
    positions = api.list_positions()    
    await context.send(f"Positions: {positions}")
    await context.send(f"{context.author}")

@bot.command()
async def buy(context, ticker, quantity):
    print(f"Recieved a buy order for {quantity} shares of {ticker}")
    if(context.author == "Scarzer#8810"):
        buy_order = api.submit_order(ticker, quantity, 'buy', 'market', 'day')
    else:
        buy_order = "No"
    await context.send(f"{buy_order}")


@bot.command()
async def check(context, ticker):
    print(f"Checking the price of a stonk")
    try:
        # last_trade_price = api.get_last_trade(ticker)
        # await context.send(f"Last price ${last_trade_price.price}")
        bars = api.get_barset(ticker, 'day', limit=1000)
        bars = bars.df[ticker]
        
        fig = io.BytesIO()
        
        plt.title(f"{ticker} -- Last Price {bars.tail(1)['close']}")
        plt.plot(bars["close"])
        plt.savefig(fig, format="png")
        fig.seek(0)

        await context.send(file=discord.File(fig, f"{ticker}.png"))
        plt.close()

    except HTTPError:
        await context.send(f"I failed finding the stock")


@bot.command()
async def account(context):
    print(f"Checking account")
    await context.send(f"{api.get_account()}")

@bot.command()
async def orders(context):
    print(f"Getting orders")
    await context.send(f"{api.list_orders()}")

@bot.command()
async def order(context, order_id):
    print(f"Getting a specific order")
    await context.send(f"{api.get_order(order_id)}")

bot.run(TOKEN)