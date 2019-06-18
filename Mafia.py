import os
import discord
from random import shuffle

from urllib.parse import urlencode
from urllib.request import Request, urlopen

MAX_PLAYERS = 10
MIN_PLAYERS = 4
key = ['D', 'N', 'M', 'I'] # these are the keys of the dictionary
gamesChannel = '512067512230215681'
rolesFile = "mafiaroles" # the file contains lines of (#:D,N,M,I)
roleNames = {key[0]:'Detective', key[1]:'Nurse', key[2]:'Mafioso', key[3]:'Innocent'}
roleNamesPlural = {key[0]:'Detectives', key[1]:'Nurses', key[2]:'Mafiosos', key[3]:'Innocents'}

class MafiaPlayer(object):
	"""Represents a single player in a mafia game, cotains user info as well as
	game information and player state
	"""
	def __init__(self, user):
		self.user = user # User object whcihc contains their id and their mention tag (use this to DM)
		self.role = 'I' # Character representing what role they are, e.g 'D'
		self.isAlive = True

	# Returns the player role
	def get_role(self):
		return self.role

	# Sets the player's role
	def set_role(self, role):
		self.role = role
		
	# Sets the player as dead
	def kill(self):
		self.isAlive = False

class MafiaGame(object):
	"""Represents the mafia game, contains all the players in the game
	Handles game interactions for a single instance of the game
	"""
	def __init__(self, client, host):
		self.client = client # this is the bot
		self.host = host
		self.maxPlayers = MIN_PLAYERS

		self.townsPeople = [] # this is a list of MafiaPlayer objects
		self.mafiaPeople = [] # this is a list of Mafia players objects
		self.mafiaNames = [] # this is a list of Mafia player names

		self.players = [self.host] # The host is a Member, and the invitees are Users. Member extends User
		self.playerIds = [self.host.id]
		self.playerNames = [self.host.mention] # Contains the mentions
		self.channel = client.get_channel(gamesChannel)
		self.roles = {'D':0, 'N':0, 'M':0, 'I':0} # dictionary containing the number of each role e.g. for 5 players {D:0, N:1, M:2, I:2}

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
				" Add players with [$invite @player1 @player2...]")

			# Get the target player
			x = False # valid invite target
			while x is False:
				guess = await self.client.wait_for_message(author=self.host)
				if guess.content.startswith("$invite "):

					# The message has to be in the form '$invite @user1 @user2 @user3...'
					info = guess.content.split(" ")
					info.pop(0) # remove the $invite string leaving only the mentions

					if len(info) < 1:
						await self.client.send_message(self.channel, content = "Usage: [$invite @player1 @player2...]")
					elif len(info) > self.maxPlayers - playerCount: # too many players added
						await self.client.send_message(self.channel, content = "Too many players.")
					else:
						x = True

						for i in range(len(info)):
							mention = info[i]
							userid = self.strip_id(mention)

							# Get the user info of the player who was mentioned (invited)
							player = await self.client.get_user_info(userid)

							# Before we actually add the player we need to check if they were already added
							if player.id in self.playerIds:
								await self.client.send_message(self.channel, content = "{} already in lobby.".format(player.name))
							else:
								self.players.append(player)
								self.playerIds.append(player.id)
								self.playerNames.append(player.mention)
								playerCount += 1
				else: # Message didnt start with "$invite "
					await self.client.send_message(self.channel, content = "Usage: [$invite @player1 @player2...]")

		# We have reached the maximum amount of players
		await self.client.send_message(self.channel, content = "[{}/{}].".format(str(playerCount), str(self.maxPlayers)) +
				" Maximum players reached.")
		await self.client.send_message(self.channel, content = "Players are: {}".format(self.playerNames))

		await self.send_roles()

	# converts a <@!199549974671917056> mention tag and returns the id 199549974671917056
	def strip_id(self, mention):
		# the mention will be in the form <@199549974671917056> or <@!199549974671917056>
		# if they have a nickname the ! will be added, we need to remove @, ! and <> for the id
		if mention[2].isdigit():
			userid = mention[2:len(mention) - 1]
		else:
			userid = mention[3:len(mention) - 1]
		return userid

	# Sends messages to each player for what their role is
	async def send_roles(self):
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

		# fill the list of MafiaPlayers
		for i in range(self.maxPlayers):
			self.townsPeople.append(MafiaPlayer(self.players[i]))
		
		# Now we need to assign the roles to each player
		shuffle(self.townsPeople)

		playerPointer = 0 # from 0 to maxPlayers - 1
		currentRole = 0 # 0 to 3 for D, N, M, I
		for count in roleCounts: # for each number of each roles
			for i in range(int(count)):
				self.townsPeople[playerPointer].role = key[currentRole]

				if currentRole is 2: # if we are the mafias add them to a list
					self.mafiaPeople.append(self.townsPeople[playerPointer])
					self.mafiaNames.append(self.townsPeople[playerPointer].user.name)

				playerPointer += 1

			currentRole += 1

		# Now send messages to each player of their role
		for player in self.townsPeople:
			await self.client.send_message(player.user, content = "You are the {}.".format(roleNames[player.role]))

		# Let the mafia know who their team is
		for player in self.townsPeople:
			if player.role is 'M':
				await self.client.send_message(player.user, content = "The Mafia consists of: {}.".format(self.mafiaNames))


	# async def play_mafia(self):
	# 	await self.setup();

	# async def night_cycle(self):

	# async def day_cycle(self):

	# Checks whether or not the game is over, returns 0 for game not over, 1 for innocents win, 2 for mafia wins
	def check_game_over(self):
		innocentCount = len(self.townsPeople) - len(self.mafiaPeople)
		mafiaCount = len(self.mafiaPeople)
		if mafiaCount == 0:
			return 1
		elif innocentCount <= mafiaCount:
			return 2

		# Game not over
		return 0

