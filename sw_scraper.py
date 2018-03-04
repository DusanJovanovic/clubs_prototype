#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import requests
from bs4 import BeautifulSoup
import json

header = {'User-Agent': 'Mozilla/5.0'}
Competition = namedtuple('Competition', 'code URL title pages')
league_codes = {'cl': Competition(10, 'uefa-champions-league', 'UEFA Champions League', -9),
                'el': Competition(18, 'uefa-cup', 'UEFA Europa League', -14)}


def retreive_links(season, league):
    league = league_codes[league]
    link = 'https://int.soccerway.com/international/europe/{}/{}{}/'.format(league.URL, season, season + 1)
    r = requests.get(link, header)
    soup = BeautifulSoup(r.text, 'lxml')
    ejs = soup.find('a', {'title': league.title}).parent.find_all('a')[2:]
    links = ['https://int.soccerway.com' + x['href'] for x in ejs]
    return links


def retreive_wrappers(link):
    r = requests.get(link, header)
    soup = BeautifulSoup(r.text, 'lxml')
    wrappers = soup.find_all('div', {'class': 'block_competition_matches_full-wrapper'})
    return wrappers if 'final-stages' not in link else wrappers[::-1]


def retreive_stage(wrapper):
    return wrapper.find('h2').text.strip()


def retreive_tr(wrapper):
    return wrapper.find_all('tr', {'class': 'no-date-repetition'})


def dates(tr, s):
    datum = tr.find('td', {'class': 'date'}).text.strip()
    return datum if datum != '' else s


def home_team(tr):
    return tr.find('td', {'class': 'team-a'}).text.strip()


def away_team(tr):
    return tr.find('td', {'class': 'team-b'}).text.strip()


def score(tr):
    result = tr.find('td', {'class': 'score-time'}).text.strip().replace(' ', '')
    if '\n' in result:
        result = result.replace('\n', '')
        span = tr.find('span', {'class': 'addition-visible'})
        if 'score-addition-left' in span['class']:
            return result[:-1]
        else:
            return result[1:]
    return result



def group_matches(link, league_abr):
    league = league_codes[league_abr]
    round_id = link[link.find('stage/r') + 7:-1]
    competition_id = league.code
    wrappers = []
    for page in range(league.pages, 1):
        group_link = ('https://int.soccerway.com/a/block_competition_matches_summary?'
                      'block_id=page_competition_1_block_competition_matches_summary_5&'
                      'callback_params={{"page":{},"block_service_id":'
                      '"competition_summary_block_competitionmatchessummary","round_id":{},'
                      '"outgroup":false,"view":2,"competition_id":{}}}&'
                      'action=changePage&params={{"page":{}}}').format(page, round_id, competition_id, page)
        wrappers.append(get_content(group_link))
    return wrappers


def get_content(link):
    r = requests.get(link, header)
    dct = json.loads(r.text)
    return BeautifulSoup(dct['commands'][0]['parameters']['content'], 'lxml')


#f = open('tst.csv', 'wt', encoding='UTF-8')
for tag in retreive_wrappers('https://int.soccerway.com/international/europe/uefa-cup/20162017/s12531/final-stages/'):
    print(retreive_stage(tag))
    s = 'date'
    trs = retreive_tr(tag)
    for tr in trs:
        s = dates(tr, s)
        print(s, home_team(tr), away_team(tr), score(tr))
    print('#########################')
#f.close()
"""for tag in group_matches('https://int.soccerway.com/international/europe/uefa-cup/20162017/group-stage/r35527/', 'el'):
    s = 'date'
    trs = retreive_tr(tag)
    for tr in trs:
        s = dates(tr, s)
        print(s, home_team(tr), away_team(tr), score(tr))
    print('#########################')"""
