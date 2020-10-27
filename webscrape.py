from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import re
season = input("Season: ")
week = input("Week: ")
player = input("Player: ")

def findPlayer(player, season, week) :
	playerFound = False
	i = 1
	while(not playerFound) :
		url = 'https://fantasy.nfl.com/league/4007290/history/' + season + '/teamgamecenter?teamId=' + str(i) + '&week=' + week
		page = urlopen(url)
		page_html = page.read()
		page.close()
		page_soup = bs(page_html, 'html.parser')
		matchup = page_soup.find_all('a', class_=re.compile("userName"))
		matchup[0] = matchup[0].text
		matchup[1] = matchup[1].text
		if (matchup[0] == player or matchup[1] == player) :
			return url
		i += 1

my_url = findPlayer(player, season, week)
uClient = urlopen(my_url)
page_html = uClient.read()
uClient.close()
#html parsing
soup = bs(page_html, 'html.parser')
teamWraps = [soup.find("div", class_=("teamWrap teamWrap-1")), soup.find("div", class_=("teamWrap teamWrap-2"))]

for t in teamWraps :
		print(t.find('a', class_=re.compile("teamName")).text + ' ', end = '')
		print(t.find('div', class_=re.compile("teamTotal")).text + ' ')
