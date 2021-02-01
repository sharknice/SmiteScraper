import json
import urllib.request

with open('sources/item_source.json') as f: #https://cms.smitegame.com/wp-json/smite-api/getItems/1
    data = json.load(f)

items = []

sourceItems = data
bootsId = 0
shoesId = 0
boots = next((x for x in sourceItems if x['DeviceName'] == 'Boots'), None)
if boots != None:
    bootsId = boots['ItemId']
shoes = next((x for x in sourceItems if x['DeviceName'] == 'Shoes'), None)
if shoes != None:
    shoesId = shoes['ItemId']

for sourceItem in sourceItems:
    if sourceItem['Type'] == "Item":
        print(sourceItem['DeviceName'])
        item = {}
        item['name'] = sourceItem['DeviceName']
        item['id'] = sourceItem['ItemId']
        item['cost'] = sourceItem['Price']
        item['type'] = "Both"
        item['tier'] = sourceItem['ItemTier']
        if item['tier'] > 1:
            parent = next((x for x in sourceItems if x['ItemId'] == sourceItem['ChildItemId']), None)
            if parent != None:
                item['cost'] += parent['Price']
                if item['tier'] == 3:
                    parentParent = next((x for x in sourceItems if x['ItemId'] == sourceItem['RootItemId']), None)
                    item['cost'] += parent['Price']

        if sourceItem['StartingItem']:
            item['starter'] = True
        if sourceItem['RootItemId'] == bootsId:
            item['shoes'] = True
        if sourceItem['RootItemId'] == shoesId:
            item['shoes'] = True

        if sourceItem['RestrictedRoles'] != "no restrictions" and sourceItem['RestrictedRoles'] != "":
            item['restrictedRoles'] = sourceItem['RestrictedRoles']

        # TODO: "toggleStats" and "stacks"

        url = sourceItem['itemIcon_URL']
        imageName = url.rsplit('/', 1)[-1].replace('*','')
        # try:
        #     urllib.request.urlretrieve(url, 'images/items/' + imageName)
        # except Exception:
        #     print("could not download " + imageName)       
        item['icon'] = 'images/smite/items/' + imageName

        if sourceItem['ItemDescription']['SecondaryDescription']:
            item['passive'] = sourceItem['ItemDescription']['SecondaryDescription']
            if 'AURA' in item['passive'] and 'Allied' not in item['passive'] and 'Ally' not in item['passive']:
                item['enemyInAura'] = {"toggle": True}
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
                    if "%" in sourceStat['Value']:
                        item['physicalPenetrationPercent'] = int(sourceStat['Value'][1:][:-1])
                        item['magicalPenetrationPercent'] = int(sourceStat['Value'][1:][:-1])
                    else:
                        item['physicalPenetration'] = int(sourceStat['Value'][1:])
                        item['magicalPenetration'] = int(sourceStat['Value'][1:])
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
            if "Acorn" in sourceItem['DeviceName']:
                item['type'] = "Acorn"
                
        items.append(item)

with open('items_result.json', 'w') as json_file:
    json.dump(items, json_file, indent='\t', sort_keys=True)
