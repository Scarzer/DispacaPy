## Discord.py is a well supported wrapper for the Discord API
import discord
from discord import reaction
from discord.ext import commands
## alpaca_trade_api wraps the Alpaca API
import alpaca_trade_api as tradeapi
## We'll be using matplotlib to generate simple line graphs
import matplotlib.pyplot as plt
## Useful imports to have
import io, os
from asyncio import TimeoutError
## Environmental Consts
## These are set in the Dockerfile
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
ALPACA_KEY_ID = os.environ.get("ALPACA_KEY_ID")
ALPACA_KEY_SECRET = os.environ.get("ALPACA_KEY_SECRET")
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'
plt.rcParams.update({'xtick.labelsize' : 'small',
                     'ytick.labelsize' : 'small',
                     'figure.figsize' : [16,9]})
## Connect to your Alpaca account
alpaca_api = tradeapi.REST(ALPACA_KEY_ID,
                           ALPACA_KEY_SECRET,
                           base_url=ALPACA_BASE_URL, 
                           api_version='v2')

## Initialize our Discord bot
bot = commands.Bot(command_prefix='>')
## Create our first command
@bot.command()
async def hello_world(context):
    await context.send("Hello Dispaca!")

def generate_account_embed(account):
    embed=discord.Embed(title="Account Status", 
                       description="Alpaca Markets Account Status", 
                       color=0x47c02c)
    
    embed.add_field(name="Cash", value=f"${account.cash}")
    embed.add_field(name="Buying Power", value=f"${account.buying_power}")
    embed.add_field(name="Portfolio Value", value=f"${account.portfolio_value}")
    embed.add_field(name="Equity", value=f"${account.equity}")
    
    return embed
## Replace the previous instance of this function in bot.py
@bot.command()
async def account(context):
    print(f"Checking account")
    account_info = alpaca_api.get_account()
    account_embed = generate_account_embed(account_info)
    await context.send(embed=account_embed)

@bot.command()
async def check(context, ticker):
    print(f"Checking the history of a stock")
    
    ## Make sure the symbol is upper case
    if isinstance(ticker, str):
        ticker = ticker.upper()
    try:
        ## Retrieve the last 100 days of trading data
        bars = alpaca_api.get_barset(ticker, 'day', limit=100)
        bars = bars.df[ticker]
        
        ## This bytes buffer will hole the image we send back
        fig = io.BytesIO()
        ## Grab the last closing price
        last_price = bars.tail(1)['close'].values[0]
        ## Make a chart from the data we retrieved
        plt.title(f"{ticker} -- Last Price ${last_price:.02f}")
        plt.xlabel("Last 100 days")
        plt.plot(bars["close"])
        ## Save the image to the buffer we created earlier
        plt.savefig(fig, format="png")
        fig.seek(0)
        ## Sending back the image to the user.
        await context.send(file=discord.File(fig, f"{ticker}.png"))
        plt.close()
    except Exception as e:
      await context.send(f"Error getting the stock's data: {e}")

def get_last_price(ticker) -> float:
    last_price = 0.0

    if isinstance(ticker, str):
        ticker = ticker.upper()
    try:
        last_trade = alpaca_api.get_last_trade(ticker)
        last_price = float(last_trade.price)
    except Exception as e:
        last_price = -1.0
    
    return last_price

@bot.command()
async def last_price(context, ticker):
    try:
        last_price = get_last_price(ticker)
        await context.send(f"{ticker} -- ${last_price.price}")
    except Exception as e:
        await context.send(f"Error getting the last price: {e}")

def generate_buy_embed(ticker, quantity, market_price) -> discord.Embed:
    embed = discord.Embed()

    total_cost = int(quantity) * market_price
    embed=discord.Embed(title=f"Buying {ticker}", 
                        description="Review your buy order below. \
                            React with 👍 to confim in the next 30 seconds")
    embed.add_field(name="Quantity", value=f"{quantity}", inline=False)
    embed.add_field(name="Per Share Cost", value=f"${market_price}", inline=False)
    embed.add_field(name="Estimated Cost", value=f"${total_cost}", inline=False)
    embed.add_field(name="In Force", value="Good Until Cancelled", inline=False )
    
    return embed

@bot.command()
async def buy(context, ticker, quantity):
    if isinstance(ticker, str):
        ticker = ticker.upper()

    ## Lets get some supporting information about this stock
    try:
        last_trade = alpaca_api.get_last_trade(ticker)
        last_price = last_trade.price
    except Exception as e:
        await context.send(f"Error getting the last price: {e}")
        return

    buy_embed = generate_buy_embed(ticker, quantity, last_price)

    await context.send(embed=buy_embed)

    ## Use this check to make sure the bot invoker is the only one to react
    def check(reaction, user):
        return user == context.message.author

    try:
        ## Wait for a reaction event. 30second timeout.
        reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
    except TimeoutError:
        await context.send("Cancelling the trade. No activity")

    else:
        if str(reaction.emoji) == '👍':
            await context.send("Executing on the trade")

            placed_order = alpaca_api.submit_order(symbol=ticker, qty=quantity, 
                                side='buy', type='market', time_in_force='gtc')
            await context.send(f"Placed orderd ID: {placed_order.id}")
        else:
            await context.send("Unexpected response. Cancelling Order")

## Start our bot
bot.run(DISCORD_TOKEN)