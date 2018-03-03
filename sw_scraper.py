from collections import namedtuple
import requests
from bs4 import BeautifulSoup

header = {'User-Agent': 'Mozilla/5.0'}
Competition = namedtuple('Competition', 'code URL title')
league_codes = {'cl': Competition(10, 'uefa-champions-league', 'UEFA Champions League'),
                'el': Competition(18, 'uefa-cup', 'UEFA Europa League')}


def retreive_links(season, league):
    league = league_codes[league]
    link = 'https://int.soccerway.com/international/europe/{}/{}{}/'.format(league.URL, season, season + 1)
    r = requests.get(link, header)
    soup = BeautifulSoup(r.text, 'lxml')
    ejs = soup.find('a', {'title': league.title}).parent.find_all('a')[2:]
    links = ['https://int.soccerway.com' + x['href'] for x in ejs]
    return links


ref_page, round_id, competition_id, page = 1, 2, 3, 4
group_link = ('https://int.soccerway.com/a/block_competition_matches_summary?'
              'block_id=page_competition_1_block_competition_matches_summary_5&'
              'callback_params={{"page":{0},"block_service_id":'
              '"competition_summary_block_competitionmatchessummary","round_id":{1},'
              '"outgroup":false,"view":2,"competition_id":{2}}}&'
              'action=changePage&params={{"page":{3}}}').format(ref_page, round_id, competition_id, page)
print(group_link)
print(retreive_links(2013, 'cl'))