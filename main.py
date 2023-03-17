from lcu_driver import Connector
import os
import json
import requests

# pip install lcu-driver

connector = Connector()
currentChampion = "nothing right now"
folderName = "Champion_Settings"
backupMark = " [BACKUP]"


@connector.ready
async def connect(connection):
    print('watch Date A Live')
    print(connection.address)
    print(connection.auth_key)
    
@connector.close
async def disconnect(_):
    print('The client has closed!')
    
# everytime your League session UPDATEs: 
@connector.ws.register('/lol-gameflow/v1/gameflow-phase', event_types=('UPDATE',))
async def main(connection, event):
    await checkLockIn(connection, event.data)
    await checkPostGame(connection, event.data)
        
async def checkLockIn(connection, event):
    if event == "GameStart":
        
        # when the game starts:
        await updateChampion(connection)
        pasteFiles()
        
async def checkPostGame(connection, event):
    if event == 'WaitingForStats':
        
        # when the game ends:
        copyFiles()
            
        
def pasteFiles():
    try: 
        print(f'Copying keybinds for {currentChampion}...')
        
        # all the otto settings go into the otto variable
        with open(pathToChampSetting(), 'r') as ottoSettings:
            otto = json.load(ottoSettings)

        # replace the keybind part with the ottoSettings
        with open(pathToRealSettings(), 'r') as leagueSettings:
            settings = json.load(leagueSettings)
            settings['files'][1] = otto
            #the most important bit of code!!

        # write the new data into the PersistedSettings.json
        with open(pathToRealSettings(),'w') as newSettings:
            json.dump(settings, newSettings, indent=4)

        print(f'Replaced keybinds for {currentChampion}.')
    except:
        print('File has not been created yet.')
        copyFiles(True)
    
def copyFiles(first_time=False):
    print(f'Saving keybinds for {currentChampion}...')
    # if the champion is played for the first time, it will inherit the settings from the backup file
    # i feel like it is better like this, contact me if you think otherwise
    if first_time:
        suffix = backupMark
    else:
        suffix = ''
    
    # save the settings from the PersistedSettings.json
    with open(pathToRealSettings() + suffix, 'r') as leagueSettings:
        settings = json.load(leagueSettings)
    # save the leagueSettings into a champion-specific file
    with open(pathToChampSetting(), 'w') as ottoSettings:
        json.dump(settings["files"][1], ottoSettings, indent=4)
              
    print(f"File saved as {currentChampion}_settings.otto")
    
####################### functions to clean everything up #######################
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
        
    # update currentChampion
    global currentChampion
    currentChampion = champion
    print(f'Updated current champion to: {currentChampion}.')

def setupFolder():
    try:
        os.mkdir("Champion_Settings")
    except:
        print("Folder 'Champion_Settings' exists already.")
    
def backup():
    if not os.path.isfile(pathToRealSettings() + backupMark):
        with open(pathToRealSettings() + backupMark, 'w') as backupSettings:
            with open(pathToRealSettings(), 'r') as leagueSettings:
                json.dump(json.load(leagueSettings), backupSettings, indent=4)
                # dump the leagueSettings in the backup file
                
        print('Backup succesful.')
    else:
        print('Backup exists already.')
    
def pathToChampSetting():
    return f"./{folderName}/{currentChampion}_settings.otto"

def pathToRealSettings():
    return f'./PersistedSettings.json'

setupFolder()
backup()
connector.start()

# watch Date A Live
