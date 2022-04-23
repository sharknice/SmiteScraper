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
            item['passive'] = sourceItem['ItemDescription']['SecondaryDescription'].replace("<font color='#42F46E'>", "").replace("<font color='#F44242'>", "")
            if sourceItem['ActiveFlag'] == 'n':
                item['name'] = 'REMOVE'
            if 'AURA' in item['passive'].lower() and 'Allied'.lower() not in item['passive'].lower() and 'Ally'.lower() not in item['passive'].lower():
                item['enemyInAura'] = {"toggle": True}
            manaToMagicalPower = re.search("\d+% of your Mana from items is converted to Magical Power".lower(), item['passive'].lower())
            if manaToMagicalPower:
                amount = re.findall(r'\d+', manaToMagicalPower.group())
                item['manaToMagicalPower'] = int(amount[0])
            if '% of your Mana is converted to Physical Power'.lower() in item['passive'].lower():
                item['manaToPhysicalPower'] = 0.03
            basicAttackFlatIncrease = re.search("\+\d+ Basic Attack Damage".lower(), item['passive'].lower())
            if basicAttackFlatIncrease:
                amount = re.findall(r'\d+', basicAttackFlatIncrease.group())
                item['basicAttackFlatIncrease'] = int(amount[0])
            basicAttackPercentPenetration = re.search("your basic attacks benefit from an additional \d+% physical penetration".lower(), item['passive'].lower())
            if basicAttackPercentPenetration:
                amount = re.findall(r'\d+', basicAttackPercentPenetration.group())
                item['basicAttackPercentPenetration'] = int(amount[0])
            criticalStrikeDamage = re.search("Critical Strike bonus damage dealt is increased by \d+%".lower(), item['passive'].lower())
            if criticalStrikeDamage:
                amount = re.findall(r'\d+', criticalStrikeDamage.group())
                item['criticalStrikeDamage'] = int(amount[0])
            overcapAttackSpeedToPhysicalPower = re.search("For each \d*\.?\d+ Attack Speed you go over cap you gain \d+ Physical Power".lower(), item['passive'].lower())
            if overcapAttackSpeedToPhysicalPower:
                over = re.findall(r'\d*\.?\d+', overcapAttackSpeedToPhysicalPower.group())
                gain = re.findall(r'\d+', overcapAttackSpeedToPhysicalPower.group())
                item['overcapAttackSpeedToPhysicalPower'] = float(float(over[0])/int(gain[-1]))
            maxHealthDamage = re.search("deal Physical Damage equal to \d+% of the target's maximum Health".lower(), item['passive'].lower())
            if maxHealthDamage:
                amount = re.findall(r'\d+', maxHealthDamage.group())
                item['maxHealthDamage'] = int(amount[0])
            criticalStrikeDamageDecrease = re.search("Critical Strikes bonus damage taken is decreased by \d+%".lower(), item['passive'].lower())
            if criticalStrikeDamageDecrease:
                amount = re.findall(r'\d+', criticalStrikeDamageDecrease.group())
                item['criticalStrikeDamageDecrease'] = int(amount[0])

            if 'per 10% of your available Mana'.lower() in item['passive'].lower():
                item['stacks'] = { "current": 10, "max": 10, "stacks": {}, "type": "permanent" }
                magicalPowerStacks = re.search("grants \d+ Magical power per".lower(), item['passive'].lower())
                if magicalPowerStacks:
                    amount = re.findall(r'\d+', magicalPowerStacks.group())
                    item['stacks']['stacks']['magicalPower'] = int(amount[0])

            if 'stack'.lower() in item['passive'].lower():
                item['stacks'] = { "current": 0, "max": 0, "stacks": {}, "type": "permanent" }
                manaStacks = re.search("\d+ Mana per Stack".lower(), item['passive'].lower())
                if manaStacks:
                    amount = re.findall(r'\d+', manaStacks.group())
                    item['stacks']['stacks']['mana']= int(amount[0])
                physicalPowerStacks = re.search("gives you stacks of \+\d*\.?\d+ Physical Power".lower(), item['passive'].lower())
                if physicalPowerStacks:
                    amount = re.findall(r'\d*\.?\d+', physicalPowerStacks.group())
                    item['stacks']['stacks']['physicalPower'] = float(amount[0])
                physicalPowerStacks = re.search("increases your Physical Power by \d+".lower(), item['passive'].lower())
                if physicalPowerStacks:
                    amount = re.findall(r'\d+', physicalPowerStacks.group())
                    item['stacks']['stacks']['physicalPower'] = int(amount[0])
                physicalLifestealStacks = re.search("and \+\d*\.?\d+% Physical Lifesteal".lower(), item['passive'].lower())
                if physicalLifestealStacks:
                    amount = re.findall(r'\d*\.?\d+', physicalLifestealStacks.group())
                    item['stacks']['stacks']['physicalLifesteal'] = float(amount[0])
                magicalPowerStacks = re.search("and \d+ Magical Power".lower(), item['passive'].lower())
                if magicalPowerStacks:
                    amount = re.findall(r'\d+', magicalPowerStacks.group())
                    item['stacks']['stacks']['magicalPower'] = int(amount[0])
                magicalPowerStacks = re.search("gain \d+ power".lower(), item['passive'].lower())
                if magicalPowerStacks:
                    amount = re.findall(r'\d+', magicalPowerStacks.group())
                    item['stacks']['stacks']['magicalPower'] = int(amount[0])
                magicalPowerStacks = re.search("and \+\d*\.?\d+ Magical Power".lower(), item['passive'].lower())
                if magicalPowerStacks:
                    amount = re.findall(r'\d*\.?\d+', magicalPowerStacks.group())
                    item['stacks']['stacks']['magicalPower'] = float(amount[0])
                magicalProtectionStacks = re.search("gain \+\d+ Magical Protection".lower(), item['passive'].lower())
                if magicalProtectionStacks:
                    amount = re.findall(r'\d+', magicalProtectionStacks.group())
                    item['stacks']['stacks']['magicalProtection'] = int(amount[0])
                physicalProtectionStacks = re.search("and \+\d+ Physical Protection".lower(), item['passive'].lower())
                if physicalProtectionStacks:
                    amount = re.findall(r'\d+', physicalProtectionStacks.group())
                    item['stacks']['stacks']['physicalProtection'] = int(amount[0])
                physicalProtectionStacks = re.search("stack of \d+ Physical Protection".lower(), item['passive'].lower())
                if physicalProtectionStacks:
                    amount = re.findall(r'\d+', physicalProtectionStacks.group())
                    item['stacks']['stacks']['physicalProtection'] = int(amount[0])
                protectionStacks = re.search("provides \d+ Physical and Magical Protections".lower(), item['passive'].lower())
                if protectionStacks:
                    amount = re.findall(r'\d+', protectionStacks.group())
                    item['stacks']['stacks']['physicalProtection'] = int(amount[0])
                    item['stacks']['stacks']['magicalProtection'] = int(amount[0])
                protectionStacks = re.search("provide \d+ Physical and Magical Protection".lower(), item['passive'].lower())
                if protectionStacks:
                    amount = re.findall(r'\d+', protectionStacks.group())
                    item['stacks']['stacks']['physicalProtection'] = int(amount[0])
                    item['stacks']['stacks']['magicalProtection'] = int(amount[0])
                movementSpeedStacks = re.search("provide \d+% Movement Speed".lower(), item['passive'].lower())
                if movementSpeedStacks:
                    amount = re.findall(r'\d+', movementSpeedStacks.group())
                    item['stacks']['stacks']['movementSpeed'] = int(amount[0])
                movementSpeedStacks = re.search("granting \d+% Movement Speed".lower(), item['passive'].lower())
                if movementSpeedStacks:
                    amount = re.findall(r'\d+', movementSpeedStacks.group())
                    item['stacks']['stacks']['movementSpeed'] = int(amount[0])
                attackSpeedStacks = re.search(", \d+% Attack Speed".lower(), item['passive'].lower())
                if attackSpeedStacks:
                    amount = re.findall(r'\d+', attackSpeedStacks.group())
                    item['stacks']['stacks']['attackSpeed'] = int(amount[0])
                attackSpeedStacks = re.search("gain \d+% Attack Speed".lower(), item['passive'].lower())
                if attackSpeedStacks:
                    amount = re.findall(r'\d+', attackSpeedStacks.group())
                    item['stacks']['stacks']['attackSpeed'] = int(amount[0])
                criticalStrikeStacks = re.search("and \d*\.?\d+% Physical Critical Strike Chance".lower(), item['passive'].lower())
                if criticalStrikeStacks:
                    amount = re.findall(r'\d*\.?\d+', criticalStrikeStacks.group())
                    item['stacks']['stacks']['criticalChance'] = float(amount[0])
                criticalStrikeStacks = re.search("provides \d+% Critical Strike Chance".lower(), item['passive'].lower())
                if criticalStrikeStacks:
                    amount = re.findall(r'\d+', criticalStrikeStacks.group())
                    item['stacks']['stacks']['criticalChance'] = int(amount[0])
                healthStacks = re.search("gain \+\d+ Health".lower(), item['passive'].lower())
                if healthStacks:
                    amount = re.findall(r'\d+', healthStacks.group())
                    item['stacks']['stacks']['health'] = int(amount[0])
                basicAttackPercentIncreaseStacks = re.search("provides \d*\.?\d+% Increased Basic Attack Damage".lower(), item['passive'].lower())
                if basicAttackPercentIncreaseStacks:
                    amount = re.findall(r'\d*\.?\d+', basicAttackPercentIncreaseStacks.group())
                    item['stacks']['stacks']['basicAttackPercentIncreaseStacks'] = float(amount[0])

                maxStacks = re.search("max. \d+ stacks".lower(), item['passive'].lower())
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("Stacks up to \d+ times".lower(), item['passive'].lower())
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("Stack up to \d+ times".lower(), item['passive'].lower())
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("At \d+ Stacks".lower(), item['passive'].lower())
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("max of \d+ stacks".lower(), item['passive'].lower())
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("maximum of \d+ stacks".lower(), item['passive'].lower())
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])
                maxStacks = re.search("max \d+ stacks".lower(), item['passive'].lower())
                if maxStacks:
                    amount = re.findall(r'\d+', maxStacks.group())
                    item['stacks']['max'] = int(amount[0])
                    item['stacks']['current'] = int(amount[0])

                if 'consume'.lower() in item['passive'].lower() or 'Stacks last for'.lower() in item['passive'].lower() or 'Stacks are removed'.lower() in item['passive'].lower() or 'For every 100 gold you have gain'.lower() in item['passive'].lower() or 'lasts'.lower() in item['passive'].lower() or 'for 5s'.lower() in item['passive'].lower() or 'for 15 s'.lower() in item['passive'].lower():
                    item['stacks']['type'] = "temporary"
                    item['stacks']['current'] = 0

                if 'Evolves'.lower() in item['passive'].lower():
                    item['stacks']['evolved'] = { 'icon': 'images/smite/items/evolved-' + imageName}
                    coolDown = re.search("gaining \d+% Cooldown Reduction".lower(), item['passive'].lower())
                    if coolDown:
                        amount = re.findall(r'\d+', coolDown.group())
                        item['stacks']['evolved']['cooldownReduction'] = int(amount[0])
                    physicalPower = re.search("gaining \d+ Physical Power".lower(), item['passive'].lower())
                    if physicalPower:
                        amount = re.findall(r'\d+', physicalPower.group())
                        item['stacks']['evolved']['physicalPower'] = int(amount[0])
                    physicalLifesteal = re.search(", \d+% Physical Lifesteal".lower(), item['passive'].lower())
                    if physicalLifesteal:
                        amount = re.findall(r'\d+', physicalLifesteal.group())
                        item['stacks']['evolved']['physicalLifesteal'] = int(amount[0])
                    manaToMagicalPower = re.search("gaining \d+% extra Mana to Power conversion".lower(), item['passive'].lower())
                    if manaToMagicalPower:
                        amount = re.findall(r'\d+', manaToMagicalPower.group())
                        item['stacks']['evolved']['manaToMagicalPower'] = int(amount[0])
                    physicalProtection = re.search("providing an Aura of \d+ Physical Protection".lower(), item['passive'].lower())
                    if physicalProtection:
                        amount = re.findall(r'\d+', physicalProtection.group())
                        item['stacks']['evolved']['physicalProtection'] = int(amount[0])
                    magicalProtection = re.search("and \d+ Magical Protection".lower(), item['passive'].lower())
                    if magicalProtection:
                        amount = re.findall(r'\d+', magicalProtection.group())
                        item['stacks']['evolved']['magicalProtection'] = int(amount[0])

            if 'while below'.lower() in item['passive'].lower() or 'If you drop below'.lower() in item['passive'].lower() or 'Your Critical Hits provide you with'.lower() in item['passive'].lower() or 'While you are within'.lower() in item['passive'].lower() or 'after using an ability'.lower() in item['passive'].lower():
                item['toggleStats'] = { 'toggle': False }
                physicalLifestealToggle = re.search("gain an additional \d+% Physical Lifesteal".lower(), item['passive'].lower())
                if physicalLifestealToggle:
                    amount = re.findall(r'\d+', physicalLifestealToggle.group())
                    item['toggleStats']['physicalLifesteal'] = int(amount[0])
                physicalpowerToggle = re.search("provides \d+ Physical Power".lower(), item['passive'].lower())
                if physicalpowerToggle:
                    amount = re.findall(r'\d+', physicalpowerToggle.group())
                    item['toggleStats']['physicalPower'] = int(amount[0])
                attackSpeedToggle = re.search("and \d+% Attack Speed".lower(), item['passive'].lower())
                if attackSpeedToggle:
                    amount = re.findall(r'\d+', attackSpeedToggle.group())
                    item['toggleStats']['attackSpeed'] = int(amount[0])
                attackSpeedToggle = re.search(" you gain \d+% Attack Speed".lower(), item['passive'].lower())
                if attackSpeedToggle:
                    amount = re.findall(r'\d+', attackSpeedToggle.group())
                    item['toggleStats']['attackSpeed'] = int(amount[0])
                physicalPenetrationPercentToggle = re.search("provide you with \d+% Physical Penetration".lower(), item['passive'].lower())
                if physicalPenetrationPercentToggle:
                    amount = re.findall(r'\d+', physicalPenetrationPercentToggle.group())
                    item['toggleStats']['physicalPenetrationPercent'] = int(amount[0])
                attackAndMovementSpeedToggle = re.search("increase your Attack Speed and Movement Speed by \d+%".lower(), item['passive'].lower())
                if attackAndMovementSpeedToggle:
                    amount = re.findall(r'\d+', attackAndMovementSpeedToggle.group())
                    item['toggleStats']['attackSpeed'] = int(amount[0])
                    item['toggleStats']['movementSpeed'] = int(amount[0])
                basicAttackPercentIncrease = re.search("Basic Attack will deal an additional \d+% damage".lower(), item['passive'].lower())
                if basicAttackPercentIncrease:
                    amount = re.findall(r'\d+', basicAttackPercentIncrease.group())
                    item['toggleStats']['basicAttackPercentIncrease'] = int(amount[0])

            damagePercentIncrease = re.search("enemies take \d+% increased damage".lower(), item['passive'].lower())
            if damagePercentIncrease:
                item['toggleStats'] = { 'toggle': False }
                amount = re.findall(r'\d+', damagePercentIncrease.group())
                item['toggleStats']['damagePercentIncrease'] = int(amount[0])

        if sourceItem['ItemDescription']['Menuitems']:
            for sourceStat in sourceItem['ItemDescription']['Menuitems']:
                if sourceStat['Description'] == 'Basic Attack Damage':
                    item['basicAttackFlatIncrease'] = int(sourceStat['Value'][1:])
                if sourceStat['Description'] == 'Physical Power':
                    item['physicalPower'] = int(sourceStat['Value'][1:])
                    item['type'] = "Physical"
                if sourceStat['Description'] == 'Magical Power':
                    item['magicalPower'] = int(sourceStat['Value'][1:])
                    if item['type'] == 'Physical':
                        item['type'] = "Both"
                    else:
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
        
        if 'Evolved' not in item['name'] and 'REMOVE' not in item['name'] and '*' not in item['name'] and not 'shoes' in item and 'Worn' not in item['name']:
            items.append(item)

with open('items_result.json', 'w') as json_file:
    json.dump(items, json_file, indent='\t', sort_keys=True)
