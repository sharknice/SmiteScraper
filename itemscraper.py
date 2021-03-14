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

        url = sourceItem['itemIcon_URL']
        imageName = url.rsplit('/', 1)[-1].replace('*','')
        # try:
        #     urllib.request.urlretrieve(url, 'images/items/' + imageName)
        # except Exception:
        #     print("could not download " + imageName)       
        item['icon'] = 'images/smite/items/' + imageName

        if sourceItem['ItemDescription']['SecondaryDescription']:
            item['passive'] = sourceItem['ItemDescription']['SecondaryDescription']
            if 'font color' in item['passive']:
                item['name'] = 'REMOVE'
            if 'starter item' in item['passive'].lower():
                item['starter'] = True
            if 'AURA' in item['passive'] and 'Allied' not in item['passive'] and 'Ally' not in item['passive']:
                item['enemyInAura'] = {"toggle": True}
            manaToMagicalPower = re.search("\d+% of your Mana from items is converted to Magical Power", item['passive'])
            if manaToMagicalPower:
                amount = re.findall(r'\d+', manaToMagicalPower.group())
                item['manaToMagicalPower'] = int(amount[0])
            if '% of your Mana is converted to Physical Power' in item['passive']:
                item['manaToPhysicalPower'] = 0.03
            basicAttackFlatIncrease = re.search("\+\d+ Basic Attack Damage", item['passive'])
            if basicAttackFlatIncrease:
                amount = re.findall(r'\d+', basicAttackFlatIncrease.group())
                item['basicAttackFlatIncrease'] = int(amount[0])
            criticalStrikeDamage = re.search("Critical Strike bonus damage dealt is increased by \d+%", item['passive'])
            if criticalStrikeDamage:
                amount = re.findall(r'\d+', criticalStrikeDamage.group())
                item['criticalStrikeDamage'] = int(amount[0])
                
            if 'stacks' in item['passive'] or 'Stacks' in item['passive']:
                item['stacks'] = { "current": 0, "max": 0, "stacks": {}, "type": "permanent" }
                manaStacks = re.search("\d+ Mana per Stack", item['passive'])
                if manaStacks:
                    amount = re.findall(r'\d+', manaStacks.group())
                    item['stacks']['stacks']['mana']= int(amount[0])
                physicalPowerStacks = re.search("gives you stacks of \+\d*\.?\d+ Physical Power", item['passive'])
                if physicalPowerStacks:
                    amount = re.findall(r'\d*\.?\d+', physicalPowerStacks.group())
                    item['stacks']['stacks']['physicalPower'] = float(amount[0])
                physicalPowerStacks = re.search("increases your Physical Power by \d+", item['passive'])
                if physicalPowerStacks:
                    amount = re.findall(r'\d+', physicalPowerStacks.group())
                    item['stacks']['stacks']['physicalPower'] = int(amount[0])
                physicalLifestealStacks = re.search("and \+\d*\.?\d+% Physical Lifesteal", item['passive'])
                if physicalLifestealStacks:
                    amount = re.findall(r'\d*\.?\d+', physicalLifestealStacks.group())
                    item['stacks']['stacks']['physicalLifesteal'] = float(amount[0])
                magicalPowerStacks = re.search("and \d+ Magical Power", item['passive'])
                if magicalPowerStacks:
                    amount = re.findall(r'\d+', magicalPowerStacks.group())
                    item['stacks']['stacks']['magicalPower'] = int(amount[0])
                magicalPowerStacks = re.search("gain \d+ power", item['passive'])
                if magicalPowerStacks:
                    amount = re.findall(r'\d+', magicalPowerStacks.group())
                    item['stacks']['stacks']['magicalPower'] = int(amount[0])
                magicalPowerStacks = re.search("and \+\d*\.?\d+ Magical Power", item['passive'])
                if magicalPowerStacks:
                    amount = re.findall(r'\d*\.?\d+', magicalPowerStacks.group())
                    item['stacks']['stacks']['magicalPower'] = float(amount[0])
                magicalProtectionStacks = re.search("gain \+\d+ Magical Protection", item['passive'])
                if magicalProtectionStacks:
                    amount = re.findall(r'\d+', magicalProtectionStacks.group())
                    item['stacks']['stacks']['magicalProtection'] = int(amount[0])
                physicalProtectionStacks = re.search("and \+\d+ Physical Protection", item['passive'])
                if physicalProtectionStacks:
                    amount = re.findall(r'\d+', physicalProtectionStacks.group())
                    item['stacks']['stacks']['physicalProtection'] = int(amount[0])
                physicalProtectionStacks = re.search("stack of \d+ Physical Protection", item['passive'])
                if physicalProtectionStacks:
                    amount = re.findall(r'\d+', physicalProtectionStacks.group())
                    item['stacks']['stacks']['physicalProtection'] = int(amount[0])
                protectionStacks = re.search("provides \d+ Physical and Magical Protections", item['passive'])
                if protectionStacks:
                    amount = re.findall(r'\d+', protectionStacks.group())
                    item['stacks']['stacks']['physicalProtection'] = int(amount[0])
                    item['stacks']['stacks']['magicalProtection'] = int(amount[0])
                protectionStacks = re.search("provide \d+ Physical and Magical Protection", item['passive'])
                if protectionStacks:
                    amount = re.findall(r'\d+', protectionStacks.group())
                    item['stacks']['stacks']['physicalProtection'] = int(amount[0])
                    item['stacks']['stacks']['magicalProtection'] = int(amount[0])
                movementSpeedStacks = re.search("provide \d+% Movement Speed", item['passive'])
                if movementSpeedStacks:
                    amount = re.findall(r'\d+', movementSpeedStacks.group())
                    item['stacks']['stacks']['movementSpeed'] = int(amount[0])
                movementSpeedStacks = re.search("granting \d+% Movement Speed", item['passive'])
                if movementSpeedStacks:
                    amount = re.findall(r'\d+', movementSpeedStacks.group())
                    item['stacks']['stacks']['movementSpeed'] = int(amount[0])
                attackSpeedStacks = re.search(", \d+% Attack Speed", item['passive'])
                if attackSpeedStacks:
                    amount = re.findall(r'\d+', attackSpeedStacks.group())
                    item['stacks']['stacks']['attackSpeed'] = int(amount[0])
                attackSpeedStacks = re.search("gain \d+% Attack Speed", item['passive'])
                if attackSpeedStacks:
                    amount = re.findall(r'\d+', attackSpeedStacks.group())
                    item['stacks']['stacks']['attackSpeed'] = int(amount[0])
                criticalStrikeStacks = re.search("and \d*\.?\d+% Physical Critical Strike Chance", item['passive'])
                if criticalStrikeStacks:
                    amount = re.findall(r'\d*\.?\d+', criticalStrikeStacks.group())
                    item['stacks']['stacks']['criticalChance'] = float(amount[0])
                criticalStrikeStacks = re.search("provides \d+% Critical Strike Chance", item['passive'])
                if criticalStrikeStacks:
                    amount = re.findall(r'\d+', criticalStrikeStacks.group())
                    item['stacks']['stacks']['criticalChance'] = int(amount[0])
                healthStacks = re.search("gain \+\d+ Health", item['passive'])
                if healthStacks:
                    amount = re.findall(r'\d+', healthStacks.group())
                    item['stacks']['stacks']['health'] = int(amount[0])

                maxStacks = re.search("max. \d+ stacks", item['passive'], re.IGNORECASE)
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("Stacks up to \d+ times", item['passive'], re.IGNORECASE)
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("Stack up to \d+ times", item['passive'], re.IGNORECASE)
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("At \d+ Stacks", item['passive'], re.IGNORECASE)
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("max of \d+ stacks", item['passive'], re.IGNORECASE)
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("maximum of \d+ stacks", item['passive'], re.IGNORECASE)
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("max \d+ stacks", item['passive'], re.IGNORECASE)
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])

                if 'consume' in item['passive'] or 'Stacks last for' in item['passive'] or 'Stacks are removed' in item['passive'] or 'For every 100 gold you have gain' in item['passive'] or 'lasts' in item['passive'] or 'Lasts' in item['passive'] or 'for 5s' in item['passive'] or 'for 15 s' in item['passive']:
                    item['stacks']['type'] = "temporary"
                    item['stacks']['current'] = 0

                if 'Evolves' in item['passive'] or 'evolves' in item['passive']:
                    item['stacks']['evolved'] = { 'icon': 'images/smite/items/evolved-' + imageName}
                    coolDown = re.search("gaining \d+% Cooldown Reduction", item['passive'])
                    if coolDown:
                        amount = re.findall(r'\d+', coolDown.group())
                        item['stacks']['evolved']['cooldownReduction'] = int(amount[0])
                    physicalPower = re.search("gaining \d+ Physical Power", item['passive'])
                    if physicalPower:
                        amount = re.findall(r'\d+', physicalPower.group())
                        item['stacks']['evolved']['physicalPower'] = int(amount[0])
                    physicalLifesteal = re.search(", \d+% Physical Lifesteal", item['passive'])  
                    if physicalLifesteal:
                        amount = re.findall(r'\d+', physicalLifesteal.group())
                        item['stacks']['evolved']['physicalLifesteal'] = int(amount[0])
                    manaToMagicalPower = re.search("gaining \d+% extra Mana to Power conversion", item['passive'])  
                    if manaToMagicalPower:
                        amount = re.findall(r'\d+', manaToMagicalPower.group())
                        item['stacks']['evolved']['manaToMagicalPower'] = int(amount[0])
                    physicalProtection = re.search("providing an Aura of \d+ Physical Protection", item['passive'])  
                    if physicalProtection:
                        amount = re.findall(r'\d+', physicalProtection.group())
                        item['stacks']['evolved']['physicalProtection'] = int(amount[0])
                    magicalProtection = re.search("and \d+ Magical Protection", item['passive'])  
                    if magicalProtection:
                        amount = re.findall(r'\d+', magicalProtection.group())
                        item['stacks']['evolved']['magicalProtection'] = int(amount[0])

            if 'If you drop below' in item['passive'] or 'Your Critical Hits provide you with' in item['passive'] or 'While you are within' in item['passive'] or 'after using an ability' in item['passive']:
                item['toggleStats'] = { 'toggle': False }
                physicalLifestealToggle = re.search("gain an additional \d+% Physical Lifesteal", item['passive'])
                if physicalLifestealToggle:
                    amount = re.findall(r'\d+', physicalLifestealToggle.group())
                    item['toggleStats']['physicalLifesteal'] = int(amount[0])
                physicalpowerToggle = re.search("provides \d+ Physical Power", item['passive'])
                if physicalpowerToggle:
                    amount = re.findall(r'\d+', physicalpowerToggle.group())
                    item['toggleStats']['physicalPower'] = int(amount[0])
                attackSpeedToggle = re.search("and \d+% Attack Speed", item['passive'])
                if attackSpeedToggle:
                    amount = re.findall(r'\d+', attackSpeedToggle.group())
                    item['toggleStats']['attackSpeed'] = int(amount[0])
                attackSpeedToggle = re.search(" you gain \d+% Attack Speed", item['passive'])
                if attackSpeedToggle:
                    amount = re.findall(r'\d+', attackSpeedToggle.group())
                    item['toggleStats']['attackSpeed'] = int(amount[0])
                physicalPenetrationPercentToggle = re.search("provide you with \d+% Physical Penetration", item['passive'])
                if physicalPenetrationPercentToggle:
                    amount = re.findall(r'\d+', physicalPenetrationPercentToggle.group())
                    item['toggleStats']['physicalPenetrationPercent'] = int(amount[0])
                attackAndMovementSpeedToggle = re.search("increase your Attack Speed and Movement Speed by \d+%", item['passive'])
                if attackAndMovementSpeedToggle:
                    amount = re.findall(r'\d+', attackAndMovementSpeedToggle.group())
                    item['toggleStats']['attackSpeed'] = int(amount[0])
                    item['toggleStats']['movementSpeed'] = int(amount[0])
                basicAttackPercentIncrease = re.search("Basic Attack will deal an additional \d+% damage", item['passive'], re.IGNORECASE)
                if basicAttackPercentIncrease:
                    amount = re.findall(r'\d+', basicAttackPercentIncrease.group())
                    item['toggleStats']['basicAttackPercentIncrease'] = int(amount[0])

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
        
        if 'Evolved' not in item['name'] and 'REMOVE' not in item['name'] and '*' not in item['name']:
            items.append(item)

with open('items_result.json', 'w') as json_file:
    json.dump(items, json_file, indent='\t', sort_keys=True)
