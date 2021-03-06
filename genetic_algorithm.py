# **************************************************************************** #
#                                                                              #
#                                                                  /           #
#    Daily Fantasy Hockey Genetic Algorithm              ::       /::::::::    #
#                                                       ::       /::           #
#    By: Jarvis Nederlof <jnederlo@student.42.us.org>  ::       /::            #
#    LINECRUNCHER (L/C)                               ::       /::             #
#                                                    :::::::::/:::::::::       #
#    https://github.com/jnederlo                             /                 #
#                                                                              #
# **************************************************************************** #

import csv
import time
import random
import copy

class GeneticNHL(object):
	'''
		Genetic Algorithm class for NHL daily fantasy on Draftkings.
	'''

	def __init__(self, num_lineups, duration=60):
		self.num_lineups = num_lineups
		self.duration = duration
		self.goalies = []
		self.centers = []
		self.wingers = []
		self.defencemen = []
		self.utils = []
		self.top_150 = []

	def run(self):
		'''
			Run the program for a set duration of seconds. Longer run-time might produce higher
			projected lineups, but shouldn't take more than about 60 seconds or so.
		'''

		runtime = time.time() + self.duration
		while time.time() < runtime:
			self.get_lineups()
			self.top_150.sort(key=lambda x: x[-1], reverse=True)
			#We use 150 as the number here b/c drafkings only allows a maximum of 150 lineups in any one contest
			self.top_150 = self.top_150[:150]

	def get_lineups(self):
		'''
			This is where we create new lineups and add to top lineups (i.e. the 'lineups' class variable).
			We create 10 lineups, rank them and mate the top 3 together,
			then we take the offspring and mate with a randomly selected lineup from the top lineups.
		'''

		#generate 10 new lineups
		new_lineups = [self.generate_lineup() for _ in range(10)]

		#sort the lineups by their predicted score
		new_lineups.sort(key=lambda x: x[-1], reverse=True)

		#Add the newly created lineups to the top_150 (they will be sorted and bottom ones removed later)
		self.top_150.extend(new_lineups)

		#Mate the top 3 lineups together
		offspring_1 = self.mate_lineups(new_lineups[0], new_lineups[1])
		offspring_2 = self.mate_lineups(new_lineups[0], new_lineups[2])
		offspring_3 = self.mate_lineups(new_lineups[1], new_lineups[2])
		
		#Mate the offspring with a randomly selected lineup from the top_150 and add to top_150
		#Adding this step makes the algorithm more greedy, and produces higher projections, but can be skipped
		self.top_150.append(self.mate_lineups(offspring_1, self.top_150[random.randint(0, len(self.top_150) - 1)]))
		self.top_150.append(self.mate_lineups(offspring_2, self.top_150[random.randint(0, len(self.top_150) - 1)]))
		self.top_150.append(self.mate_lineups(offspring_3, self.top_150[random.randint(0, len(self.top_150) - 1)]))
		
		#Add the original offspring to the top_150
		self.top_150.append(offspring_1)
		self.top_150.append(offspring_2)
		self.top_150.append(offspring_3)

	def mate_lineups(self, lineup1, lineup2):
		'''
			Mate takes in two lineups, creates lists of positions from the available lineups
			and adds another random player to each position list. It then randomly selects the required
			number of positions for a new lineup from each position list, checks that the lineup is valid,
			and returns the valid lineup.
		'''

		#Create lists of all available players for each position from the two lineups plus a random player or 2
		centers = [lineup1[0], lineup1[1], lineup2[0], lineup2[1],
						self.centers[random.randint(0, len(self.centers) - 1)]]
		wingers = [lineup1[2], lineup1[3], lineup1[4], lineup2[2], lineup2[3], lineup2[4],
						self.wingers[random.randint(0, len(self.wingers) - 1)]]
		defencemen = [lineup1[5], lineup1[6], lineup2[5], lineup2[6],
						self.defencemen[random.randint(0, len(self.defencemen) - 1)]]
		goalies = [lineup1[7], lineup2[7],
						self.goalies[random.randint(0, len(self.goalies) - 1)],
						self.goalies[random.randint(0, len(self.goalies) - 1)]]
		utils = [lineup1[8], lineup2[8],
						self.utils[random.randint(0, len(self.utils) - 1)],
						self.utils[random.randint(0, len(self.utils) - 1)]]

		#Randomly grab num players from each position to fill out the new mated lineup
		def grab_players(players, num):
			avail_players = copy.deepcopy(players)
			selected_players = []
			while len(selected_players) < num:
				i = random.randint(0, len(avail_players) - 1)
				selected_players.append(avail_players[i])
				del avail_players[i]
			return selected_players

		while True:
			#Create the new lineup by selecting players from each position list
			lineup = []
			lineup.extend(grab_players(centers, 2))
			lineup.extend(grab_players(wingers, 3))
			lineup.extend(grab_players(defencemen, 2))
			lineup.extend(grab_players(goalies, 1))
			lineup.extend(grab_players(utils, 1))

			#Check if the lineup is valid (i.e. it satisfies some basic constraints)
			lineup = self.check_valid(lineup)
			#If lineup isn't valid, run mate again
			if lineup:
				return lineup

	def generate_lineup(self):
		'''
			Generate a single lineup with the correct amount of positional requirements.
			The lineup is then checked for validity and returned.
		'''

		while True:
			#add the correct number of each position to a lineup
			lineup = []
			lineup.append(self.centers[random.randint(0, len(self.centers) - 1)])
			lineup.append(self.centers[random.randint(0, len(self.centers) - 1)])
			lineup.append(self.wingers[random.randint(0, len(self.wingers) - 1)])
			lineup.append(self.wingers[random.randint(0, len(self.wingers) - 1)])
			lineup.append(self.wingers[random.randint(0, len(self.wingers) - 1)])
			lineup.append(self.defencemen[random.randint(0, len(self.defencemen) - 1)])
			lineup.append(self.defencemen[random.randint(0, len(self.defencemen) - 1)])
			lineup.append(self.goalies[random.randint(0, len(self.goalies) - 1)])
			lineup.append(self.utils[random.randint(0, len(self.utils) - 1)])

			#Check if the lineup is valid (i.e. it satisfies some basic constraints)
			lineup = self.check_valid(lineup)
			if lineup:
				return lineup

	def check_valid(self, lineup):
		'''
			Valid lineups remain under the $50,000 salary cap,
			have a minimum of 3 teams, and 9 total players.
			Every lineup already satisfires the positional constraints when created.
		'''

		#calculate the total projection of the lineup based on player averages
		projection = round(sum(player['avePoints'] for player in lineup), 2)
		#calculate the total salary used for the lineup
		salary = sum(player['salary'] for player in lineup)
		#get a list of the unique teams on the lineup
		teams = set([player['teamAbbrev'] for player in lineup])
		#remove duplicate players from lineup and count how many players
		num_players = len(set(player['name'] for player in lineup))

		#check the salary cap, at least 3 teams, and at least 9 unique players
		if salary < 50000 and len(teams) >= 3 and num_players == 9:
			#add the salary and the projection to the lineup of players and return the lineup
			lineup.extend((salary, projection))
			return lineup
		return False

	def load_roster(self):
		'''
			Load in the roster of players from the DraftKings DKSalaries CSV download.
			Removes players with an average of 0 points, indicating they are probably not active.
			The user should do additional filters to remove players who are not starting, injured, or
			not active. The user should also replace the average points with their own projections.
		'''

		with open("./DKSalaries.csv") as f:
			reader = csv.reader(f)

			#skip past the instructions and header in file
			for _ in range(8):
				next(reader)

			#grab the the player information for each player
			for row in reader:
				player = {}
				player['name'] = row[11]
				player['position'] = row[14][0]
				player['salary'] = int(row[15])
				player['teamAbbrev'] = row[17]
				player['avePoints'] = float(row[18])

				#append each player dictionary to their corresponding position list
				#only grab players who's average points are not 0 (i.e. they are active)
				if player['avePoints'] != 0:
					if player['position'] == 'G':
						self.goalies.append(player)
					elif player['position'] == 'C':
						self.centers.append(player)
					elif player['position'] == 'W':
						self.wingers.append(player)
					elif player['position'] == 'D':
						self.defencemen.append(player)

					#append the player to the utility position list if not a goalie
					if player['position'] != 'G':
						self.utils.append(player)

	def save_file(self):
		'''
			Trim the lineup to include only the player name + id, and save CSV files.
			One CSV will have the salary and projection included, and one will not.
			The one without the salary and projection can be uploaded directly to DraftKings.
		'''

		#trim the lineups to include only the player name + id, salary and projection
		lineups = [[player['name'] if isinstance(player, dict) else player for player in lineup]
						for lineup in self.top_150]

		#remove the duplicate lineups
		lineups = [lineups[i] for i in range(self.num_lineups - 1) if lineups[i] != lineups[i+1]]

		#remove the salary and projection so can upload lineups to DraftKings
		lineups_for_upload = [lineup[:9] for lineup in lineups]

		header = ['C', 'C', 'W', 'W', 'W', 'D', 'D', 'G', 'UTIL', 'Salary', 'Projection']
		header_for_upload = ['C', 'C', 'W', 'W', 'W', 'D', 'D', 'G', 'UTIL']

		with open("./lineups.csv", 'w') as f:
			writer = csv.writer(f)
			writer.writerow(header)
			writer.writerows(lineups)

		with open("./lineups_for_upload.csv", 'w') as f:
			writer = csv.writer(f)
			writer.writerow(header_for_upload)
			writer.writerows(lineups_for_upload)

if __name__ == "__main__":
	#specify the number of lineups to generate (from 1 to 150), and how long to let the program run for (optional)
	#the default duration is 60 seconds.
	#I use runtime instead of # of mutations b/c I think it is more intuitive.
	g = GeneticNHL(num_lineups=150)
	g.load_roster()
	g.run()
	g.save_file()
