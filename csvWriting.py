import csv
import os
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import re
#player = input("Player: ")
#compare_weeks = [input("Compare Week: "), input('And Week:')]



def getTeamId(player, season) :
	url = 'https://fantasy.nfl.com/league/4007290/history/' + season + '/owners'
	page = urlopen(url)
	html = page.read()
	page.close()
	soup = bs(html, 'html.parser')
	teamWraps = soup.find_all('tr', class_ = re.compile('team-'))
	for teamWrap in teamWraps :
		if teamWrap.find('td', class_ = 'teamOwnerName').text.strip() == player :
			return teamWrap.attrs['class'][0].split('-')[1]

def compareRoster(teamId, season, start, end) :
	start_roster = getRoster(teamId, season, start)
	end_roster = getRoster(teamId, season, end)

	similar_count = 0
	for player in end_roster :
		if player in start_roster :
			similar_count += 1

	return similar_count

def getRoster(teamId, season, week) :
	page = urlopen('https://fantasy.nfl.com/league/4007290/history/' + season + '/teamgamecenter?teamId=' + teamId + '&week=' + week)
	soup = bs(page.read(), 'html.parser')
	page.close()
	owner = soup.find('a', class_ = re.compile('userName userId')).text
	starters = soup.find('div', id = 'tableWrap-1').find_all('td', class_ = 'playerNameAndInfo')
	starters = [starter.text for starter in starters]
	bench = soup.find('div', id = 'tableWrapBN-1').find_all('td', class_ = 'playerNameAndInfo')
	bench = [benchplayer.text for benchplayer in bench]

	player_totals = soup.find('div', id = 'teamMatchupBoxScore').find('div', class_ = 'teamWrap teamWrap-1').find_all('td', class_ = re.compile("statTotal"))
	player_totals = [player.text for player in player_totals]

	roster = starters + bench
	rosterandtotals = []
	teamtotals = soup.findAll('div', class_ = re.compile('teamTotal teamId-'))
	ranktext = soup.find('span', class_ = re.compile('teamRank teamId-')).text
	rank = ranktext[ranktext.index('(') + 1: ranktext.index(')')]
	for i in range(len(roster)) :
	 	rosterandtotals.append(roster[i])
	 	rosterandtotals.append(player_totals[i])

	try:
		rosterandtotals = [owner, rank] + rosterandtotals + [teamtotals[0].text, soup.find('div', class_ = 'teamWrap teamWrap-2').find('a', re.compile('userName userId')).text, teamtotals[1].text]
	except:
		rosterandtotals = [owner, rank] + rosterandtotals + [teamtotals[0].text, 'N/A', 'N/A']
	return rosterandtotals






season = input("Season: ")
path = './FlatCats-League-History/' + season

if !os.path.isdir(path) :
	os.mkdir(path)

if input("Write season data to csv y/n?") == 'y' :
	#converting url to soup
url = "https://fantasy.nfl.com/league/4007290/history/" + season + "/teamgamecenter?teamId=1&week=1"
page = urlopen(url)
html = page.read()
page.close()
soup = bs(html, 'html.parser')

season_length = len(soup.find_all('li', class_ = re.compile('ww ww-')))

owners_url = 'https://fantasy.nfl.com/league/4007290/history/' + season + '/owners'
owners_page = urlopen(owners_url)
owners_html = owners_page.read()
owners_page.close()
owners_soup = bs(owners_html, 'html.parser')
number_of_owners = len(owners_soup.find_all('tr', class_ = re.compile('team-')))
print(number_of_owners)

position_tags = [tag.text for tag in soup.find('div', id = 'teamMatchupBoxScore').find('div', class_ = 'teamWrap teamWrap-1').find_all('span', class_ = 'final')]
header = []

for i in range(len(position_tags)) :
	header.append(position_tags[i])
	header.append('Points')

header = ['Owner',  'Rank'] + header + ['Total', 'Opponent', 'Opponent Total']

for i in range(1, season_length + 1) :
	with open('./FlatCats-League-History/' + season + '/' + str(i) + '.csv', 'w', newline='') as f :
		writer = csv.writer(f)
		writer.writerow(header)
		for j in range(1, number_of_owners + 1) :
			writer.writerow(getRoster(str(j), season, str(i)))
		

	print(i)

#print('These rosters share ' + str(compareRoster(getTeamId(player, season), season, compare_weeks[0], compare_weeks[1])) + ' common players')

# url = 'https://fantasy.nfl.com/league/4007290/history/' + season + '/teamgamecenter?teamId=' + getTeamId(player, season) + '&week=' + week
# page = urlopen(url)
# html = page.read()
# page.close()
# soup = bs(html, 'html.parser')
# player_table = soup.find('div', id = 'tableWrap-1')
# names = player_table.find_all('td', class_ = 'playerNameAndInfo')
# for name in names :
# 	print (name.text)

