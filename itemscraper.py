import json
import urllib.request

with open('sources/item_source.json') as f: #https://cms.smitegame.com/wp-json/smite-api/getItems/1
    data = json.load(f)

items = []
#sourceItems = data['items']
sourceItems = data
for sourceItem in sourceItems:
    if sourceItem['Type'] == "Item":
        print(sourceItem['DeviceName'])
        item = {}
        item['name'] = sourceItem['DeviceName']
        item['id'] = sourceItem['ItemId']
        item['cost'] = sourceItem['Price']
        item['type'] = "Both"
        item['tier'] = sourceItem['ItemTier']

        url = sourceItem['itemIcon_URL']
        imageName = url.rsplit('/', 1)[-1].replace('*','')
        #urllib.request.urlretrieve(url, 'images/items/' + imageName)
        item['icon'] = 'images/smite/items/' + imageName

        if sourceItem['ItemDescription']['SecondaryDescription']:
            item['passive'] = sourceItem['ItemDescription']['SecondaryDescription']
        if sourceItem['ItemDescription']['Menuitems']:
            for sourceStat in sourceItem['ItemDescription']['Menuitems']:
                if sourceStat['Description'] == 'Physical Power':
                    item['physicalPower'] = int(sourceStat['Value'][1:])
                    item['type'] = "Physical"
                if sourceStat['Description'] == 'Magical Power':
                    item['magicalPower'] = int(sourceStat['Value'][1:])
                    item['type'] = "Magical"
                if sourceStat['Description'] == 'Attack Speed':
                    item['attackSpeed'] = int(sourceStat['Value'][1:][:-1])
                if sourceStat['Description'] == 'Physical Lifesteal':
                    item['physicalLifesteal'] = int(sourceStat['Value'][1:][:-1])
                    item['type'] = "Physical"
                if sourceStat['Description'] == 'Magical Lifesteal':
                    item['magicalLifesteal'] = int(sourceStat['Value'][1:][:-1])
                    item['type'] = "Magical"
                if sourceStat['Description'] == 'Physical Penetration':
                    if "%" in sourceStat['Value']:
                        item['physicalPenetrationPercent'] = int(sourceStat['Value'][1:][:-1])
                    else:
                        item['physicalPenetration'] = int(sourceStat['Value'][1:])
                    item['type'] = "Physical"
                if sourceStat['Description'] == 'Magical Penetration':
                    if "%" in sourceStat['Value']:
                        item['magicalPenetrationPercent'] = int(sourceStat['Value'][1:][:-1])
                    else:
                        item['magicalPenetration'] = int(sourceStat['Value'][1:])
                    item['type'] = "Magical"
                if sourceStat['Description'] == 'Penetration':
                    item['physicalPenetration'] = int(sourceStat['Value'][1:])
                if sourceStat['Description'] == 'Critical Strike Chance':
                    item['criticalChance'] = int(sourceStat['Value'][1:][:-1])
                    item['type'] = "Physical"
                if sourceStat['Description'] == 'Physical Protection':
                    item['physicalProtection'] = int(sourceStat['Value'][1:])
                if sourceStat['Description'] == 'Magical Protection':
                    item['magicalProtection'] = int(sourceStat['Value'][1:])
                if sourceStat['Description'] == 'Health':
                    item['health'] = int(sourceStat['Value'][1:])
                if sourceStat['Description'] == 'HP5':
                    item['hpFive'] = int(sourceStat['Value'][1:])
                if sourceStat['Description'] == 'Crowd Control Reduction':
                    item['crowdControl'] = int(sourceStat['Value'][1:][:-1])
                if sourceStat['Description'] == 'Movement Speed':
                    item['movementSpeed'] = int(sourceStat['Value'][1:][:-1])
                if sourceStat['Description'] == 'Cooldown Reduction':
                    item['cooldownReduction'] = int(sourceStat['Value'][1:][:-1])
                if sourceStat['Description'] == 'Mana':
                    item['mana'] = int(sourceStat['Value'][1:])
                if sourceStat['Description'] == 'MP5':
                    item['mpFive'] = int(sourceStat['Value'][1:])
                
        items.append(item)

with open('result.json', 'w') as json_file:
    json.dump(items, json_file)
