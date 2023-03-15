from lcu_driver import Connector
import requests
import json

#pip install lcu-driver

connector = Connector()


@connector.ready
async def connect(connection):
    print('watch Date A Live')
    # print(connection.address)
    # print(connection.auth_key)
    
@connector.close
async def disconnect(_):
    print('The client has closed!')
    
#everytime your League session UPDATEs:
@connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
async def checkLockIn(connection, event):
    champion = await connection.request('get', '/lol-champ-select/v1/current-champion')
    if champion.status != 200:
        return
    
    champion = await champion.json()
    if champion > 0:
        #TODO find out who the champion Nr° ___ is
        champion = whichChampionIs(champion)
        pasteFiles(champion)

def pasteFiles(champion):
    #TODO copy the keybinds from a db or something into the PersistedSettings.json file
    print(f'copying keybinds for champion Nr°{champion}')
    
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

# Example usage
connector.start()

