from lcu_driver import Connector
import requests
import json

#pip install lcu-driver

connector = Connector()
currentChampion = "nothing right now"


@connector.ready
async def connect(connection):
    print('watch Date A Live')
    print(connection.address)
    print(connection.auth_key)
    
@connector.close
async def disconnect(_):
    print('The client has closed!')
    
#everytime your League session UPDATEs: 
@connector.ws.register('/lol-gameflow/v1/gameflow-phase', event_types=('UPDATE',))
async def main(connection, event):
    await checkLockIn(connection, event.data)
    await checkPostGame(connection, event.data)
        
async def checkLockIn(connection, event):
    if event == "GameStart":
        
        #when the game starts:
        await updateChampion(connection)
        pasteFiles()
        
async def checkPostGame(connection, event):
    if event == 'EndOfGame':
        
        #when the game ends:
        copyFiles()
            
        
def pasteFiles():
    print(f'copying keybinds for champion Nr°{currentChampion}')
    #TODO copy the keybinds from a db or something into the PersistedSettings.json file
    
def copyFiles():
    with open('PersistedSettings.json', 'r') as f:
        data = json.load(f)
    
    for file in data['files']:
        if file['name'] == 'Input.ini':
            sections = {}
            for section in file['sections']:
                sections[section['name']] = section['settings']
            
            output_data = {"name": "Input.ini", "sections": []}
            for section_name in ['GameEvents', 'HUDEvents', 'Quickbinds', 'ShopEvents']:
                if section_name in sections:
                    output_data['sections'].append({"name": section_name, "settings": sections[section_name]})
            
            with open(f'{currentChampion}_settings.otto', 'w') as output_file:
                json.dump(output_data, output_file, indent=4)
                
            break
    else:
        print("Could not find section 'Input.ini' in file 'PersistedSettings.json'.")
    
    
############################### functions to clean everything ###############################
def whichChampionIs(champion_id):
    # Get the latest version of Data Dragon
    versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = requests.get(versions_url)
    versions = json.loads(response.content)
    latest_version = versions[0]

    # Get the champion data for the latest version
    url = f"http://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
    response = requests.get(url)
    champions_data = json.loads(response.content)["data"]

    # Loop through the champions data and find the champion with the matching ID
    for champion in champions_data.values():
        if int(champion["key"]) == champion_id:
            return champion["name"]

    # Return an error message if no champion with the matching ID was found
    return f"Error: Champion name not found for ID {champion_id}"

async def updateChampion(connection):    
    champion = await connection.request('get', '/lol-champ-select/v1/current-champion')
    if champion.status != 200:
        return
    
    champion = await champion.json()
    champion = whichChampionIs(champion)
        
    #update currentChampion
    global currentChampion
    currentChampion = champion
    print(f'updated current champion to: {currentChampion} / {champion}')
    
connector.start()

