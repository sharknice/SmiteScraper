import json
import re
import hashlib
from urllib.request import Request, urlopen, urlretrieve
from datetime import datetime


url = "https://api.smitegame.com/smiteapi.svc/"
devId = "4278"
authKey = "9EC9E978A14745B39718310E5D6F5A25"
    
now = datetime.now()
#timestamp = now.strftime("%Y%m%d%H%M%S")
utcTime = datetime.utcnow()
timestamp = utcTime.strftime("%Y%m%d%H%M%S")

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
    if '(' in sourceStat:
        sourceStat = (sourceStat.split('('))[0]
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
            print(rankItem)
            if 'Damage:'.lower() in rankItem['description'].lower()  and ' (' in rankItem['value']:
                stat = rankItem['value'].split('(')

                if "damage" in ability.keys():
                    ability['damage'].append(getStats(stat[0]))
                else:
                    #print (stat[0])
                    ability['damage'] = getStats(stat[0])
                #print(stat[0])
                temp = re.findall(r'\d+', stat[1])
                if len(temp) > 0:
                    ability['powerDamage'] = int(temp[0])
            elif 'Damage:'.lower() in rankItem['description'].lower():
                if "of" in rankItem['value']:
                    stat = rankItem['value'].split(' of')
                else:
                    stat = [rankItem['value']]
                if "damage" in ability.keys():
                    print(stat[0])
                    print(getStats(stat[0]))
                    if isinstance(ability['damage'], int):
                        ability['damage'] = [ability['damage']]
                    ability['damage'].append(getStats(stat[0]))
                else:
                    #print (stat[0])
                    ability['damage'] = getStats(stat[0])
            elif 'Damage per '.lower() in rankItem['description'].lower():
                if not 'bonus' in rankItem['description'].lower():
                    stat = rankItem['value'].split("(")
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

def createSession():
    stringToHash = devId + "createsession" + authKey + timestamp
    signature = hashlib.md5(stringToHash.encode())
    #print(signature)
    get = (url + "createsessionjson/" + devId + "/" + signature.hexdigest() + "/" + timestamp)
    #print(get)
    request = Request(get, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(request)
    session = []
    session = [json.loads(response.read())]
    return session[0]['session_id']

def getGods():
    sessionId = createSession()
    stringToHash = devId + "getgods" + authKey + timestamp
    signature = hashlib.md5(stringToHash.encode())
    getg = (url + "getgodsjson/" + devId + "/" + signature.hexdigest() + "/" + sessionId + "/" + timestamp + "/1")
    #print(getg)
    request = Request(getg, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(request)
    godlist = []
    godlist = json.loads(response.read())
    #print(godlist)
    f = open("godApiList.json", "w")
    json.dump(godlist, f)
    f.close()
    return godlist
    

##with open('sources/gods_source.json') as f:  # https://cms.smitegame.com/wp-json/smite-api/all-gods/1
##    sourceGods = json.load(f)

gods = []
gods = getGods()
newGods = []
#print (gods)
for sourceGod in gods:
    god = {}
    name = sourceGod["Name"].strip()
    print(name)
    god['name'] = name
    god['id'] = sourceGod["id"]
    god['title'] = sourceGod['Title'].strip()
    god['pantheon'] = sourceGod['Pantheon'].strip()
    god['type'] = sourceGod['Roles'].strip()
    types = sourceGod['Type'].split(', ')
    god['attackType'] = types[0].strip()
    if len(types) > 1:
        god['powerType'] = types[1].strip()
    god['pros'] = sourceGod['Pros'].strip()
    god['health'] = sourceGod['Health']
    god['healthPerLevel'] = sourceGod['HealthPerLevel']
    god['mana'] = sourceGod['Mana']
    god['manaPerLevel'] = sourceGod['ManaPerLevel']
    god['speed'] = sourceGod['Speed']
    god['attackSpeed'] = sourceGod['AttackSpeed']
    god['attackSpeedPerLevel'] = sourceGod['AttackSpeedPerLevel'] * 100.0

    damage = sourceGod['PhysicalPower']
    damagePerLevel = sourceGod['PhysicalPowerPerLevel']
    if damage == 0:
        damage = sourceGod['MagicalPower']/5
        damagePerLevel = sourceGod['MagicalPowerPerLevel']
    god['damage'] = damage
    god['damagePerLevel'] = damagePerLevel

    god['physicalProtection'] = sourceGod['PhysicalProtection']
    god['physicalProtectionPerLevel'] = sourceGod['PhysicalProtectionPerLevel']
    god['magicalProtection'] = sourceGod['MagicProtection']
    god['magicalProtectionPerLevel'] = sourceGod['MagicProtectionPerLevel']
    god['hpFive'] = sourceGod['HealthPerFive']
    god['hpFivePerLevel'] = sourceGod['HP5PerLevel']
    god['mpFive'] = sourceGod['ManaPerFive']
    god['mpFivePerLevel'] = sourceGod['MP5PerLevel']

    url = sourceGod['godIcon_URL']
    imageName = url.rsplit('/', 1)[-1].replace('*', '')
    #urlretrieve(url, 'images/gods/' + imageName)
    god['icon'] = 'images/smite/gods/' + imageName
    #print (sourceGod['Ability_4'])

    god['passive'] = getAbilityJson(
        sourceGod['Ability_5'])
    god['abilityOne'] = getAbilityJson(
        sourceGod['Ability_1'])
    god['abilityTwo'] = getAbilityJson(
        sourceGod['Ability_2'])
    god['abilityThree'] = getAbilityJson(
        sourceGod['Ability_3'])
    god['abilityFour'] = getAbilityJson(
        sourceGod['Ability_4'])
    newGods.append(god)
with open('gods_result.json', 'w') as json_file:
    json.dump(newGods, json_file, indent='\t', sort_keys=True)
