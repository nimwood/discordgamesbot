import discord
import os
import random

from GuessGame import GuessGame
from Mafia import MafiaGame

secret = 'NDQ2OTkyMjM2NjAxOTMzODI0.Ds0Bjg.d2ipHFaswpqlXYqM6mBz_RDayH8'

client = discord.Client()

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))
	await client.send_message(client.get_channel('512067512230215681'), "Games to play: '$playguess'")

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith('$playguess'):
		game = GuessGame(client, message.author)
		await game.play_guess()

	if message.content.startswith('$playmafia'):
		game = MafiaGame(client, message.author)
		await game.play_mafia()

client.run(secret)
