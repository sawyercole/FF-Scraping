import csv
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import re

season = input("Season: ")
player = input("Player: ")
compare_weeks = [input("Compare Week: "), input('And Week:')]
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

def compareRoster(teamId, Season, start, end) :
	#opens and converts the two pages to soup
	start_page = urlopen('https://fantasy.nfl.com/league/4007290/history/' + season + '/teamgamecenter?teamId=' + teamId + '&week=' + start)
	end_page = urlopen('https://fantasy.nfl.com/league/4007290/history/' + season + '/teamgamecenter?teamId=' + teamId + '&week=' + end)
	start_soup = bs(start_page.read(), 'html.parser')
	end_soup = bs(end_page.read(), 'html.parser')
	start_page.close()
	end_page.close()


	start_starters = start_soup.find('div', id = 'tableWrap-1').find_all('td', class_ = 'playerNameAndInfo')
	start_starters = [starter.text for starter in start_starters]
	start_bench = start_soup.find('div', id = 'tableWrapBN-1').find_all('td', class_ = 'playerNameAndInfo')
	start_bench = [bench.text for bench in start_bench]

	end_starters = end_soup.find('div', id = 'tableWrap-1').find_all('td', class_ = 'playerNameAndInfo')
	end_starters = [starter.text for starter in end_starters]
	end_bench = end_soup.find('div', id = 'tableWrapBN-1').find_all('td', class_ = 'playerNameAndInfo')
	end_bench = [bench.text for bench in end_bench] 

	start_roster = start_starters + start_bench
	end_roster = end_starters + end_bench

	similar_count = 0
	print(start_roster)
	print(end_roster)
	for player in end_roster :
		if player in start_roster :
			similar_count += 1

	return similar_count

print('These rosters share ' + str(compareRoster(getTeamId(player, season), season, compare_weeks[0], compare_weeks[1])) + ' common players')

# url = 'https://fantasy.nfl.com/league/4007290/history/' + season + '/teamgamecenter?teamId=' + getTeamId(player, season) + '&week=' + week
# page = urlopen(url)
# html = page.read()
# page.close()
# soup = bs(html, 'html.parser')
# player_table = soup.find('div', id = 'tableWrap-1')
# names = player_table.find_all('td', class_ = 'playerNameAndInfo')
# for name in names :
# 	print (name.text)

