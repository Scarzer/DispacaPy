import discord
from alpaca_trade_api import rest

## Embed Generation was done with the help of the discord embed sandbox
## https://cog-creators.github.io/discord-embed-sandbox/

def generate_account_embed(account_info: rest.Account) -> discord.Embed:
    """ 
    Account details are found in the API documetnation
    https://alpaca.markets/docs/api-documentation/api-v2/account/
    """
    embed=discord.Embed(title="Account Status", color=0x22ff00)
    embed.add_field(name="Cash", value=f"${account_info['cash']}", inline=True)
    embed.add_field(name="Buying Power", value=f"${account_info['buying_power']}", inline=True)
    embed.add_field(name="Portfolio Power", value=f"{account_info['portfolio_value']}", inline=True)

    return embed