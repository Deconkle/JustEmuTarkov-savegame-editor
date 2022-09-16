import json
from os import path, listdir
from math import ceil

root = "N:\\JET\\server"

locale_path = path.join(root,"db\\locales\\en\\locale.json")
profile_id = None # we don't know which profile to use, functions auto-choose the correct profile
locale = None

globals_path = path.join(root,'db\\base\\globals.json')

if not path.exists(path.join(root,'Server.exe')):
    print("We can't find your local JET server in the directory provided:")
    print("'"+root+"'")

# we need to know the ID of the profile we're actually trying to edit
def profile_setup():
    profiles = listdir(path.join(root,"user\\profiles\\"))
    profile = None
    if len(profiles) == 1: # if only one profile exists, we can just choose that one
        profile = profiles[0]
        return profile
    #else:
        # FINISH THIS FUNCTION
        # remember, we can read the profile ID of the last played character in server logs

if not profile_id:
    profile_id = profile_setup()

character_path = path.join(root,f"user\\profiles\\{profile_id}\\character.json")

def populate_locale():
    print("Loading locale file.")
    with open(locale_path, 'r', encoding='utf-8') as f:
        locale = json.loads(f.read())
        return locale
locale = populate_locale()

def populate_globals():
    print("Loading globals file") # <-- we wanna make sure this isn't getting called more than it's needed
    with open(globals_path, 'r', encoding='utf-8') as f:
        globals = json.loads(f.read())
        return globals
globals = populate_globals()

def query_table(table, *keys):
    item = table
    keys = list(keys)
    while keys:
        key = keys.pop(0)
        item = item[key]
    return item

def get_file_data(file_path):
    with open(file_path,'r',encoding='utf-8') as f:
        return json.loads(f.read())

def get_character_summary(profile_id):
    profiles_path = path.join(root, "user\\profiles\\")
    account_name = None
    version = None
    if not path.exists(path.join(profiles_path,profile_id)):
        print("Invalid profile_id sent to get_character_summary")
        return False
    if path.exists(path.join(profiles_path,profile_id,'accounts.json')): # <-- this is still false
        account_data = get_file_data(path.join(profiles_path,profile_id,'accounts.json'))['email']
        account_name = account_data['email']
        version = account_data['edition']
    print(account_name)

# if we want to add functions to change our level, globals.json has a nice table for that
# ['level']['exp_table'][level]['exp'] = required_xp_for_level

# this also includes weapon mastery. why? why not?
#class skills:

    # we can figure out if a skill actually does anything in globals.json
    # globals.json['data']['Mastering'] and globals.json['data']['SkillsSettings'] are very helpful

class quests:
    active_statuses = ["Started","AvailableForFinish"]
    finished_quests = ["Success","Fail"]

    def load_cur_quest_data():
        local_quests = {}
        with open(character_path, 'r', encoding='utf-8') as f:
            quests = json.loads(f.read())['Quests']
            for quest in quests:
                local_quests[quest['qid']] = {'status': quest['status']}
        return local_quests

    def get_quest_names(quests):
        quest_names = {}
        query = query_table(locale,'quest')
        for quest in quests:
            quest_name = query[quest]['name'] # 4:55AM: THIS IS SICK | 9:25AM: oh just you wait...
            quest_requirements = query[quest]['conditions']
            quest_names[quest] = quests[quest] | {"name": quest_name} | {"conditions": reversed([v for v in quest_requirements.values() if v])} # merge our dicts together
        return quest_names # {'status': 'Success', 'name': 'Ice Cream Cones', 'conditions': ['Hand over the magazines','Locate the locked bunker on Woods']}

    def print_quest_data(quest_list, status_triggers, show_conditions=False):
        longest_quest_name = len(sorted( [quest_list[quest]['name'] for quest in quest_list], key=len )[-1])
        quest_table_buffer = 2
        print("\n")
        for quests in quest_list:
            quest = quest_list[quests]
            if quest['status'] in status_triggers:
                # let's just get the printing over with, yeah..?
                print(quest['name']+(" "*(longest_quest_name-len(quest['name'])+quest_table_buffer))+'-'+quest['status']+('\n'+'\n'.join( ['['+str(k+1)+'] '+v for k,v in enumerate(quest['conditions']) ] )+'\n' if show_conditions else ""))

    #def change_quest_status(quest_name, status)

#quests.print_quest_data(quests.get_quest_names(quests.load_cur_quest_data()), quests.active_statuses)
print(quests.get_quest_names(quests.load_cur_quest_data()))


class hideout:
    def get_hideout_area_levels(): # read from database. here we get the max level of hideout areas.
        hideout_data = {}
        areas = listdir(path.join(root,"db\\hideout\\areas"))
        for area in areas:
            with open(path.join(root,"db\\hideout\\areas",area),'r', encoding='utf-8') as hideout_area:
                data = json.loads(hideout_area.read())
                hideout_data[data['type']] = {'max_level': len(data['stages'])}
        return hideout_data
    # hideout_data = { 4: {'max_level': 4}, 5: {'max_level': 1} }

    def get_local_hideout_data(data): # read from character. here we get our current hideout setup (current area levels)
        with open(character_path, 'r', encoding='utf-8') as raw:
            hideout = json.loads(raw.read())['Hideout']['Areas']
            for area in hideout:
                data[area['type']]['current_level'] = area['level']
        return data

    def get_hideout_names(data):
        for item in data:
            data[item]['name'] = query_table(locale, 'interface','hideout_area_'+str(item)+'_name')
        return data

    def populate_hideout_data():
        hideout_data = get_hideout_names(get_local_hideout_data(get_hideout_area_levels()))
        return hideout_data

    # print out our current hideout stats in a neat table
    # takes populate_hideout_data()
    def print_hideout_data(hideout_data):
        longest_area_name = len( sorted( [hideout_data[k]['name'] for k in hideout_data], key=len )[-1] ) # of all the area names, which one is the longest?
        hideout_table_buffer_length = 3
        for area in hideout_data:
            name = hideout_data[area]['name'] # areas name, ex "Medstation"
            level = ceil(hideout_data[area]['current_level'],4) # using ceil() as a massive band-aid for stash having 5 ['stages'] instead of 4
            is_max = level == hideout_data[area]['max_level']
            # print the name, ex "Medstation", followed by 19 - len('Medstation') spaces (+buffer), then we print the areas level.
            #-->                                -->                                 -->                   after that, we add the text "(MAX)" if our area is already the max level
            print(name+(" "*(longest_area_name+hideout_table_buffer_length-len(name))+"level "+str(level)+(" (MAX)" if is_max else "")))




# reminders
# don't hardcode item IDs
# instead, we can hardcode the method of finding those item IDs
# I'd like to aviod loading EVERY. SINGLE. ITEM. into memory

"""
commands:
add [rubles,euro,dollars] <amount>
get loadout (get info, top down view of currently equipped loadout)

commit (commit changes, possibly even showing a changelog) (auto back-up changed files)
rollback [latest] (roll back last changes) my god imagine buildling a changleog reverser

[get,peek,show] hideout
[change,set] hideout medstation 4

show quest(s) [default=current,all]

[set/change] profile
"""
