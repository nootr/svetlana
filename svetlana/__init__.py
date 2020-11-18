from svetlana.webdiplomacy import WebDiplomacyClient
from svetlana.bot import DiscordClient

wd_client = WebDiplomacyClient()
bot = DiscordClient(wd_client)
