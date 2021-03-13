import json
import urllib.request
import re

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
            if 'starter item' in item['passive'].lower():
                item['starter'] = True
            if 'AURA' in item['passive'] and 'Allied' not in item['passive'] and 'Ally' not in item['passive']:
                item['enemyInAura'] = {"toggle": True}
            manaToMagicalPower = re.search("\d+% of your Mana from items is converted to Magical Power", item['passive'])
            if manaToMagicalPower:
                amount = re.findall(r'\d+', manaToMagicalPower.group())
                item['manaToMagicalPower'] = amount
            if '% of your Mana is converted to Physical Power' in item['passive']:
                item['manaToPhysicalPower'] = 0.03
            if 'stacks' in item['passive']:
                item['stacks'] = { "current": 0, "max": 0, "stacks": [], "type": "permanent" }
                manaStacks = re.search("\d+ Mana per Stack", item['passive'])
                if manaStacks:
                    amount = re.findall(r'\d+', manaStacks.group())
                    item['stacks']['stacks'].append({ "mana" : amount[0]})
                physicalPowerStacks = re.search("gives you stacks of \+\d*\.?\d+ Physical Power", item['passive'])
                if physicalPowerStacks:
                    amount = re.findall(r'\d*\.?\d+', physicalPowerStacks.group())
                    item['stacks']['stacks'].append({ "physicalPower" : amount[0]})
                physicalLifestealStacks = re.search("and \+\d*\.?\d+% Physical Lifesteal", item['passive'])
                if physicalLifestealStacks:
                    amount = re.findall(r'\d*\.?\d+', physicalLifestealStacks.group())
                    item['stacks']['stacks'].append({ "physicalLifesteal" : amount[0]})
                magicalProtectionStacks = re.search("gain \+\d+ Magical Protection", item['passive'])
                if magicalProtectionStacks:
                    amount = re.findall(r'\d+', magicalProtectionStacks.group())
                    item['stacks']['stacks'].append({ "magicalProtection" : amount[0]})
                physicalProtectionStacks = re.search("and \+\d+ Physical Protection", item['passive'])
                if physicalProtectionStacks:
                    amount = re.findall(r'\d+', physicalProtectionStacks.group())
                    item['stacks']['stacks'].append({ "physicalProtection" : amount[0]})
                movementSpeedStacks = re.search("provide \d+% Movement Speed", item['passive'])
                if movementSpeedStacks:
                    amount = re.findall(r'\d+', movementSpeedStacks.group())
                    item['stacks']['stacks'].append({ "movementSpeed" : amount[0]})
                attackSpeedStacks = re.search(", \d+% Attack Speed", item['passive'])
                if attackSpeedStacks:
                    amount = re.findall(r'\d+', attackSpeedStacks.group())
                    item['stacks']['stacks'].append({ "attackSpeed" : amount[0]})

                maxStacks = re.search("max. \d+ stacks", item['passive'])
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = amount[0]
                    item['stacks']['current'] = amount[0]
                maxStacks = re.search("Stacks up to \d+ times", item['passive'], re.IGNORECASE)
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = amount[0]
                    item['stacks']['current'] = amount[0]
                maxStacks = re.search("At \d+ Stacks", item['passive'], re.IGNORECASE)
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = amount[0]
                    item['stacks']['current'] = amount[0]

                if 'consume' in item['passive']:
                    item['stacks']['type'] = "temporary"
                    item['stacks']['current'] = 0
                if 'Evolves' in item['passive']:
                    item['stacks']['evolved'] = {}
                    coolDown = re.search("gaining \d+% Cooldown Reduction", item['passive'])
                    if coolDown:
                        amount = re.findall(r'\d+', coolDown.group())
                        item['stacks']['evolved']['cooldownReduction'] = amount[0]
                    physicalPower = re.search("gaining \d+ Physical Power", item['passive'])
                    if physicalPower:
                        amount = re.findall(r'\d+', physicalPower.group())
                        item['stacks']['evolved']['physicalPower'] = amount[0]
                    physicalLifesteal = re.search(", \d+% Physical Lifesteal", item['passive'])  
                    if physicalLifesteal:
                        amount = re.findall(r'\d+', physicalLifesteal.group())
                        item['stacks']['evolved']['physicalLifesteal'] = amount[0]
                    manaToMagicalPower = re.search("gaining \d+% extra Mana to Power conversion", item['passive'])  
                    if manaToMagicalPower:
                        amount = re.findall(r'\d+', manaToMagicalPower.group())
                        item['stacks']['evolved']['manaToMagicalPower'] = amount[0]

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
        
        if 'Evolved' not in item['name']:
            items.append(item)

with open('items_result.json', 'w') as json_file:
    json.dump(items, json_file, indent='\t', sort_keys=True)
