import subprocess
import re
from subprocess import check_output
import time

def StatuscheckVPN():
    print('\033[4m' + "Let's get this VPN party started.\n" + '\033[0m')
    nord_output = subprocess.Popen(["nordvpn", "status"], stdout=subprocess.PIPE)
    status = re.split('[\r \n :]', nord_output.communicate()[0].decode("utf-8"))[-2]

    if status == "Disconnected":
        print("You are not connected to NordVPN. Don't worry, I'll set you up!")
        pass
    else:
        print("You are already connected to NordVPN. I'm going to reset your connection...")
        subprocess.call(["nordvpn", "disconnect"], stdout=subprocess.DEVNULL)
        pass

    geolocation = input("Which country do you want to connect to:\n")
    print("\nNice, " + "\033[1m" + geolocation + "\033[0m" + " ,got it! Let's see...")
    initial_server = check_output(["nordvpn", "c", geolocation])
    check_server = re.search('(?<=You are connected to )(.*)(?=\()', str(initial_server))[0].strip()
    print("Ok, let's start here: " '\033[4m' + check_server + '\033[0m')
    print("##########################")
    return geolocation

def VPNrotate(geolocation):
    while True:
        failed_attempt = 0
        retry = 0
        print("\nI'm picking another random server in " + "\033[1m" + geolocation + "\033[0m" + " as we speak...\n")
        newconnect_output = check_output(["nordvpn", "c", geolocation])
        check_server = re.search('(?<=You are connected to )(.*)(?=\()', str(newconnect_output))[0].strip()
        print("I found a neat server for you! It's called " + '\033[4m' + check_server + '\033[0m' + "\n")

        while True:
            print("\033[1m" + "Testing connection..." + "\033[0m")
            check_connection = check_output(["ping","-c","1","google.com"])

            if '0% packet loss' in str(check_connection):
                print("Pinged google.com with success; your connection works!")
                print("##########################")
                break
            else:
                print("Something is wrong here, I'm gonna wait 30 seconds and try a different server...")
                time.sleep(30)
                failed_attempt = failed_attempt + 1
                if failed_attempt > 2:
                    print("Sorry, the connection seems broken....")
                    raise Exception("VPN seems to be down!\n")
                    print("##########################")
                else:
                    retry = 1
                    break
        if retry == 1:
            continue
        else:
            break