#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright Brian Shannon 2014

import json
import urllib2
import unicodecsv as csv
import ConfigParser

# Modify config.ini (using config.ini.example as a template)
# Use the documentation to find the app key, user token and board id
# https://trello.com/docs/

config = ConfigParser.RawConfigParser()
config.read('config.ini')

APP_KEY = config.defaults()["app_key"]
USER_TOKEN = config.defaults()["user_token"]
BOARD_ID = config.defaults()["board_id"]
BOARD_URL_FORMAT = "https://api.trello.com/1/board/%s?key=%s&token=%s&cards=all&members=all&lists=all"
BOARD_URL = BOARD_URL_FORMAT % (BOARD_ID,APP_KEY,USER_TOKEN)

def cardToRow(card, idToUserName):
    return [card["name"],
            ",".join(map(lambda x: idToUserName[x], card["idMembers"])),
            card["dateLastActivity"][0:10] + " " + card["dateLastActivity"][11:16]]

def main():
    jsonfile = urllib2.urlopen(BOARD_URL)
    jsons = json.loads(jsonfile.read())

    cards = jsons["cards"]
    lists = jsons["lists"]
    members = jsons["members"]

    # done or archived, actually
    donelist = filter(lambda x: x["name"] == "Done" or x["closed"] == True, lists)[0]
    donecards = filter(lambda x: x["idList"] == donelist["id"], cards)

    cardsWithMember = lambda m, x: m["id"] in x["idMembers"]
    membersCardCount = dict()
    for member in members:
        numDoneWithMember = len(filter(lambda x: cardsWithMember(member, x), donecards))
        membersCardCount[member["username"]] = numDoneWithMember

    for member in membersCardCount.keys():
        print member + "\t:", membersCardCount[member]

    idToUserName = dict()
    for member in members:
        idToUserName[member["id"]] = member["username"]

    with open("done.csv", "w") as donecsvfile:
        csvwriter = csv.writer(donecsvfile)
        csvwriter.writerows(map(lambda x: cardToRow(x, idToUserName),donecards))


if __name__ == "__main__":
    main()
