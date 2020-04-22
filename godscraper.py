import json
import urllib.request
import re


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def getStats(sourceStat):
    if 'initial' in sourceStat:
        return 0
    if 'per shot' in sourceStat:
        sourceStat = (sourceStat.split(' per shot'))[0]
    if 'every' in sourceStat:
        sourceStat = (sourceStat.split(' every'))[0]
    if ' (' in sourceStat:
        sourceStat = (sourceStat.split(' ('))[0]
    if '%' in sourceStat:
        sourceStat = (sourceStat.split('%'))[0]
    if '/' in sourceStat:
        return [num(number) for number in sourceStat.split('/')]
    elif sourceStat.isdigit():
        return num(sourceStat)
    else:
        return 0


def getAbilityJson(sourceJson):
    ability = {}
    ability['level'] = 5
    ability['name'] = sourceJson['Summary']

    url = sourceJson['URL']
    imageName = url.rsplit('/', 1)[-1].replace('*', '')
    try:
        urllib.request.urlretrieve(url, 'images/abilities/' + imageName)
    except Exception:
        print("could not download " + url)
    ability['icon'] = 'images/smite/abilities/' + imageName

    itemDescription = sourceJson['Description']['itemDescription']
    ability['description'] = itemDescription['description']

    if itemDescription['cooldown']:
        ability['cooldown'] = getStats(itemDescription['cooldown'][:-1])
    if itemDescription['cost']:
        ability['cost'] = getStats(itemDescription['cost'])

    if itemDescription['rankitems']:
        toggleStats = {}
        stacks = {}
        for rankItem in itemDescription['rankitems']:
            if rankItem['description'] == 'Damage:' and ' (' in rankItem['value']:
                stat = rankItem['value'].split(' (')
                ability['damage'] = getStats(stat[0])
                temp = re.findall(r'\d+', stat[1])
                if len(temp) > 0:
                    ability['powerDamage'] = int(temp[0])
            elif rankItem['description'] == 'Damage per Tick:':
                stat = rankItem['value'].split(" (")
                ability['damage'] = getStats(stat[0])
                temp = re.findall(r'\d+', stat[1])
                if len(temp) > 0:
                    ability['powerDamage'] = int(temp[0])
                ability['ticks'] = 1
            elif rankItem['description'] == 'Healing:':
                toggleStats['hpFive'] = getStats(rankItem['value'])
            elif rankItem['description'] == 'Movement Speed:':
                toggleStats['movementSpeed'] = getStats(rankItem['value'][:-1])
            elif rankItem['description'] == 'Attack Speed:':
                toggleStats['attackSpeed'] = getStats(rankItem['value'][:-1])
            elif rankItem['description'] == 'Damage Buff:':
                toggleStats['basicAttackPercentIncrease'] = getStats(
                    rankItem['value'][:-1])
            elif rankItem['description'] == 'Landing Damage:' or rankItem['description'] == 'Ranged Damage:':
                stat = rankItem['value'].split(" (")
                ability['secondaryDamage'] = {}
                ability['secondaryDamage']['damage'] = getStats(stat[0])
                temp = re.findall(r'\d+', stat[1])
                if len(temp) > 0:
                    ability['secondaryDamage']['powerDamage'] = int(temp[0])
            elif rankItem['description'] == 'Attack Damage:':
                stat = rankItem['value'].split(" (")
                ability['damage'] = getStats(stat[0])
                temp = re.findall(r'\d+', stat[1])
                if len(temp) > 0:
                    ability['powerDamage'] = int(temp[0])
            elif rankItem['description'] == 'Max Stacks:':
                stacks['max'] = rankItem['value']
            elif rankItem['description'] == 'Bonus Power:':
                toggleStats['physicalPower'] = getStats(rankItem['value'])

        if stacks:
            stacks['current'] = 0
            stacks['stacks'] = toggleStats
            ability['stacks'] = stacks
        elif toggleStats:
            toggleStats['toggle'] = False
            ability['toggleStats'] = toggleStats

    return ability


with open('sources/gods_source.json') as f:  # https://cms.smitegame.com/wp-json/smite-api/all-gods/1
    sourceGods = json.load(f)

gods = []
for sourceGod in sourceGods:
    god = {}
    name = sourceGod['name'].strip()
    print(name)
    god['name'] = name
    god['id'] = sourceGod['id']
    god['title'] = sourceGod['title'].strip()
    god['pantheon'] = sourceGod['pantheon'].strip()
    god['type'] = sourceGod['role'].strip()
    types = sourceGod['type'].split(', ')
    god['attackType'] = types[0].strip()
    if len(types) > 1:
        god['powerType'] = types[1].strip()

    # load the god specific json
    url = 'https://cms.smitegame.com/wp-json/wp/v2/gods?slug=' + \
        name.replace(' ', '-') + '&lang_id=1'
    response = urllib.request.urlopen(url)
    godData = json.loads(response.read())[0]['api_information']
    # set the specific data
    god['pros'] = godData['Pros'].strip()
    god['health'] = godData['Health']
    god['healthPerLevel'] = godData['HealthPerLevel']
    god['mana'] = godData['Mana']
    god['manaPerLevel'] = godData['ManaPerLevel']
    god['speed'] = godData['Speed']
    god['attackSpeed'] = godData['AttackSpeed']
    god['attackSpeedPerLevel'] = godData['AttackSpeedPerLevel'] * 100.0

    damage = godData['PhysicalPower']
    damagePerLevel = godData['PhysicalPowerPerLevel']
    if damage == 0:
        damage = godData['MagicalPower']/5
        damagePerLevel = godData['MagicalPowerPerLevel']
    god['damage'] = damage
    god['damagePerLevel'] = damagePerLevel

    god['physicalProtection'] = godData['PhysicalProtection']
    god['physicalProtectionPerLevel'] = godData['PhysicalProtectionPerLevel']
    god['magicalProtection'] = godData['MagicProtection']
    god['magicalProtectionPerLevel'] = godData['MagicProtectionPerLevel']
    god['hpFive'] = godData['HealthPerFive']
    god['hpFivePerLevel'] = godData['HP5PerLevel']
    god['mpFive'] = godData['ManaPerFive']
    god['mpFivePerLevel'] = godData['MP5PerLevel']

    url = godData['godIcon_URL']
    imageName = url.rsplit('/', 1)[-1].replace('*', '')
    urllib.request.urlretrieve(url, 'images/gods/' + imageName)
    god['icon'] = 'images/smite/gods/' + imageName

    god['passive'] = getAbilityJson(
        godData['Ability_5'])
    god['abilityOne'] = getAbilityJson(
        godData['Ability_1'])
    god['abilityTwo'] = getAbilityJson(
        godData['Ability_2'])
    god['abilityThree'] = getAbilityJson(
        godData['Ability_3'])
    god['abilityFour'] = getAbilityJson(
        godData['Ability_4'])

    gods.append(god)

with open('gods_result.json', 'w') as json_file:
    json.dump(gods, json_file)
