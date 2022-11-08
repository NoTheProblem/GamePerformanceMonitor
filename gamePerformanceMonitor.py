#!pip install fps_inspector_sdk
#!pip install numpy
#!pip install pandas
#!pip install pythonping

import time
import os
import psutil
import sys
import pandas as pd
import numpy
from datetime import datetime
from fps_inspector_sdk import fps_inspector
from pythonping import ping

os.system('cls')

hostDomain = 'www.facebook.com'

menuMessage = """
-----------------------------------------------------------------------
1. Monitor game.
2. Change host domain for pinging.
3. Add new supported Games.
4. Exit.
-----------------------------------------------------------------------
"""

startUpMessage = """
How to use:
1. Open game.
2. Run the game and wait for game to load.
3. Select one of suppored games by pressing number assinged to it.
4. Enjoj.
5. After session press CTRL + C in terminal to stop.
-----------------------------------------------------------------------
Enter -1 if you wanth to exit to main menu.
-----------------------------------------------------------------------
Supported games:  
"""

enterMessage = """
-----------------------------------------------------------------------
Enter game ID:  
"""

addGamesMessage = """
-----------------------------------------------------------------------

If you wanth to add new game, program requires name of .exe file that runs that game.
Few ways to find out exact name (name doesn't have to match game name you see).

-----------------------------------------------------------------------
If game doesn't start through client:
1. Right click on game icon.
2. Properties.
3. Open file location.
4. Copy name of highlighted file.
-----------------------------------------------------------------------

-----------------------------------------------------------------------
If game doesn't start through client:
1. Start game (not just client).
2. Open task menager.
3. Find game.
4. Right click -> Go to details.
5. Copy highlighted name.
-----------------------------------------------------------------------
"""

line = '-----------------------------------------------------------------------'

def addGame():
    print(line + '\nInput game name (one you will se in menu): ')
    gameName = input()
    print('Input game .exe file (one you copied, without .exe): ')
    exeName = input()
    file_object = open('SupportedGames.txt', 'a+')
    insert = '\n' +gameName + ',' + exeName +  '.exe'
    file_object.write(insert)
    file_object.close()
    os.system('cls')
    print(gameName + ' is added!')

def ping_host(host):
    ping_result = ping(target=host, count=10, timeout=2)

    return {
        'avg_latency': ping_result.rtt_avg_ms,
        'min_latency': ping_result.rtt_min_ms,
        'max_latency': ping_result.rtt_max_ms,
        'packet_loss': ping_result.packet_loss
    }

def Monitor():

    try:
        gameNames = pd.read_csv("SupportedGames.txt", sep=",", header = None)
    except:
        print(line + '\n SupportedGames.txt not found! \n Add SupportedGames.txt to same directory as program, or in main menu add new games (option 3.)')
        return

    print(startUpMessage)
    i = 0
    for game in gameNames.iloc[:,0]:
        print('Game ID: ' + str(i) + '  Game: ' + game)
        i = i + 1 
    print(enterMessage)

    gameNotFound = True

    while gameNotFound:
        gameId = input()
        try:
            gameId = int(gameId)
        except:
            print('Invalid ID!')
            return
        if gameId == -1:
            os.system('cls')
            return

        pid = 0
        PROCNAME = gameNames.iloc[gameId,1]

        for proc in psutil.process_iter():
            if proc.name() == PROCNAME:
                pid = proc.pid
                print('Game found! Enjoj! \nPress CTRL + C to stop.')
                gameNotFound = False
                break
        if gameNotFound:
            print('Game not found! Make sure game is running.')


    bandwidthDF = pd.DataFrame(columns=['Timestamp', 'RecievedMB', 'SentMB', 'TotalMB', 'avg_latency', 'min_latency', 'max_latency', 'packet_loss'])
    bandwidthDF.attrs['host_domain'] = hostDomain
    
    now = datetime.now()

    dt_string = now.strftime("%d_%m_%Y_%H_%M")

    float_formatter = lambda x: "%.5f" % x
    numpy.set_printoptions (formatter={'float_kind': float_formatter}, threshold=numpy.inf)

    last_received = psutil.net_io_counters().bytes_recv
    last_sent = psutil.net_io_counters().bytes_sent
    last_total = last_received + last_sent
    fps_inspector.start_fliprate_recording (pid)

    try:
        while True:    
            bytes_received = psutil.net_io_counters().bytes_recv
            bytes_sent = psutil.net_io_counters().bytes_sent
            bytes_total = bytes_received + bytes_sent

            new_received = bytes_received - last_received
            new_sent = bytes_sent - last_sent
            new_total = bytes_total - last_total

            mb_new_received = new_received / 1024 / 1024
            mb_new_sent = new_sent / 1024 / 1024
            mb_new_total = new_total / 1024 / 1024

            pingData = ping_host(hostDomain)

            new_row = {
            'Timestamp': time.time(), 'RecievedMB':mb_new_received, 'SentMB':mb_new_sent, 'TotalMB':mb_new_total, 
            'avg_latency': pingData['avg_latency'], 'min_latency': pingData['min_latency'], 'max_latency': pingData['max_latency'], 
            'packet_loss': pingData['packet_loss']
            }

            bandwidthDF = bandwidthDF.append(new_row, ignore_index=True)

            last_recieved = bytes_received
            last_sent = bytes_sent
            last_total = bytes_total

            time.sleep(1)

    except KeyboardInterrupt:
        pass

    print('-----------------------------------------------------------------------\nSaving data...')

    fps_inspector.stop_fliprate_recording ()
    data = fps_inspector.get_last_fliprates(100000000) # Since get_all_filprates doesnt work

    gameName = gameNames.iloc[gameId,0].replace(" ", "_")
    fileName = dt_string + '_' + gameName + '_'

    bandwidthDF.Timestamp = bandwidthDF.Timestamp.apply(lambda x: datetime.fromtimestamp(x))
    bandwidthDF.to_csv(fileName   + 'bandwidth.csv')
    os.system('cls')
    print('Bandwidth data saved.')
    data.Timestamp = data.Timestamp.apply(lambda x: datetime.fromtimestamp(x))
    data.to_csv(fileName + 'fsp.csv')
    print('FPS data saved.')


def main():
	print(menuMessage)
	menuID = input()

	while menuID != '4':
	    os.system('cls')
	    if menuID == '1':
	        Monitor()
	    if menuID == '2':   
	        os.system('cls') 
	        print(line + '\nCurrent host domain for pinging: ' + hostDomain +'\n' + line)
	        print('1. Change host domain\n2. Back to main menu\n')
	        changeHost = input()
	        if changeHost == '1':
	            print('Input new host domain:')
	            newHost = input()
	            hostDomain = newHost
	            os.system('cls')
	            print('New host domain: ' + hostDomain)
	        else:
	            os.system('cls')
	    if menuID == '3':
	        os.system('cls')
	        print(line + '\nList of supported games: ')
	        try:
	            gameNames = pd.read_csv("SupportedGames.txt", sep=",", header = None)
	            for game in gameNames.iloc[:,0]:
	            	print(game) 
	        except:
	            print('No supported games!')
	        print(addGamesMessage)
	        print(line)
	        print('1. Add new game\n2. Back to main menu\n')
	        addGameInput = input()
	        if addGameInput == '1':
	            addGame()
	        else:
	            os.system('cls')
	    print(menuMessage)
	    menuID = input()

if __name__ == "__main__":
    main()