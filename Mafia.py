import os
import discord

from urllib.parse import urlencode
from urllib.request import Request, urlopen

MAX_PLAYERS = 10
MIN_PLAYERS = 3
gamesChannel = '512067512230215681'

class MafiaGame(object):
	"""Represents the mafia game, contains all the players in the game
	Handles game interactions for a single instance of the game
	"""
	def __init__(self, client, host):
		self.client = client
		self.host = host
		self.maxPlayers = MIN_PLAYERS
		self.players = [self.host]
		self.channel = client.get_channel(gamesChannel)

	# Sets up the initial conditions of the game, asks the host how many players they would like
	# and which players to invite
	async def setup(self):
		await self.client.send_message(self.channel, content = "Welcome to Mafia, {},".format(self.host.name) +
			" please specify the maximum amount of players [3 - 10].")

		# Helper method that checks the given maxPlayers
		def check(msg):
			if msg.content.isdigit:
				number = int(msg.content)
				if number >= 3 and number <= 10:
					return True
			return False

		# Get the maxPlayers for the game
		maximum = await self.client.wait_for_message(author=self.host, check=check)
		maxPlayers = int(maximum.content)
		self.maxPlayers = maxPlayers

		# Now we need to add a bunch of players to fill up the game
		playerCount = 1 # one for the host
		while playerCount < self.maxPlayers:
			await self.client.send_message(self.channel, content = "[{}/{}].".format(str(playerCount), str(self.maxPlayers)) +
				" Add players with [$invite @player]")

			# Get the target player
			key = False
			while key is False:
				guess = await self.client.wait_for_message(author=self.host)
				if guess.content.startswith("$invite "):

					# The message has to be in the form of two words
					info = guess.content.split(" ")
					if len(info) is 2:
						key = True
						mention = info[1]
						userid = mention[2:len(mention) - 1]
						await self.client.send_message(self.channel, content = userid)

						url = 'https://discordapp.com/api/users/{}'.format(userid) # Set destination URL here
						post_fields = {'recipient_id' : userid}     # Set POST fields here

						request = Request(url, urlencode(post_fields).encode())
						json = urlopen(request).read().decode()
						print(json)

						# Now we need to check that the second word is a target person
					else: # Message received was $invite [something something] not length 2
						await self.client.send_message(self.channel, content = "Usage: [$invite @player]")
				else: # Message didnt start with "$invite "
					await self.client.send_message(self.channel, content = "Usage: [$invite @player]")


	async def play_mafia(self):
		await self.setup();

