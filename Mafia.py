import os
import discord

from urllib.parse import urlencode
from urllib.request import Request, urlopen

MAX_PLAYERS = 10
MIN_PLAYERS = 4
gamesChannel = '512067512230215681'
rolesFile = "mafiaroles" # the file contains lines of (#:D,N,M,I)
roleNames = {'D':'Detective', 'N':'Nurse', 'M':'Mafioso', 'I':'Innocent'}
roleNamesPlural = {'D':'Detectives', 'N':'Nurses', 'M':'Mafiosos', 'I':'Innocents'}

class MafiaGame(object):
	"""Represents the mafia game, contains all the players in the game
	Handles game interactions for a single instance of the game
	"""
	def __init__(self, client, host):
		self.client = client
		self.host = host
		self.maxPlayers = MIN_PLAYERS
		self.players = [self.host] # The host is a Member, and the invitees are Users. Member extends User
		self.playerIds = [self.host.id]
		self.playerNames = [self.host.mention] # Contains the mentions
		self.channel = client.get_channel(gamesChannel)
		self.roles = {'D':0, 'N':0, 'M':0, 'I':0} # dictionary containing the number of each role e.g. for 5 players {D:0, N:1, M:2, I:2}
		print("host is: {}".format(self.host))

	# Sets up the initial conditions of the game, asks the host how many players they would like
	# and which players to invite
	async def setup(self):
		await self.client.send_message(self.channel, content = "Welcome to Mafia, {},".format(self.host.name) +
			" please specify the maximum amount of players [{} - {}].".format(MIN_PLAYERS, MAX_PLAYERS))

		# Helper method that checks the given maxPlayers
		def check(msg):
			if msg.content.isdigit():
				print(msg.content)
				number = int(msg.content)
				if number >= MIN_PLAYERS and number <= MAX_PLAYERS:
					return True
			return False

		# Get the maxPlayers for the game
		maximum = await self.client.wait_for_message(author=self.host, check=check)
		maxPlayers = int(maximum.content)
		self.maxPlayers = maxPlayers

		# Now we need to add a bunch of players to fill up the game
		playerCount = 1 # Starts at 1 for the host
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

						# the mention will be in the form <@199549974671917056> or <@!199549974671917056>
						# if they have a nickname the ! will be added, we need to remove @, ! and <> for the id
						if mention[2].isdigit():
							userid = mention[2:len(mention) - 1]
						else:
							userid = mention[3:len(mention) - 1]

						# Get the user info of the player who was mentioned (invited)
						player = await self.client.get_user_info(userid)

						# Before we actually add the player we need to check if they were already added
						if player.id in self.playerIds:
							await self.client.send_message(self.channel, content = "Player already in lobby.")
							continue

						playerCount += 1
						self.players.append(player)
						self.playerIds.append(player.id)
						self.playerNames.append(player.mention)

						# Now we need to check that the second word is a target person
					else: # Message received was $invite [something something] not length 2
						await self.client.send_message(self.channel, content = "Usage: [$invite @player]")
				else: # Message didnt start with "$invite "
					await self.client.send_message(self.channel, content = "Usage: [$invite @player]")

		# We have reached the maximum amount of players
		await self.client.send_message(self.channel, content = "[{}/{}].".format(str(playerCount), str(self.maxPlayers)) +
				" Maximum players reached.")
		await self.client.send_message(self.channel, content = "Players are: {}".format(self.playerNames))

		await self.send_roles()

	# Sends messages to each player for what their role is
	async def send_roles(self):
		key = ['D', 'N', 'M', 'I'] # these are the keys of the dictionary
		# First we need to read the mafiaroles file to know how many of each role
		roleInfo = open(rolesFile, 'r')
		for line in roleInfo: # each line looks like '#:D,N,M,I'
			data = line.split(':') # data is ['#','D,N,M,I']
			if int(data[0]) is self.maxPlayers:
				roleCounts = data[1].split(',') # roleCounts is ['D', 'N', 'M', 'I']
				i = 0
				for count in roleCounts:
					self.roles[key[i]] = int(count)
					i += 1

		# at this point self.roles should be filled up with the correct roles count
		# we need to let everyone know how many of each role there is
		i = 0
		for char in key:
			if self.roles[char] is 0:
				await self.client.send_message(self.channel, content = "There are no {}s.".format(roleNames[char])) 
			elif self.roles[char] is 1:
				await self.client.send_message(self.channel, content = "There is 1 {}.".format(roleNames[char]))
			else:
				await self.client.send_message(self.channel, content = "There are {} {}.".format(self.roles[char], roleNamesPlural[char]))







	async def play_mafia(self):
		await self.setup();
