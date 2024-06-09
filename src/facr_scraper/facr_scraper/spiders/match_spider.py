import scrapy
import requests

from bs4 import BeautifulSoup, PageElement
from src.facr_scraper.facr_scraper.items import MatchItem


class MatchSpider(scrapy.Spider):
    # Set the name of the spider (has to be defined outside the constructor due to the scrapy framework)
    name = "match"

    def __init__(self, target_team: str, base_url: str, central_url: str, cookie: str) -> None:
        """
        Initialize the spider that scrapes the match information from the website: https://www.fotbal.cz.

        :param target_team: name of the team to scrape the information for
        :param base_url: base url of the aforementioned football association website.
        :param central_url: central url of the website with the information about all matches
        :param cookie: PHPSESSID cookie to access the website
        :return: None
        """
        super(MatchSpider, self).__init__()

        # Save the base url and add the '/' at the end if it is missing
        self.base_url = base_url if base_url[-1] == '/' else base_url + '/'

        # Save the central url and target team
        self.central_url = central_url
        self.target_team = target_team

        # Set the headers for the request to obtain the general match information
        self.headers = {
            "cookie": cookie,
        }

        # Initialize the list to store the relative urls to the detailed match information
        self.relative_urls = []

        # Extract the information about the matches
        self.match_items = self.extract_match_info()

        # Get the links to the detailed match information
        self.start_urls = [self.base_url + link for link in self.relative_urls]

        # Set up match counter
        self.match_counter = 0

    def parse(self, response) -> None:
        """
        Parse the response from the website and extract the detailed information about each of the matches. This method
        will be called for each of the links in the start_urls. (internal scrapy functionality)

        Also, this method is very specific to the structure of the website and if the structure changes,
        the method will have to be updated.

        :param response: response from the website
        :return: None
        """
        # Parse the html content using BeautifulSoup for easier extraction of the information
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the half-time score
        half_time_score_text = soup.find('p', class_="H8 u-c-grey--100").get_text(strip=True).replace("(", "")\
            .replace(")", "")
        half_time_score = [int(score) for score in half_time_score_text.split(":")]

        # Extract the scorers and the time of the goals
        # -- Check if the target team is the home or the visitor team (when mentioned first -> home team)
        team_names = self.match_items[self.match_counter]["team_names"]
        is_home_team = self.target_team == team_names[0]

        # -- Set the class string for the scorers
        class_str = "MatchTimeline-item MatchTimeline-item"
        class_str += "--home" if is_home_team else "--visitor"

        # -- Extract the scorers
        scorer_elements = soup.find_all("li", class_=class_str)
        scorers = {}
        for scorer in scorer_elements:
            minute = int(scorer.find("strong").get_text(strip=True).replace(".", ""))
            player = scorer.find('p').get_text(strip=True)
            if player not in scorers:
                scorers[player] = []
            scorers[player].append(minute)

        # Select the sections of the web-page with the information about the target team
        sections = soup.find_all("section", class_="u-mt-24 u-overflow-x-auto")
        relevant_section = None
        for section in sections:
            # Extract team name
            team_name = section.find("h2", class_="H7").get_text(strip=True)

            # Skip the section if the target team is not in the team names
            if self.target_team == team_name:
                relevant_section = section
                break

        # Select the all rows of the table containing the information about the target team
        rows = relevant_section.find("table").find_all("tbody")[0].find_all("tr")

        # Loop through each row representing one player
        players_info = []
        for row in rows:
            # Extract the player information
            player_info = self.extract_player_info(row)

            # Check if the player scored a goal and add it to the player information
            player_name = player_info["name"]
            if player_name in scorers:
                player_info["goals"] = scorers[player_name]
            else:
                player_info["goals"] = []

            # Store the player information
            players_info.append(player_info)

        # Store the information about the match
        self.match_items[self.match_counter]["half_time_score"] = half_time_score
        self.match_items[self.match_counter]["players"] = players_info

        # Yield the information
        yield self.match_items[self.match_counter]

        # Increment the match counter
        self.match_counter += 1

        print(f"Match {self.match_counter} scraped.")

    def extract_match_info(self) -> [MatchItem, ...]:
        """
        Extract the information about the matches from the start_urls[0] website. The information includes the date,
        time, teams, referee, delegate, place, score, match number, notes, nuber of spectators, and the link to the
        detailed match information.

        Also note that this method is very specific to the structure of the website and if the structure changes, the
        method will have to be updated.

        :return: list with the match information (format: [MatchItem, ...])
                    - Note that the keys and values are in czech.
        """
        # Initialize array to store the match information
        match_info = []

        # Get the response from the website
        response = requests.get(self.central_url, headers=self.headers)

        # Parse the html content using BeautifulSoup for easier extraction of the information
        soup = BeautifulSoup(response.text, "html.parser")

        # Iterate over the matches and for each match extract the desired information
        for match_element in soup.find_all("li", class_="MatchRound js-matchRound"):
            if match_element:
                # Extract information about one match
                info = self.extract_one_match_info(match_element)

                # Skip the match if the target team is not in the team names (info is empty)
                if not info:
                    continue

                # Store the information about the match
                match_info.append(info)
            else:
                raise ValueError("MatchRound not found. Structure of the website has changed.")
        return match_info

    def extract_one_match_info(self, match_element: PageElement) -> MatchItem:
        """
        Extract the information about one match from the match_element.

        Also note that this method is very specific to the structure of the website and if the structure changes, the
        method will have to be updated.

        :param match_element: BeautifulSoup element with the information about one match
        :return: item with the information about the match
        """
        # Initialize the item to store the match information
        match_item = MatchItem()

        # Extract both team names
        team_names = [span.get_text(strip=True) for span in match_element.find_all("span", class_="H7")]

        # Skip the match if the target team is not in the team names
        if self.target_team not in team_names:
            return None

        # Extract the link to the detailed match information and store the team names
        link = match_element.find('a', class_="MatchRound-match")["href"]
        self.relative_urls.append(link)
        match_item["team_names"] = team_names

        # Extract the score
        score_element = match_element.find("strong", class_="H4 u-c-tertiary")
        score = []
        if score_element:
            score_text = score_element.get_text(strip=True)
            score = [int(score) for score in score_text.split(":")]
        match_item["score"] = score

        # Extract the additional information about the match
        meta_elements = match_element.find_all("p")
        for meta in meta_elements:
            # Find idx of the first ':' in the text
            meta_text = meta.get_text(strip=True)
            colon_idx = meta_text.find(':')
            if colon_idx == -1:
                raise ValueError("Colon not found in the meta text. Structure of the meta text has changed.")

            # The first part of the text is the key, the second part is the value
            key = meta_text[:colon_idx]
            value = meta_text[colon_idx + 1:].strip()

            # TODO: Refactor this part
            if key == "Datum":
                key = "date"
                value = value.replace("\xa0", " ").replace(".", "").split(" ")
            elif key == "Číslo utkání":
                key = "match_number"
            elif key == "Rozhodčí":
                key = "referees"
                value = value.replace("\t", "").replace("-", "").replace(",", "").split("\n")
            elif key == "Delegát":
                key = "delegate"
            elif key == "Hřiště":
                key = "stadium"
            elif key == "Diváků":
                key = "spectators"
            elif key == "Poznámka":
                key = "note"
            match_item[key] = value

        return match_item

    @staticmethod
    def extract_player_info(row: PageElement) -> dict:
        """
        Extract the information about the player from the table row.

        :param row: BeautifulSoup element with the information about the player
        :return: dictionary with the player information
        """
        # Initialize the dictionary to store the player information
        player_info = {}

        # Extract the text content of each cell in the row
        cells = row.find_all("td")
        player_info["number"] = int(cells[0].get_text(strip=True))
        player_info["position"] = cells[1].get_text(strip=True)
        player_info["name"] = cells[2].get_text(strip=True)
        player_info["red_card"] = int(cells[4].get_text(strip=True)) if cells[4].get_text(strip=True) else -1
        player_info["yellow_cards"] = [int(card) for card in cells[3].get_text(strip=True).split(",")
                                       if card] if cells[3].get_text(strip=True) else []

        # Check if the player was a captain
        if "[K]" in player_info["name"]:
            player_info["captain"] = True
            player_info["name"] = player_info["name"].replace("[K]", "").strip()
        else:
            player_info["captain"] = False

        # Extract substitution info if present
        substitution_td = cells[5]
        player_info["substitution_minute"] = int(substitution_td.find("span").get_text(strip=True)) \
            if substitution_td.find("span") else -1
        player_info["substitution_player"] = substitution_td.find("span")["title"] \
            if substitution_td.find("span") and "title" in substitution_td.find("span").attrs else ""

        return player_info
