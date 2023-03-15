from lcu_driver import Connector

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
    
def whichChampionIs(champion):
    return "Yoshino"
    
connector.start()

