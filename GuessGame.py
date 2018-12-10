import discord
import os
import random

# Each step of the game
# position, length 
STEPS = ((0, 2), (0, 3), (1, 3), (2, 3), (3, 3), (2, 4), (1, 4), (0, 4), (0, 5), (1, 5), (0, 6))

class GuessGame(object):
	"""An instance of the guessing game
	"""
	
	def __init__(self, client, player):
		self.client = client
		self.player = player
		self.channel = client.get_channel('512067512230215681')

	def load_words(self, filename, length):

		"""Returns a list of all words contained in filename that have the given length

		Parameters:
			filename(str): The filename of the desired file to be read
			length(int): The desired number of letters of words for the list

		Returns:
			list: a list of length letter words from filename.
		"""
		
		word_list = open(filename, 'r')
		filtered_list = [ ] 
		for line in word_list: 
			word = line.strip() 
			if len(line) == length+1: 
				filtered_list.append(word)
		word_list.close()
		return filtered_list

	async def compute_score(self, guess, position, word):
		"""Computes the score for a given guess.

		Parameters:
			guess(str): The guessing input word to be scored.
			word(str): The unknown six letter word to compare guess with.

		Returns:
			int: the score in the given round.
		"""
		score = 0
		sliced_word = word[position:position+len(guess)] 
		for letter in word:
			if letter in guess:
				score += 20
		for c1, c2 in zip(guess, sliced_word):
			if c1 == c2:
				score += 80
		return score

					
		
	async def prompt_guess(self, position, length):
		"""Repeatedly prompts the user to make a guess at a given position.

		Ends when a valid input is detected.

		Parameters:
			position(int): The index of which the guess starts at in the unknown word
			length(int): The specified word length desired

		Returns:
			str: the first guess in words.txt with the specified length
		"""

		lower_bound = position + 1
		upper_bound = position + length

		await self.client.send_message(self.channel, content = "Now guess " + str(length) + " letters corresponding to letters "
					  + str(lower_bound) + " to " + str(upper_bound) + " of the unknown word: ")
		key = False
		while key is False:
			guess = await self.client.wait_for_message(author=self.player)
			if len(guess.content) is length:
				key = True
			else:
				await self.client.send_message(self.channel, content = "Invalid guess {}. Should be {} characters long".format(str(guess.content), str(length)))
		return guess

	async def play_guess(self):
		await self.client.send_message(self.channel, content = "Welcome to the brain teasing zig-zag word game.")
		await self.client.send_message(self.channel, content = "Hi " + self.player.name + "! We have selected a 6 letter word for you to guess.")
		await self.client.send_message(self.channel, content = "Let the game begin!")
		word = random.choice(self.load_words("words.txt", 6))
		cumulative_score = 0
		empty = "______"

		for position, length in STEPS:
			response = await self.prompt_guess(position, length)
			guess = response.content
			score = await self.compute_score(guess, position, word)
			cumulative_score += score
			await self.client.send_message(self.channel, content = "Your guess and score were: " + str(empty[ :position] + guess + empty[position + length: ]) + " : " + str(score))
		if guess == word:
			await self.client.send_message(self.channel, content = "\nCongratulations! You correctly guessed the word '" + str(word) + "'.")
			await self.client.send_message(self.channel, content = "Your total score was " + str(cumulative_score) + ".")
		else:
			await self.client.send_message(self.channel, content = "\nYou did not manage to guess the correct word. It was '" + str(word) + "'. Better luck next time.")
			await self.client.send_message(self.channel, content = "Your total score was " + str(cumulative_score) + ".")
