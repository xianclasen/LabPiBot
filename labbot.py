#!/usr/bin/env python
'''
A simple Python Twitter bot for managing power in my CCIE lab.
Will accept control messages from a specific Twitter account in the form of mentions.

Author: Christian Clasen
'''

import datetime
import logging
import subprocess
import time
import mentionlib
import Robot

robot = Robot.Robot()

# Open an SSH connection to the ESXI host and issue the 'poweroff' command
def shutdown():
    ssh = subprocess.Popen(["ssh", "root@esxi", "poweroff"],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)


def ping(host):
    proc = subprocess.Popen(["ping -c 1 " + host],
                            stdout=subprocess.PIPE,
                            shell=True)
    (out, err) = proc.communicate()
    return out


# Power on the lab via the power strip
def switch_on():
    try:
        robot.forward(255, .5)
        logging.info(humantime + ': Told the robot to switch the lab on.')
    except:
        logging.exception('Got exception on switch_on.')
        raise

# Power off the lab via the power strip
def switch_off():
    try:
        robot.backward(255, .5)
        logging.info(humantime + ': Told the robot to switch the lab off.')
    except:
        logging.exception('Got exception on switch_off.')
        raise


# Set up logging
logging.basicConfig(filename='./labbot.log', level=logging.INFO)

# Initialize the last mention ID
lastmentionjson = mentionlib.getlastmentionjson()
lastmentiondict = mentionlib.parsementionjson(lastmentionjson)
initmentionid = mentionlib.initmentionid(lastmentiondict)
logging.debug("Initial mention ID: " + str(initmentionid))

if __name__ == '__main__':
    while True:
        try:

            # Variables for timestamp
            epochtime = time.time()
            humantime = datetime.datetime.fromtimestamp(epochtime).strftime('%Y-%m-%d %H:%M:%S')

            # Wait 60 seconds between polls to avoid Twitter's API rate limit
            time.sleep(60)

            # Setup the last mention variables
            lastmentionjson = mentionlib.getlastmentionjson()
            lastmentiondict = mentionlib.parsementionjson(lastmentionjson)
            lastmentionscreenname = mentionlib.getmentionscreenname(lastmentiondict)
            lastmentionid = mentionlib.getlastmentionid(lastmentiondict)
            lastmentiontext = mentionlib.getlastmentiontext(lastmentiondict)
            mentionerstatus = mentionlib.verifymentioner(lastmentionscreenname)
            idstatus = mentionlib.verifymentionid(lastmentionid, initmentionid)

            logging.debug('Last mention ID: ' + str(lastmentionid) + ' Last mention text: ' + str(lastmentiontext))

            # If the mentioner is allowed, and the ID is new
            if (mentionerstatus == 'Verified') and (idstatus == 'Verified'):

                # Log who issued us what command
                logging.info(humantime + ': ' + lastmentionscreenname + ' issued us the following command: ' + lastmentiontext)

                # Reinitialize the ID
                initmentionid = lastmentionid

                # Answer a basic health check query
                if '@LabPiBot Hello' in lastmentiontext:

                    mantionlib.createtweet("@XianClasen Is it me you're looking for? " + humantime)

                # Switch on the lab
                elif '@LabPiBot Poweron' in lastmentiontext:

                    switch_on()
                    mentionlib.createtweet('@XianClasen I switched the lab on.  Give me some time to verify that it worked. ' + humantime)
                    logging.info(humantime + ': Tweet created: I switched the lab on.  Give me some time to verify that it worked.')

                    i = 0
                    hostisup = False
                    while not hostisup:

                        time.sleep(30)
                        i = i + 1

                        if '1 receive' in ping('esxi'):
                            hostisup = True
                            logging.info(humantime + 'Got a ping reply from esxi.')

                        elif i > 20:
                            mentionlib.createtweet("@XianClasen I have failed you.  The lab isn't up. " + humantime)
                            logging.info(humantime + ": Tweet created: I have failed you.  The lab isn't up.")
                            break

                    if hostisup:
                        mentionlib.createtweet('@XianClasen I verified that the lab is up. ' + humantime)
                        logging.info(humantime + ': Tweet created: I verified that the lab is up. ')

                # Shutdown and switchoff the lab
                elif '@LabPiBot Poweroff' in lastmentiontext:

                    shutdown()
                    mentionlib.createtweet("@XianClasen I told ESXI to shutdown.  I'll let you know when I've switched off the power. " + humantime)
                    logging.info(humantime + ": Tweet created: I told ESXI to shutdown.  I'll let you know when I've switched off the power.")

                    # Ping ESXI until it stops responding, or we reach 10 minutes
                    hostisup = True
                    i = 0

                    while hostisup:

                        i = i + 1
                        time.sleep(30)

                        if ('0 receive' in ping('esxi')) or (i > 20):
                            hostisup = False

                    # Turn off the power
                    logging.info(humantime + ': Switching off the power now.')
                    switch_off()
                    mentionlib.createtweet("@XianClasen I've switched off the power. " + humantime)

            # In case the mentioner isn't trusted
            elif mentionerstatus == 'Unverified':

                logging.warning(lastmentionscreenname + ' tried to issue us the following command: ' + lastmentiontext)
                print(lastmentionscreenname + ' tried to issue us the following command: ' + lastmentiontext)
                mentionlib.createtweet("@" + lastmentionscreenname + " You didn't say the magic word! " + humantime)
                logging.info(humantime + ": Tweet created: " + lastmentionscreenname + " You didn't say the magic word!")

                # Reinitialize the last mention ID
                initmentionid = lastmentionid

        except:
            logging.exception('Got exception on main program.')
            raise
