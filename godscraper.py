import json
import re
from urllib.request import Request, urlopen, urlretrieve

def num(s):
    try:
        if is_int(s):
            return int(s)
        elif is_float(s):
            return float(s)
    except ValueError:
        return s

def is_int(n):
    try:
        float_n = float(n)
        int_n = int(float_n)
    except ValueError:
        return False
    else:
        return float_n == int_n

def is_float(n):
    try:
        float_n = float(n)
    except ValueError:
        return False
    else:
        return True

def getStats(sourceStat):
    if 'initial' in sourceStat:
        return 0
    if ' per shot' in sourceStat:
        sourceStat = (sourceStat.split(' per shot'))[0]
    if ' per second' in sourceStat:
        sourceStat = (sourceStat.split(' per second'))[0]
    if ' every' in sourceStat:
        sourceStat = (sourceStat.split(' every'))[0]
    if ' (' in sourceStat:
        sourceStat = (sourceStat.split(' ('))[0]
    if '%' in sourceStat:
        sourceStat = (sourceStat.split('%'))[0]
    if '+' in sourceStat:
        sourceStat = (sourceStat.split('+'))[1]
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
    # try:
    #     urlretrieve(url, 'images/abilities/' + imageName)
    # except Exception:
    #     print("could not download " + url)
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
            if 'Damage:'.lower() in rankItem['description'].lower()  and ' (' in rankItem['value']:
                stat = rankItem['value'].split(' (')
                if "damage" in ability.keys():
                    ability['damage'].append(getStats(stat[0]))
                else:
                    ability['damage'] = getStats(stat[0])
                temp = re.findall(r'\d+', stat[1])
                if len(temp) > 0:
                    ability['powerDamage'] = int(temp[0])
            elif 'Damage per '.lower() in rankItem['description'].lower():
                if not 'bonus' in rankItem['description'].lower():
                    stat = rankItem['value'].split(" (")
                    if "damage" in ability.keys():
                        ability['damage'].append(getStats(stat[0]))
                    else:
                        ability['damage'] = getStats(stat[0])
                    if len(stat) > 1:
                        temp = re.findall(r'\d+', stat[1])
                        if len(temp) > 0:
                            ability['powerDamage'] = int(temp[0])
                #ability['ticks'] = 1
            elif rankItem['description'].lower() == 'Healing:'.lower():
                toggleStats['hpFive'] = getStats(rankItem['value'])
            elif rankItem['description'].lower() == 'Movement Speed:'.lower():
                toggleStats['movementSpeed'] = getStats(rankItem['value'][:-1])
            elif rankItem['description'].lower() == 'Attack Speed:'.lower():
                toggleStats['attackSpeed'] = getStats(rankItem['value'][:-1])
            elif rankItem['description'].lower() == 'Damage Buff:'.lower():
                toggleStats['basicAttackPercentIncrease'] = getStats(
                    rankItem['value'][:-1])
            elif rankItem['description'].lower() == 'Landing Damage:'.lower() or rankItem['description'].lower() == 'Ranged Damage:'.lower():
                stat = rankItem['value'].split(" (")
                ability['secondaryDamage'] = {}
                ability['secondaryDamage']['damage'] = getStats(stat[0])
                temp = re.findall(r'\d+', stat[1])
                if len(temp) > 0:
                    ability['secondaryDamage']['powerDamage'] = int(temp[0])
            elif rankItem['description'].lower() == 'Attack Damage:'.lower():
                stat = rankItem['value'].split(" (")
                ability['damage'].append(getStats(stat[0]))
                temp = re.findall(r'\d+', stat[1])
                if len(temp) > 0:
                    ability['powerDamage'] = int(temp[0])
            elif rankItem['description'].lower() == 'Max Stacks:'.lower():
                stacks['max'] = rankItem['value']
            elif rankItem['description'].lower() == 'Bonus Power:'.lower():
                toggleStats['physicalPower'] = getStats(rankItem['value'])
            if 'Duration:'.lower() in rankItem['description'].lower() or 'Thrown:'.lower() in rankItem['description'].lower():
                #print (getStats(rankItem['value'].replace("s", "")))
                if not rankItem['description'].lower() == 'Stun Duration:'.lower():
                    if 'ticks' in ability.keys():
                        ability['ticks'].append(getStats(rankItem['value'].replace("s", "")))
                    else:
                        ability['ticks'] = [getStats(rankItem['value'].replace("s", ""))]
            #if "damage" in ability.keys(): Debug for Damage Array
                #print(ability['damage'])

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
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(request)
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
    #urlretrieve(url, 'images/gods/' + imageName)
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
    json.dump(gods, json_file, indent='\t', sort_keys=True)