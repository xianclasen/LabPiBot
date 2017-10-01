# LabPiBot

I have a CCIE Security lab which is rather loud, and consists of several network devices and an ESXi rack server.  I have to turn off the lab at night and boot it in the morning, and often have to do this remotely.

Because I am too cheap to buy a network-capable UPS, I used some Raspberry Pi stuff I had left over from another project to flip the switch on a power-strip.  Because I'm too lazy to log in over my VPN and shut down my ESXi server manually, I leveraged the Twitter API to control the behavior of the bot through mentions.