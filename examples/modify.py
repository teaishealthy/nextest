from nextcord import Client
from nextcord_testing import Framework


client = Client("token")

framework = Framework.modify(client)

client.run()