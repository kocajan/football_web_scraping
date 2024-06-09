# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class FacrscraperPipeline:
    def process_item(self, item, spider):
        # Export the item to a JSON file
        # - Check if the first match is being processed, if so, clear the file
        mode = 'a'
        if spider.match_counter == 0:
            mode = 'w'

        # - Write the item to the file
        with open("matches.json", mode) as file:
            file.write(str(item) + "\n")
