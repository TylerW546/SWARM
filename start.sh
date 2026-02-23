screen -ls | grep '\.swarm' | awk '{print $1}' | xargs -r -I{} screen -S {} -X quit && screen -wipe;
screen -dmS swarm bash -c 'cd /home/swarm/SWARM && /usr/bin/python3 main.py';
