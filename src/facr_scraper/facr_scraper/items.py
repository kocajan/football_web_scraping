# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MatchItem(scrapy.Item):
    team_names = scrapy.Field()
    score = scrapy.Field()
    half_time_score = scrapy.Field()
    players = scrapy.Field()
    date = scrapy.Field()
    match_number = scrapy.Field()
    referees = scrapy.Field()
    delegate = scrapy.Field()
    stadium = scrapy.Field()
    spectators = scrapy.Field()
    note = scrapy.Field()

