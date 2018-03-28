#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import requests
from bs4 import BeautifulSoup
import json
import itertools

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
    td = tr.find('td', {'class': 'team-a'})
    country = td.a['class'][-1].replace('_16_right', '').replace('-', ' ').title()
    return td.text.strip() + ',' + country


def away_team(tr):
    td = tr.find('td', {'class': 'team-b'})
    country = td.a['class'][-1].replace('_16_left', '').replace('-', ' ').title()
    return td.text.strip() + ',' + country


def score(tr):
    result = tr.find('td', {'class': 'score-time'}).text.strip().replace(' ', '')
    if '\n' in result:
        result = result.replace('\n', '')
        span = tr.find('span', {'class': 'addition-visible'})
        if 'score-addition-left' in span['class']:
            return result[:-1].split('-')
        else:
            return result[1:].split('-')
    return result.split('-')



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


def tr_to_string(tr, s, season, stage):
    s = dates(tr, s)
    try:
        home_score, away_score = score(tr)
    except ValueError:
        home_score, away_score = 'CANC', 'CANC'
    lst = [s, home_team(tr), home_score, away_team(tr), away_score, stage, str(season)]
    return (','.join(lst) + '\n', s)


# https://int.soccerway.com/international/europe/uefa-cup/20162017/1st-qualifying-round/r35523/
def link_to_string(link, season, abr):
    s = '11/11/11'
    if 'final-stages' in link:
        strng = ''
        for wrapper in retreive_wrappers(link):
            stage = abr + '-' + retreive_stage(wrapper)
            trs = retreive_tr(wrapper)
            for tr in trs:
                tup, s = tr_to_string(tr, s, season, stage)
                strng += tup
    elif 'group-stage' in link:
        strng = ''
        for wrapper in group_matches(link, abr):
            stage = abr + '-group-stage'
            trs = retreive_tr(wrapper)
            for tr in trs:
                tup, s = tr_to_string(tr, s, season, stage)
                strng += tup
    else:
        strng = ''
        for wrapper in retreive_wrappers(link):
            stage = abr + '-' + link.split('/')[-3]
            trs = retreive_tr(wrapper)
            for tr in trs:
                tup, s = tr_to_string(tr, s, season, stage)
                strng += tup
    return strng
    

f = open('results.csv', 'wt', encoding='UTF-8')
f.write('Date,Home,H_Country,H_Score,Away,A_Country,A_Score,Stage,Season\n')
comb = itertools.product(range(2013, 2018), ['cl', 'el'])
for el in comb:
    print(el)
    for link in retreive_links(el[0], el[1]):
        print(link)
        strng = link_to_string(link, el[0], el[1])
        f.write(strng)
f.close()
