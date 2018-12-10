import discord
import os
import random

from GuessGame import GuessGame
from Mafia import MafiaGame

# The secret string used to get access to the bot
secret = 'NDQ2OTkyMjM2NjAxOTMzODI0.Ds0Bjg.d2ipHFaswpqlXYqM6mBz_RDayH8'

# Initialises the discord bot
client = discord.Client()

# Called whenever the bot first starts up and is ready to go
@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))
	await client.send_message(client.get_channel('512067512230215681'), "Games to play: '$playguess'")

# Called whenever there is a message in the current channel
@client.event
async def on_message(message):
	# Ignore messages by the bot itself
	if message.author == client.user:
		return

	# Play the guess game
	if message.content.startswith('$playguess'):
		game = GuessGame(client, message.author)
		await game.play_guess()

	# Play the mafia game
	if message.content.startswith('$playmafia'):
		game = MafiaGame(client, message.author)
		await game.play_mafia()

client.run(secret)
