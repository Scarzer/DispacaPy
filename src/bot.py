import discord
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi
from discord.ext import commands
from requests.models import HTTPError
import io, os

## CONSTANTS
TOKEN = os.environ.get("DISCORD_TOKEN")
ALPACA_KEY_ID = os.environ.get("ALPACA_KEY_ID")
ALPACA_KEY_SECRET = os.environ.get("ALPACA_KEY_SECRET")

plt.rcParams.update({'xtick.labelsize' : 'small',
                     'ytick.labelsize' : 'small',
                     'figure.figsize' : [16,9]})

api = tradeapi.REST(ALPACA_KEY_ID, ALPACA_KEY_SECRET, base_url='https://paper-api.alpaca.markets', api_version='v2') # or use ENV Vars shown below
account = api.get_account()
api.list_positions()

bot = commands.Bot(command_prefix='>')

## Embed Generation was done with the help of the discord embed sandbox
## https://cog-creators.github.io/discord-embed-sandbox/

def generate_account_embed(account_info) -> discord.Embed:
    """ 
    Account details are found in the API documetnation
    https://alpaca.markets/docs/api-documentation/api-v2/account/
    """
    embed=discord.Embed(title="Account Status", color=0x22ff00)
    embed.add_field(name="Cash", value=f"${account_info.cash}", inline=True)
    embed.add_field(name="Buying Power", value=f"${account_info.buying_power}", inline=True)
    embed.add_field(name="Portfolio Power", value=f"${account_info.portfolio_value}", inline=True)

    return embed

@bot.command()
async def positions(context):
    positions = api.list_positions()    
    await context.send(f"Positions: {positions}")

@bot.command()
async def buy(context, ticker, quantity):
    print(f"Recieved a buy order for {quantity} shares of {ticker} from {context.author}")
    buy_order = api.submit_order(ticker, quantity, 'buy', 'market', 'day')
    await context.send(f"{buy_order}")

@bot.command()
async def test(context):
    await context.send(f"Your ID is {context.author.id}")

@bot.command()
async def check(context, *ticker):
    print(f"Checking the price of a stonk")
    try:
        # last_trade_price = api.get_last_trade(ticker)
        # await context.send(f"Last price ${last_trade_price.price}")
        print(ticker)
        bars = api.get_barset(ticker, 'day', limit=100)
        bars = bars.df[ticker]
        
        fig = io.BytesIO()
        
        plt.title(f"{ticker} -- Last Price {bars.tail(1)['close'].values[0]:.02f}")
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
    account_info = api.get_account()
    account_embed = generate_account_embed(account_info)
    await context.send(embed=account_embed)

@bot.command()
async def orders(context):
    print(f"Getting orders")
    await context.send(f"{api.list_orders()}")

@bot.command()
async def order(context, order_id):
    print(f"Getting a specific order")
    await context.send(f"{api.get_order(order_id)}")

bot.run(TOKEN)