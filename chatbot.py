# PA6, CS124, Stanford, Winter 2019
# v.1.0.3
# Chatbot.py
# Original Python code by Ignacio Cases (@cases)
######################################################################
import movielens

import numpy as np
import re
import random
from collections import Counter


# noinspection PyMethodMayBeStatic
class Chatbot:
	"""Simple class to implement the chatbot for PA 6."""

	def __init__(self, creative=False):
		self.name = 'popcornpal'
		self.creative = creative

		# This matrix has the following shape: num_movies x num_users
		# The values stored in each row i and column j is the rating for
		# movie i by user j
		self.titles, ratings = movielens.ratings()
		self.sentiment = movielens.sentiment()
		self.articles = ["the", "a", "an", "The", "A", "An", "le", "la", "lo", "las", "los", "il", "der", "les", "die", "el"]
		self.count = 0 # keep track of number of movies user has given
		self.clarification = False
		self.prevMovies = []
		self.prevSentiment = 0
		self.currMovie = ""
		self.currSentiment = 0 

		#############################################################################
		# TODO: Binarize the movie ratings matrix.                                  #
		#############################################################################

		# Binarize the movie ratings before storing the binarized matrix.
		# print(ratings[0])
		self.ratings = self.binarize(ratings, threshold=2.5)
		# print(self.ratings[0])

		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################

	#############################################################################
	# 1. WARM UP REPL                                                           #
	#############################################################################

	def greeting(self):
		"""Return a message that the chatbot uses to greet the user."""
		#############################################################################
		# TODO: Write a short greeting message                                      #
		#############################################################################

		greeting_message =  "Hi, there! I'm PopcornPal! I'm going to recommend a movie to you, but first I need to know a little more about your taste in movies. Can you tell me about a movie that you have seen? (Please put the movie title in quotation marks!) I need 5 preferences recommendations"

		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return greeting_message

	def goodbye(self):
		"""Return a message that the chatbot uses to bid farewell to the user."""
		#############################################################################
		# TODO: Write a short farewell message                                      #
		#############################################################################

		goodbye_message = "Thank you for hanging out with me! Stay in touch! Goodbye!"

		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return goodbye_message

	###############################################################################
	# 2. Modules 2 and 3: extraction and transformation                           #
	###############################################################################

	def process(self, line):
		"""Process a line of input from the REPL and generate a response.
		This is the method that is called by the REPL loop directly with user input.
		You should delegate most of the work of processing the user's input to
		the helper functions you write later in this class.
		Takes the input string from the REPL and call delegated functions that
		  1) extract the relevant information, and
		  2) transform the information into a response to the user.
		Example:
		  resp = chatbot.process('I loved "The Notebook" so much!!')
		  print(resp) // prints 'So you loved "The Notebook", huh?'
		:param line: a user-supplied line of text
		:returns: a string containing the chatbot's response to the user input
		"""
		#############################################################################
		# TODO: Implement the extraction and transformation in this method,         #
		# possibly calling other functions. Although modular code is not graded,    #
		# it is highly recommended.                                                 #
		#############################################################################
		if self.creative:
			# response = "I processed {} in creative mode!!".format(line)
			found_movies = []
			extracted_movies = self.extract_titles(line)
			response = self.checkEmotion(line)
			response += self.checkArbitrary(line)

			# extract sentiment
			sentiment = self.extract_sentiment(line)

			# prevMovie = self.prevMovies[0]
			# prevSentiment = self.prevSentiment

			if self.clarification:
				if self.toLower(line) == "yes":
					self.currMovie = self.prevMovies[0]
					self.currSentiment = self.prevSentiment
					self.prevMovies = []
					self.prevSentiment = 0
					self.clarification = False
					#response += "sentiment + movie" # PLACEHOLDER

				elif self.toLower(line) == "stop":
					self.prevMovies = []
					self.prevSentiment = 0
					self.clarification = False
					response += "Starting a new search query"
					return response
				elif self.toLower(line) == "no":
					response += "Please provide me another clarification on your search. If you wish to make another search type: STOP"
					self.clarification = True
					return response
				else:

					"""
					DORIAN STOPPED HERE
					"""

					found_movies = self.disambiguate(line, self.prevMovies)
					if len(found_movies) == 0:
						response += "I'm sorry, I couldn't find anything with your clarification. Starting new search query."
						self.prevMovies = []
						self.prevSentiment = 0
						self.clarification = False
						return response
					elif len(found_movies) == 1:
						movie = self.titles[found_movies[0]]
						self.prevMovies = [movie]
						response += "Did you mean " + movie + "? Let me know \"yes\" or \"no\"."
						return response
					elif len(found_movies) > 1:
						self.clarification = True
						self.prevMovies = found_movies
						self.prevSentiment = sentiment
						response += "I've found some movies similar to what you inputted. Could you give me more info to help me pick the right one on the ones I've found?"
						print(found_movies)
						return response

			# if no movies are found, ask user to talk about a movie
			if len(extracted_movies) == 0 and self.currMovie == "":
				if response == "":
					response += "Sorry, "
				response += self.getArbitraryResponse(random.randint(0,5))
				response += self.getArbitrarySuggestion(random.randint(0,5))
				response += "(Remember, I only recognize movies in quotation marks!)"
				return response

			# DISAMBIGUATE
			if len(extracted_movies) > 1:
				if response == "":
					response += "Oh wait, "
				response += "can you tell me about the movies one at a time? Go ahead."
				return response

			for m in extracted_movies:
				found_movies.extend(self.find_movies_by_title(m))

			if len(found_movies) == 0 and self.currMovie == "":
				for m in extracted_movies:
					found_movies.extend(self.find_movies_closest_to_title(m))
				if len(found_movies) == 0:
					response += "I'm sorry, I don't understand"
					return response
				elif len(found_movies) == 1:
					movie = self.titles[found_movies[0]][0]
					self.clarification = True
					self.prevMovies.append(movie)
					self.prevSentiment = sentiment
					response += "Did you mean " + movie + "?"
					return response
				elif len(found_movies) > 1:
					self.clarification = True
					self.prevMovies = found_movies
					self.prevSentiment = sentiment
					response += "I've found some movies similar to what you inputted. Could you give me more info to help me pick the right one on the ones I've found?"
					print(found_movies)
					return response

			if len(found_movies) > 1:
				self.clarifiction = True
				self.prevMovies = found_movies
				self.prevSentiment = sentiment
				response += "I've found some movies similar to what you inputted. Could you give me more info to help me pick the right one on the ones I've found?"
				print(found_movies)
				return response
			"""
			if len(extracted_movies) == 0:
				if response == "":
					response += "Sorry, "
				response += self.getArbitraryResponse(random.randint(0,5))
				response += self.getArbitrarySuggestion(random.randint(0,5))
				response += "(I only recognize movies in quotation marks)"
				return response

			"""		

			# if self.clarification == False:
			# 	# put movie -> sentiment into dict
			# 	extracted_movie = extracted_movies[0]
			# else:
			# 	extracted_movie = self.prevMovies[0]
			# 	sentiment = self.prevSentiment
			# 	self.clarification = False
			# 	self.prevMovies = []
			# 	self.prevSentiment = 0

			if self.currMovie != "":
				extracted_movie = self.currMovie
				self.currMovie = ""
				sentiment = self.currSentiment
				self.currSentiment = 0
			else:
				extracted_movie = extracted_movies[0]

			# get sentiment and respond
			if sentiment == 0:
				response += "I couldn't tell if you liked \"" + extracted_movie + "\". Can you tell me more about " + extracted_movie + "? "
				return response
			elif sentiment > 0:
				response += "I'm glad you liked \"" + extracted_movie + "\"! It sounds like an awesome movie! " + "I'll definitely check it out some time. "
			elif sentiment < 0:
				response += "I'm sorry you didn't like \"" + extracted_movie + "\". It sounds like a terrible movie! " + "I'll make sure to avoid that one, for sure. "


			self.count += 1
			self.movieToYear = {}

			"""
			print("extracted movies: ", extracted_movies)
			print("found movies: ",found_movies)
			print("sentiment: ", sentiment)
			"""

			if self.count == 5:
				user_matrix = self.createUserMatrix()
				recommendations = self.recommend(user_matrix, self.ratings, 5, creative=False)
				response += "\nThat's enough for me to make a recommendation. I suggest you watch " + self.titles[recommendations[0]][0] + ". Would you like to hear another recommendation? (Or enter :quit if you're done.) "
				print("recommendations", recommendations)
				self.count = 0
			else: 
				response += "Thanks for sharing that with me! \n\nCan you tell me about another movie?"



		else:
			#STARTER SECTION

			response = "I processed {} in starter mode!!".format(line) #Inserts line for {}


			extracted_movies = self.extract_titles(line)
			if len(extracted_movies) == 0:
				response = "Sorry, I don't think I understand... Can you tell me about a movie that you've seen? (I only recognize movies in quotation marks)"
				return response

			if len(extracted_movies) > 1:
				response = "Oh wait, can you tell me about the movies one at a time? Go ahead."
				return response

			sentiment_val = self.extract_sentiment(line)
			extracted_movie = extracted_movies[0]

			found_movies = []

			for m in extracted_movies:
				found_movies.extend(self.find_movies_by_title(m))

			if len(found_movies) == 0:
				response = "I'm sorry, I haven't heard about that movie before. Can you tell me about another one? (And please make sure to put the movie title in quotation marks!)"
				return response

			sentiment = self.extract_sentiment(line)
			if sentiment == 0:
				return "Hmmm, I couldn't tell if you liked \"" + extracted_movie + "\". Can you tell me more about " + extracted_movie + "?"
			elif sentiment > 0:
				response = "Nice, I'm glad you liked \"" + extracted_movie + "\"! It sounds like an awesome movie! " + "I'll definitely check it out some time."
			elif sentiment < 0:
				response = "Ugh, I'm sorry you didn't like \"" + extracted_movie + "\". It sounds like a terrible movie! " + "I'll make sure to avoid that one, for sure."


			self.count += 1
			self.movieToYear = {}

			"""
			print("extracted movies: ", extracted_movies)
			print("found movies: ",found_movies)
			print("sentiment: ", sentiment_val)
			"""

			if self.count == 5:
				user_matrix = self.createUserMatrix()
				recommendations = self.recommend(user_matrix, self.ratings, 5, creative=False)
				response += "\nThat's enough for me to make a recommendation. I suggest you watch " + self.titles[recommendations[0]][0] + ". Would you like to hear another recommendation? (Or enter :quit if you're done.)"
				print("recommendations", recommendations)
				self.count = 0
			else: 
				response += " Thanks for sharing that with me! \n\nCan you tell me about another movie?"


			# user_matrix = np.zeros((self.ratings.shape[0], 1))
			# print(user_matrix)
			# print(user_matrix.shape)

			'''
			TESTING RECOMMEND
			+1 : 8514, 7953, 6979, 7890
			I like "Wonder Woman (2009)"
			I like "The Dark Knight Rises (2012)"
			I like "The Incredible Hulk (2008)"
			I like "The Avengers (2012)"
			-1: 7369, 8726
			I don't like "Saw VI (2009)"
			I don't like "Dumb and Dumber To (2014)"
			'''

		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return response

	def checkArbitrary(self, input_text):
		can_structure = '.*[Cc]an you ([^?.]*)?'
		matches = re.findall(can_structure, input_text)
		if len(matches) != 0:
			response = "Why do you want to know if I can " + matches[0] + "? Anyway, "
			return response

		what_structure = '(?:[Ww]hat\'s|[Ww]hat is) ([^?.]*)?'
		matches = re.findall(what_structure, input_text)
		if len(matches) != 0:
			response = "Hm, I'm not exactly sure what " + matches[0] + " is... Anyway, "
			return response


		are_structure = '[Aa]re you ([^?.]*)?'
		matches = re.findall(are_structure, input_text)
		if len(matches) != 0:
			response = "I am not " + matches[0] + "... Anyway, "
			return response

		how_structure = '[Hh]ow do you ([^?.]*)?'
		matches = re.findall(how_structure, input_text)
		if len(matches) != 0:
			response = "Hm, I don't really know how I " + matches[0] + ". Anyway, "
			return response

		why_structure = '[Ww]hy do you ([^?.]*)?'
		matches = re.findall(why_structure, input_text)
		if len(matches) != 0:
			response = "Hm, I don't really know why I " + matches[0] + ". Anyway, "
			return response

		return ""


	def getArbitraryResponse(self, random):
		responses = [
		"I don't think that's really what I want to talk about right now. ",
		"I don't think I understand... ",
		"I'm a little confused. ",
		"I'm not sure I see what you mean. ",
		"I think I'd prefer to talk about a film. ",
		"I think you lost me there. "
		]

		return responses[random]

	def getArbitrarySuggestion(self, random):
		suggestions = [
		"Why don't we talk about movies? ",
		"Can you tell me about a movie that you've seen? ",
		"Do you think we could go back to talking about movies? ",
		"How about we talk about movies? ",
		"Can we talk about movies instead, please? ",
		"Should we talk about movies instead? "
		]

		return suggestions[random]

	def checkEmotion(self, input_text):
		input_list = input_text.split()
		for word in input_list:
			# print("word: ", word)
			happy = self.checkHappy(word)
			if happy == True:
				return "Sounds like you're happy! Glad to hear it! Anyway, "
			sad = self.checkSad(word)
			if sad == True:
				return "Oh no, did I say something to make you sad? Why don't we talk about something else? Anyway, "
			angry = self.checkAngry(word)
			if angry == True:
				return "Oh no, did I say something to make you angry? I apologize, I didn't mean to. Anyway, "
		return ""



	def checkHappy(self, word):
		""" 
		Returns True if the word is a word to express happiness
		Returns False if the word is not a word to expres happiness
		"""
		patterns = [
			'(^happy$)',
			'(^smile$)',
			'(^laugh$)',
			'(^joy$)',
			'(^joyful$)',
			'(^content$)',
			'(^glee$)',
			'(^cheer$)',
			'(^cheerful$)',
			'(^delight$)'
		]

		word = self.removePunctuationHelper(word)
		forms = self.getWordForms(word)
		for form in forms:
			for p in patterns:
				# print("comparing ", form, " to ", p)
				if re.fullmatch(p, form) != None:
					return True

		return False

	def checkSad(self, word):
		""" 
		Returns True if the word is a word to express sadness
		Returns False if the word is not a word to expres sadness
		"""
		patterns = [
			'(^cry$)',
			'(^sad$)',
			'(^depressed$)',
			'(^somber$)',
			'(^melancholy$)',
			'(^dismal$)',
			'(^sorrow$)',
			'(^sob$)',
			'(^gloom$)',
			'(^grief$)',
			'(^grieve$)'

		]

		word = self.removePunctuationHelper(word)
		forms = self.getWordForms(word)
		for form in forms:
			for p in patterns:
				# print("comparing ", form, " to ", p)
				if re.fullmatch(p, form) != None:
					return True

		return False

	def checkAngry(self, word):
		""" 
		Returns True if the word is a word to express anger
		Returns False if the word is not a word to expres anger
		"""
		patterns = [
			'(^angry$)',
			'(^anger$)',
			'(^mad$)',
			'(^upset$)',
			'(^scream$)',
			'(^frustrated$)',
			'(^furious$)',
			'(^fury$)',
			'(^annoy$)',
			'(^irritate$)',
			'(^infuriate$)',
			'(^exasperate$)', 
			'(^rage$)', 
			'(^wrath$)',
			'(^fume$)',
			'(^outrage$)',
			'(^enrage$)', 
			'(^livid$)',
			'(^piss$)'
		]

		word = self.removePunctuationHelper(word)
		forms = self.getWordForms(word)
		for form in forms:
			for p in patterns:
				# print("comparing ", form, " to ", p)
				if re.fullmatch(p, form) != None:
					print("returned true with: ", form, " + ", p)
					return True

		return False


	@staticmethod
	def preprocess(text):
		"""Do any general-purpose pre-processing before extracting information from a line of text.
		Given an input line of text, this method should do any general pre-processing and return the
		pre-processed string. The outputs of this method will be used as inputs (instead of the original
		raw text) for the extract_titles, extract_sentiment, and extract_sentiment_for_movies methods.
		Note that this method is intentially made static, as you shouldn't need to use any
		attributes of Chatbot in this method.
		:param text: a user-supplied line of text
		:returns: the same text, pre-processed
		"""
		#############################################################################
		# TODO: Preprocess the text into a desired format.                          #
		# NOTE: This method is completely OPTIONAL. If it is not helpful to your    #
		# implementation to do any generic preprocessing, feel free to leave this   #
		# method unmodified.                                                        #
		#############################################################################

		# Split sentence by word and convert to list
		# Lowercase all letters/words
		# normed_line = ""
		# for word in text.split():
		# 	word = word.lower()
		# 	normed_line += word + " "
		# return normed_line.strip()
		return text



		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################

		return text

	def toLower(self, text):
		# Split sentence by word and convert to list
		# Lowercase all letters/words
		normed_line = ""
		for word in text.split():
			word = word.lower()
			normed_line += word + " "
		return normed_line.strip()


	def normalize(self, text):
		getVals = list([val for val in text if val.isalpha() or val.isnumeric() or val == ' ' or val == ','])
		result = "".join(getVals)
		return result

	def levenshtein(self, s, t):
		if s == t:
			return 0
		if len(s) == 0:
			return len(t)
		if len(t) == 0:
			return len(s)

		v0 = list(range(len(t) + 1))
		v1 = [None] * (len(t) + 1)

		for i in range(len(s)):
			v1[0] = i + 1
			for j in range(len(t)):
				cost = 0 if s[i] == t[j] else 2
				v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
			for j in range(len(v0)):
				v0[j] = v1[j]

		return v1[len(t)]

	def extract_titles(self, preprocessed_input):
		"""Extract potential movie titles from a line of pre-processed text.
		Given an input text which has been pre-processed with preprocess(),
		this method should return a list of movie titles that are potentially in the text.
		- If there are no movie titles in the text, return an empty list.
		- If there is exactly one movie title in the text, return a list
		containing just that one movie title.
		- If there are multiple movie titles in the text, return a list
		of all movie titles you've extracted from the text.
		Example:
		  potential_titles = chatbot.extract_titles(chatbot.preprocess('I liked "The Notebook" a lot.'))
		  print(potential_titles) // prints ["The Notebook"]
		:param preprocessed_input: a user-supplied line of text that has been pre-processed with preprocess()
		:returns: list of movie titles that are potentially in the text
		"""
		pattern = '"([^"]*)"'
		matches = re.findall(pattern, preprocessed_input)
		return matches

	#Takes a found movie given by user and adds to movie->year dict.
	#If year is not given, year = -1
	def matchMovieToYear(self, input_movie):
		input_movie_year = {} # {original movie title : [fixed title, year]}
		movie_year = [] # [fixed title, year]
		year = self.checkYearHelper(input_movie)
		fixed_movie = input_movie
		if year != None:
			fixed_movie = input_movie.replace(year, '')  #remove year
			fixed_movie = fixed_movie.strip()
		else:
			year = -1
		movie_year.append(self.fixedTitles(fixed_movie))  #Rearranges first article word
		movie_year.append(year)
		input_movie_year[input_movie] = movie_year
		return input_movie_year


	def checkYearHelper(self, input_movie):
		"""
		Checks if a year is given by user. Returns year.
		"""
		year = None
		p = '(\([0-9]{4}\))'
		c = re.search(p, input_movie)
		if c != None:
			year = c.group(1)
		return year

	def fixedTitles(self, title):
		"""
		Removes the first article word ("a", "an", "the") from title.
		Returns the title without the first article
		"""
		words = title.split(' ', 1)
		if words[0] in self.articles:
			title = words[1] + ", " + words[0]
		return title

	def checkForeign(self, input_movie):
		title = None
		p = '(\([A-Za-z, ]+\))'
		c = re.search(p, input_movie)
		if c != None:
			title = c.group(1)
		return title

	def find_movies_by_title(self, title):
		""" Given a movie title, return a list of indices of matching movies.
		- If no movies are found that match the given title, return an empty list.
		- If multiple movies are found that match the given title, return a list
		containing all of the indices of these matching movies.
		- If exactly one movie is found that matches the given title, return a list
		that contains the index of that matching movie.
		Example:
		  ids = chatbot.find_movies_by_title('Titanic')
		  print(ids) // prints [1359, 1953]
		:param title: a string containing a movie title
		:returns: a list of indices of matching movies
		"""
		input_title = self.matchMovieToYear(title) #Returns {title : [fixed title, year]}

		title_low = self.toLower(title)
		input_low = self.matchMovieToYear(title_low)
		token_title = input_low[title_low][0].split()
		n = len(token_title)

		movies = []
		for i,t in enumerate(self.titles):
			t_orig = self.matchMovieToYear(t[0])

			t_low = self.toLower(t[0])
			t_title = self.matchMovieToYear(t_low)
			token_t = t_title[t_low][0].split()

			t_norm = self.normalize(t_title[t_low][0])
			t_norm = t_norm.split()

			if any(token_title == token_t[i:i + n] for i in range(len(token_t)-n + 1)) or any(token_title == t_norm[i:i + n] for i in range(len(t_norm)-n + 1)):
				if input_low[title_low][1] == t_title[t_low][1]:
					movies.append(i)
				elif input_low[title_low][1] == -1:
					movies.append(i)
			elif input_title[title][0] == t_orig[t[0]][0]:
				if input_title[title][1] == t_orig[t[0]][1]:
					movies.append(i)
				elif input_title[title][1] == -1:
					movies.append(i)
			elif title == t[0]:
				t_year = self.checkYearHelper(t[0])
				if input_title[title][1] == t_year:
					movies.append(i)
				elif input_title[title][1] == -1:
					movies.append(i)

			elif self.checkForeign(t_low) != None:
				foreign = self.checkForeign(t_low)[1:-1]
				token_foreign = foreign.split()

				fixed_foreign = self.fixedTitles(title_low)
				fixed_token = fixed_foreign.split()
				# print(foreign)

				if any(fixed_token == token_foreign[i:i + n] for i in range(len(token_t)-n + 1)) or any(token_title == t_norm[i:i + n] for i in range(len(t_norm)-n + 1)):
					movies.append(i)

		return movies


	def removeTitleHelper(self, input_text):
		"""
		Removes title from input_text and returns input_text without the title
		"""
		patterns = '(".*")'
		input_text = re.sub(patterns, '', input_text)
		return input_text

	def removePunctuationHelper(self, input_text):
		"""
		Removes punctuation from input_text and returns input_text without any punctuation
		"""
		patterns = '([\.,!\?;:])'
		input_text = re.sub(patterns, '', input_text)
		return input_text

	def markPunctuationHelper(self, input_text):
		"""
		Repalces punctuation from input_text with 'PUNC'
		"""
		patterns = '([\.,!\?;:])'
		input_text = re.sub(patterns, ' PUNC ', input_text)
		return input_text

	def extract_sentiment(self, preprocessed_input):
		"""Extract a sentiment rating from a line of pre-processed text.
		You should return -1 if the sentiment of the text is negative, 0 if the
		sentiment of the text is neutral (no sentiment detected), or +1 if the
		sentiment of the text is positive.
		As an optional creative extension, return -2 if the sentiment of the text
		is super negative and +2 if the sentiment of the text is super positive.
		Example:
		  sentiment = chatbot.extract_sentiment(chatbot.preprocess('I liked "The Titanic"'))
		  print(sentiment) // prints 1
		:param preprocessed_input: a user-supplied line of text that has been pre-processed with preprocess()
		:returns: a numerical value for the sentiment of the text
		"""
		
		sentiment = 0
		negated = False
		intensifier = False

		# remove titles from input
		input_text = self.removeTitleHelper(preprocessed_input)
		input_text = self.markPunctuationHelper(input_text)
		input_list = input_text.split()
		# print('START:\n ', input_list)


		for word in input_list:
			# set negated boolean and intensifier boolean
			if word == 'PUNC':
				negated = False
				intensifier = False
			elif self.checkNegation(word) == True:
				negated = True
			elif self.checkIntensifier(word) == True:
				intensifier = True

			# get sentiment value of the word
			sentiment_val = self.checkCreativeLexicon(word)

			# check if the sentiment is supposed to be negated
			if negated == True:
				sentiment_val *= -1

			if intensifier == True:
				if sentiment_val < 0:
					sentiment_val -= 1
				elif sentiment_val > 0:
					sentiment_val += 1

			print(word, ": ", sentiment_val)
			sentiment += sentiment_val

		return sentiment

		# print('FINAL:\n', input_list)


		"""sentiment = 0
		negated = False

		# remove titles from input
		input_text = self.removeTitleHelper(preprocessed_input)
		input_text = self.markPunctuationHelper(input_text)
		input_list = input_text.split()
		# print('START:\n ', input_list)

		for word in input_list:
			# set negated boolean 
			if word == 'PUNC':
				negated = False
			elif self.checkNegation(word) == True:
				negated = True

			# get sentiment value of the word
			sentiment_word = self.checkLexicon(word)
			if sentiment_word == 'pos':
				sentiment_val = 1
			elif sentiment_word == 'neg':
				sentiment_val = -1
			else:
				sentiment_val = 0

			# check if the sentiment is supposed to be negated
			if negated == True:
				sentiment_val *= -1
				word += '_NEG'
				print('negated word: ', word)

			sentiment += sentiment_val

		# print('FINAL:\n', input_list)


		if sentiment > 0:
			return 1
		elif sentiment < 0:
			return -1
		else:
			return 0"""

	def checkNegation(self, word):
		""" 
		Returns True if the word is a negation word.
		Returns False if the word is not a negation word.
		"""
		patterns = [
			'(.*n\'t)',
			'(^not$)',
			'(^no$)',
			'(^nothing$)',
			'(^never$)',
			'(^none$)',
			'(^nowhere$)',
		]

		word = self.removePunctuationHelper(word)
		for p in patterns:
			if re.fullmatch(p, word) != None:
				return True

		return False

	def checkLexicon(self, word):
		""" 
		Checks if the sentiment lexicon contains the word (or other forms of the word, i.e. singular,
		present tense, etc.) and 
		- returns 'pos' for positive words
		- returns 'neg' for negative words
		- returns 'none' for words not in the sentiment lexicon
		"""
		word = self.removePunctuationHelper(word)
		forms = self.getWordForms(word)
		value = 'none'
		forms.append(word)

		for form in forms:
			if form in self.sentiment:
				value = self.sentiment[form]

		return value

	def getWordForms(self, word):
		forms = []
		forms.append(word)

		# check last letter
		if word[-1:] == "s" or word[-1:] == "d":
			forms.append(word[0:len(word)-1]) # likes -> like, liked -> like

		# check last 2 letters
		if word[-2:] == "ed":
			forms.append(word[0:len(word)-2]) # enjoyed -> enjoy

		# check last 3 letters
		if word[-3:] == "ing":
			forms.append(word[0:len(word)-3]) # enjoying -> enjoy
			forms.append(word[0:len(word)-3] + "e")

		forms.append(word + "s") # like -> likes
		forms.append(word + "y") # cheer -> cheery
		forms.append(word + "d") # like -> liked
		forms.append(word + "ed") # enjoy -> enjoyed

		# FIX THESE
		forms.append(word[0:len(word)-1] + "ied") # cry -> cried
		forms.append(word[0:len(word)-1] + "ies") # cry -> cries
		forms.append(word[0:len(word)-1] + "ing") # like -> liking
		forms.append(word + word[-1:] + "ed") # sob -> sobbed
		forms.append(word + word[-1:] + "ing") # sob -> sobbing

		return forms

	def checkCreativeLexicon(self, word):
		word = self.removePunctuationHelper(word)
		lexicon_val = self.checkLexicon(word)
		if lexicon_val == 'pos':
				sentiment_val = 1
		elif lexicon_val == 'neg':
			sentiment_val = -1
		else:
			sentiment_val = 0

		extra_pos = self.checkExtraPositive(word)
		extra_neg = self.checkExtraNegative(word)

		if extra_pos == True:
			sentiment_val += 1
		elif extra_neg == True:
			sentiment_val -= 1

		return sentiment_val

	def checkExtraPositive(self, word):
		""" 
		Returns True if the word is an extra positive word
		Returns False if the word is not an extra positive word
		"""
		patterns = [
			'(^love$)',
			'(^adore$)',
			'(^better$)',
			'(^best$)',
			'(^cherish$)'
			'(^amazing$)',
			'(^fantastic$)',
			'(^terrific$)',
			'(^wonderful$)',
			'(^ideal$)',
			'(^fabulous$)',
			'(^triumph$)',
			'(^brilliant$)',
			'(^hilarious$)',
			'(^great$)',
			'(^acclaim$)',
			'(^outstanding$)',
			'(^remarkable$)',
			'(^outstanding$)',
			'(^gorgeous$)',
			'(^excellent$)',
			'(^magnificent$)',
			'(^marvelous$)',
			'(^perfect$)',
			'(^tremendous$)',
			'(^splendid$)'
		]

		word = self.removePunctuationHelper(word)
		forms = self.getWordForms(word)
		for form in forms:
			for p in patterns:
				if re.fullmatch(p, form) != None:
					return True

		return False

	def checkExtraNegative(self, word):
		""" 
		Returns True if the word is an extra negative word
		Returns False if the word is not an extra negative word
		"""
		patterns = [
			'(^hate$)',
			'(^detest$)',
			'(^worse$)',
			'(^worst$)',
			'(^terrible$)',
			'(^horrible$)',
			'(^awful$)',
			'(^failure$)',
			'(^dreadful$)',
			'(^disappoint$)',
			'(^unbearable$)',
			'(^poor$)',
			'(^pathetic$)',
			'(^stupid$)',
			'(^repulsive$)',
			'(^shameful$)'
		]

		word = self.removePunctuationHelper(word)
		forms = self.getWordForms(word)
		for form in forms:
			for p in patterns:
				# print("comparing ", form, " to ", p)
				if re.fullmatch(p, form) != None:
					return True

		return False


	def creative_extract_sentiment(self, preprocessed_input):
		"""Extract a sentiment rating from a line of pre-processed text.
		You should return -1 if the sentiment of the text is negative, 0 if the
		sentiment of the text is neutral (no sentiment detected), or +1 if the
		sentiment of the text is positive.
		As an optional creative extension, return -2 if the sentiment of the text
		is super negative and +2 if the sentiment of the text is super positive.
		Example:
		  sentiment = chatbot.extract_sentiment(chatbot.preprocess('I liked "The Titanic"'))
		  print(sentiment) // prints 1
		:param preprocessed_input: a user-supplied line of text that has been pre-processed with preprocess()
		:returns: a numerical value for the sentiment of the text
		"""

		sentiment = 0
		negated = False
		intensifier = False

		# remove titles from input
		input_text = self.removeTitleHelper(preprocessed_input)
		input_text = self.markPunctuationHelper(input_text)
		input_list = input_text.split()
		# print('START:\n ', input_list)


		for word in input_list:
			# set negated boolean and intensifier boolean
			if word == 'PUNC':
				negated = False
				intensifier = False
			elif self.checkNegation(word) == True:
				negated = True
			elif self.checkIntensifier(word) == True:
				intensifier = True

			# get sentiment value of the word
			sentiment_val = self.checkCreativeLexicon(word)

			# check if the sentiment is supposed to be negated
			if negated == True:
				sentiment_val *= -1

			if intensifier == True:
				if sentiment_val < 0:
					sentiment_val -= 1
				elif sentiment_val > 0:
					sentiment_val += 1

			print(word, ": ", sentiment_val)
			sentiment += sentiment_val

		# print('FINAL:\n', input_list)

		return sentiment

	def checkIntensifier(self, word):
		""" 
		Returns True if the word is an intensifier word (eg. really, very, extremely, super).
		Returns False if the word is not an intensifier word.
		"""
		patterns = [
			'(^really$)',
			'(^very$)',
			'(^super$)',
			'(^extremely$)',
			'(^rather$)',
			'(^so$)',
			'(^absolutely$)',
			'(^completely$)',
			'(^highly$)',
			'(^too$)',
			'(^totally$)',
			'(^utterly$)'
		]

		word = self.removePunctuationHelper(word)
		for p in patterns:
			if re.fullmatch(p, word) != None:
				return True

		return False


	def markTitleHelper(self, input_text):
		"""
		Removes punctuation from input_text and returns input_text without any punctuation
		"""
		patterns = '"([^"]*)"'
		input_text = re.sub(patterns, 'TITLE_', input_text)
		return input_text


	def extract_sentiment_for_movies(self, preprocessed_input):
		"""Creative Feature: Extracts the sentiments from a line of pre-processed text
		that may contain multiple movies. Note that the sentiments toward
		the movies may be different.
		You should use the same sentiment values as extract_sentiment, described above.
		Hint: feel free to call previously defined functions to implement this.
		Example:
		  sentiments = chatbot.extract_sentiment_for_text(
						   chatbot.preprocess('I liked both "Titanic (1997)" and "Ex Machina".'))
		  print(sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]
		:param preprocessed_input: a user-supplied line of text that has been pre-processed with preprocess()
		:returns: a list of tuples, where the first item in the tuple is a movie title,
		  and the second is the sentiment in the text toward that movie
		"""
		sentiment_dict = {}
		title_dict = {}

		print(preprocessed_input)

		# make dict index of movie in sentence -> movie title
		# ex. I didn't like either "I, Robot" or "Ex Machina", but "The Notebook" was pretty good.
		# 0 -> "I, Robot"
		# 1 -> "Ex Machina"
		# 2 -> The Notebook
		extracted_movies = self.extract_titles(preprocessed_input)
		for i in range(len(extracted_movies)):
			title_dict[i] = extracted_movies[i]

		# ex. I didn't like either TITLE_ or TITLE_, but TITLE_ was pretty good.
		input_text = self.markTitleHelper(preprocessed_input)
		"""
		input_list = input_text.split()
		movie_index = 0
		for i in range(len(input_list))
			if input_list[i] == 'TITLE_':
				input_list[i] += movie_index
				movie_index += 1
		"""
		print(input_text)
		chunk_list = re.split(r'but|\.|;', input_text)
		print(chunk_list)

		# REEVALUATE HERE
		"""
		for chunk in chunk_list:
			sentiment = self.extract_sentiment(chunk)
			sentiment_dict[] = sentiment
	"""


		"""
		for i in range(len(extracted_movies))
		found_movies = []
		for movie in extracted_movies:
			title = self.buildUserDict(movie)
			found_movies.extend(self.find_movies_by_title(title))
	



		pass
		"""

	def find_movies_closest_to_title(self, title, max_distance=3):
		"""Creative Feature: Given a potentially misspelled movie title,
		return a list of the movies in the dataset whose titles have the least edit distance
		from the provided title, and with edit distance at most max_distance.
		- If no movies have titles within max_distance of the provided title, return an empty list.
		- Otherwise, if there's a movie closer in edit distance to the given title
		  than all other movies, return a 1-element list containing its index.
		- If there is a tie for closest movie, return a list with the indices of all movies
		  tying for minimum edit distance to the given movie.
		Example:
		  chatbot.find_movies_closest_to_title("Sleeping Beaty") # should return [1656]
		:param title: a potentially misspelled title
		:param max_distance: the maximum edit distance to search for
		:returns: a list of movie indices with titles closest to the given title and within edit distance max_distance
		"""
		title_low = self.toLower(title)
		input_low = self.matchMovieToYear(title_low)
		closest = max_distance

		movies = []
		for i,t in enumerate(self.titles):

			t_low = self.toLower(t[0])
			t_title = self.matchMovieToYear(t_low)

			dist = self.levenshtein(input_low[title_low][0], t_title[t_low][0])
			if dist <= closest:
				print(dist)
				if dist < closest:
					movies = []
					closest = dist
				movies.append(i)

		return movies

	def disambiguate(self, clarification, candidates):
		"""Creative Feature: Given a list of movies that the user could be talking about
		(represented as indices), and a string given by the user as clarification
		(eg. in response to your bot saying "Which movie did you mean: Titanic (1953)
		or Titanic (1997)?"), use the clarification to narrow down the list and return
		a smaller list of candidates (hopefully just 1!)
		- If the clarification uniquely identifies one of the movies, this should return a 1-element
		list with the index of that movie.
		- If it's unclear which movie the user means by the clarification, it should return a list
		with the indices it could be referring to (to continue the disambiguation dialogue).
		Example:
		  chatbot.disambiguate("1997", [1359, 2716]) should return [1359]
		:param clarification: user input intended to disambiguate between the given movies
		:param candidates: a list of movie indices
		:returns: a list of indices corresponding to the movies identified by the clarification
		"""
		numbers = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eight', 'ninth', 'tenth']
		suggest = []


		for word in clarification.split():
			for movie in candidates:
				if word.isnumeric():
					if int(word) == movie:
						suggest.append(movie)
					elif int(word) < len(candidates)-1:
						suggest.append(candidates[int(word)-1])
					elif int(word) == int(self.checkYearHelper(self.titles[movie][0])[1:-1]):
						suggest.append(movie)
				elif word in numbers:
					suggest.append(candidates[numbers.index(word)])
		if len(suggest) == 0:
			suggest.extend(self.find_movies_by_title(clarification))

		return suggest

	#############################################################################
	# 3. Movie Recommendation helper functions                                  #
	#############################################################################

	@staticmethod
	def binarize(ratings, threshold=2.5):
		"""Return a binarized version of the given matrix.
		To binarize a matrix, replace all entries above the threshold with 1.
		and replace all entries at or below the threshold with a -1.
		Entries whose values are 0 represent null values and should remain at 0.
		Note that this method is intentionally made static, as you shouldn't use any
		attributes of Chatbot like self.ratings in this method.
		:param ratings: a (num_movies x num_users) matrix of user ratings, from 0.5 to 5.0
		:param threshold: Numerical rating above which ratings are considered positive
		:returns: a binarized version of the movie-rating matrix
		"""
		#############################################################################
		# TODO: Binarize the supplied ratings matrix. Do not use the self.ratings   #
		# matrix directly in this function.                                         #
		#############################################################################

		# The starter code returns a new matrix shaped like ratings but full of zeros.
		# binarized_ratings = np.zeros_like(ratings)
		binarized_ratings = ratings
		binarized_ratings[binarized_ratings == 0] = 10
		binarized_ratings[binarized_ratings < 3.0] = -1
		binarized_ratings[binarized_ratings == 10] = 0
		binarized_ratings[binarized_ratings >= 3.0] = 1
		

		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return binarized_ratings

	def similarity(self, u, v):
		"""Calculate the cosine similarity between two vectors.
		You may assume that the two arguments have the same shape.
		:param u: one vector, as a 1D numpy array
		:param v: another vector, as a 1D numpy array
		:returns: the cosine similarity between the two vectors
		"""
		#############################################################################
		# TODO: Compute cosine similarity between the two vectors.
		#############################################################################
		sim = 0
		# if np.linalg.norm(u) * np.linalg.norm(v) != 0:
		# 	sim == np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
		if np.linalg.norm(u) != 0 and np.linalg.norm(v) != 0:
			sim = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return sim



	# Creates and returns sparse vector of user sentiments to given movies
	def createUserMatrix(self):
		user_matrix = np.zeros((self.ratings.shape[0], 1))
		for key, value in self.userSentiment.items():
			user_matrix[key] = value
		return user_matrix


	def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
		"""Generate a list of indices of movies to recommend using collaborative filtering.
		You should return a collection of `k` indices of movies recommendations.
		As a precondition, user_ratings and ratings_matrix are both binarized.
		Remember to exclude movies the user has already rated!
		Please do not use self.ratings directly in this method.
		:param user_ratings: a binarized 1D numpy array of the user's movie ratings
		:param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
		  `ratings_matrix[i, j]` is the rating for movie i by user j
		:param k: the number of recommendations to generate
		:param creative: whether the chatbot is in creative mode
		:returns: a list of k movie indices corresponding to movies in ratings_matrix,
		  in descending order of recommendation
		"""

		#######################################################################################
		# TODO: Implement a recommendation function that takes a vector user_ratings          #
		# and matrix ratings_matrix and outputs a list of movies recommended by the chatbot.  #
		# Do not use the self.ratings matrix directly in this function.                       #
		#                                                                                     #
		# For starter mode, you should use item-item collaborative filtering                  #
		# with cosine similarity, no mean-centering, and no normalization of scores.          #
		#######################################################################################

		# Populate this list with k movie indices to recommend to the user.
		recommendations = []
		rec = {} # movie index -> scores
		user_pref = {}
		for index, row in enumerate(user_ratings):
			if user_ratings[index] != 0:
				user_pref[index] = user_ratings[index]

		for index, row in enumerate(ratings_matrix):
			if index not in user_pref:
				score = 0
				for key,value in user_pref.items():
					sim = self.similarity(ratings_matrix[key], row)
					score += (sim * value)
				rec[index] = score
		recommendations = sorted(rec, key=rec.get, reverse=True)[:k]




		# Ask for 5 movies -> fill in sentiment for those indexes in sparse user/movie vector
		# Cosine sim each missing movie with rows of 5 movies that user gave input on
		# Compute given user rating * sim = score for each given movie
		# Store in dict score -> index of movie  ----> Keep highest k scores


		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return recommendations

	#############################################################################
	# 4. Debug info                                                             #
	#############################################################################

	def debug(self, line):
		"""Return debug information as a string for the line string from the REPL"""
		# Pass the debug information that you may think is important for your
		# evaluators
		debug_info = 'debug info'
		return debug_info

	#############################################################################
	# 5. Write a description for your chatbot here!                             #
	#############################################################################
	def intro(self):
		"""Return a string to use as your chatbot's description for the user.
		Consider adding to this description any information about what your chatbot
		can do and how the user can interact with it.
		"""
		return """
		Tired of watching trailer after trailer in search of the perfect movie?
		Search no further! Just have a short chat with PopcornPal, talking about some movies you've
		liked or disliked, and PopcornPal will generate a personalized movie recommendation for you
		based on your very own movie tastes and preferences!

		(Note: Please make sure to put the movie titles in quotation marks.)
		"""


if __name__ == '__main__':
	print('To run your chatbot in an interactive loop from the command line, run:')
	print('    python3 repl.py')