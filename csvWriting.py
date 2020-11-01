import csv
import os
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import re
leagueID = input("Enter League ID: ")
league_name = input ("League Name: ")
season = input("Season: ")

#gets the total numver of players in a given season
def get_numberofowners() :
	owners_url = 'https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/owners'
	owners_page = urlopen(owners_url)
	owners_html = owners_page.read()
	owners_page.close()
	owners_soup = bs(owners_html, 'html.parser')
	number_of_owners = len(owners_soup.find_all('tr', class_ = re.compile('team-')))
	return number_of_owners

number_of_owners = get_numberofowners() #number of teams in the league

#gets the team id number from a player name, currently unused
def getteamid(player) :
	url = 'https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/owners'
	page = urlopen(url)
	html = page.read()
	page.close()
	soup = bs(html, 'html.parser')
	teamWraps = soup.find_all('tr', class_ = re.compile('team-'))
	for teamWrap in teamWraps :
		if teamWrap.find('td', class_ = 'teamOwnerName').text.strip() == player :
			return teamWrap.attrs['class'][0].split('-')[1]

#teams that don't fill all their starting roster spots for a week will have a longer bench
#the more roster spots left unfilled, the more bench players that team will have
#this method gets the teamid of the team with the longest bench for the week as well as the length of their bench
def get_longest_bench(week) :
	longest_bench_data = [0, 0]
	for i in range (1, number_of_owners + 1) :
		page = urlopen('https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/teamgamecenter?teamId=' + str(i) + '&week=' + str(week))
		soup = bs(page.read(), 'html.parser')
		page.close()
		bench_length = len(soup.find('div', id = 'tableWrapBN-1').find_all('td', class_ = 'playerNameAndInfo'))
		if(bench_length > longest_bench_data[0]) :
			longest_bench_data = [bench_length, i]

	return longest_bench_data

#generates the header for the csv file for the week
#different weeks can have different headers if players do not fill all their starting roster spots
def get_header(week, longest_bench_teamID) :
	url = "https://fantasy.nfl.com/league/" + leagueID + "/history/" + season + "/teamgamecenter?teamId=" +str(longest_bench_teamID) + "&week=" + str(week)
	page = urlopen(url)
	html = page.read()
	page.close()
	soup = bs(html, 'html.parser') #uses the page of the teamID with the longest bench to generate the header

	position_tags = [tag.find('span').text for tag in soup.find('div', id = 'teamMatchupBoxScore').find('div', class_ = 'teamWrap teamWrap-1').find_all('tr', class_ = re.compile('player-'))]
	#position tags are the label for each starting roster spot. different leagues can have different configurations for their starting rosters

	header = [] #csv file header

	#adds the position tags to the header. each tag is followed by a column to record the player's points for the week
	for i in range(len(position_tags)) :
		header.append(position_tags[i])
		header.append('Points')

	header = ['Owner',  'Rank'] + header + ['Total', 'Opponent', 'Opponent Total']

	return header

#gets one row of the csv file
#each row is the weekly data for one team in the league
def getrow(teamId, week, longest_bench) : 

	#loads gamecenter page as soup
	page = urlopen('https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/teamgamecenter?teamId=' + teamId + '&week=' + week)
	soup = bs(page.read(), 'html.parser')
	page.close()

	owner = soup.find('a', class_ = re.compile('userName userId')).text #username of the team owner

	starters = soup.find('div', id = 'tableWrap-1').find_all('td', class_ = 'playerNameAndInfo')
	starters = [starter.text for starter in starters]
	bench = soup.find('div', id = 'tableWrapBN-1').find_all('td', class_ = 'playerNameAndInfo')
	bench = [benchplayer.text for benchplayer in bench]

	#in order to keep the row properly aligned, bench spots that are filled by another team
	#but not by this team are filled with a -
	while len(bench) < longest_bench: 
		bench.append('-')

	roster = starters + bench #every player on the team roster, in the order they are listed in game center, for the given week

	player_totals = soup.find('div', id = 'teamMatchupBoxScore').find('div', class_ = 'teamWrap teamWrap-1').find_all('td', class_ = re.compile("statTotal"))
	player_totals = [player.text for player in player_totals] #point totals for each player with indecies which correspond to that player's index in roster

	teamtotals = soup.findAll('div', class_ = re.compile('teamTotal teamId-')) #the team's total points for the week
	ranktext = soup.find('span', class_ = re.compile('teamRank teamId-')).text
	rank = ranktext[ranktext.index('(') + 1: ranktext.index(')')]#the team's rank in the standings

	rosterandtotals = [] #alternating player names and their corresponding weekly point totals
	for i in range(len(roster)) :
		 rosterandtotals.append(roster[i])

		 #checks if there is a point total coressponding to the player, if not that spot is filled with a -
		 try:
		 	rosterandtotals.append(player_totals[i])
		 except:
		 	rosterandtotals.append('-')

	#try except statement is for the situation where the league member would not have an opponent for the week
	#in this case the Opponent and Opponent Total columns are filled with -
	try:
		completed_row = [owner, rank] + rosterandtotals + [teamtotals[0].text, soup.find('div', class_ = 'teamWrap teamWrap-2').find('a', re.compile('userName userId')).text, teamtotals[1].text]
	except:
		completed_row = [owner, rank] + rosterandtotals + [teamtotals[0].text, '-', '-']

	return completed_row


#checks if a directory exists with that team name. If it doesn't it asks the user if it wants to create a new directory
#to store the league data in.
if not os.path.isdir('./' + league_name + '-League-History') :
	if(input('No folder named ' + league_name + '-League-History found would you like to create a new folder with that name y/n?' ) == 'y') :
		os.mkdir('./' + league_name + '-League-History')
	else :
		exit()

path = './' + league_name + '-League-History/' + season #the path of the folder where the weekly csv files are stored

#if that folder doesn't already exist a new one is made
if not os.path.isdir(path) :
	os.mkdir(path)

#if input("Write season data to csv y/n?") == 'y' :
print(season)
page = urlopen('https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/teamgamecenter?teamId=1&week=1')
soup = bs(page.read(), 'html.parser')
page.close()
season_length = len(soup.find_all('li', class_ = re.compile('ww ww-'))) #determines how may unique csv files are created, total number of weeks in the season 

for i in range(1, season_length + 1): #iterates through each week of the season, creating a new csv file every loop
	longest_bench = get_longest_bench(i) #a list containing the length of the longest bench followed by the ID of the team with the longest bench
	header = get_header(i, longest_bench[1]) #header for the csv
	with open('./' + league_name +'-League-History/' + season + '/' + str(i) + '.csv', 'w', newline='') as f :
		writer = csv.writer(f)
		writer.writerow(header) #writes header as the first line in the new csv file
		for j in range(1, number_of_owners + 1) : #iterates through every team owner
			writer.writerow(getrow(str(j), str(i), longest_bench[0])) #writes a row for each owner in the csv
	print("Week " + str(i) + " Complete")
print("Done")
