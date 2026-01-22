# Droomrobot

## Installation
1) Install SIC: https://socialrobotics.atlassian.net/wiki/spaces/CBSR/pages/2180415493/Getting+started
2) Clone this repository: ```git clone https://github.com/Social-AI-VU/droomrobot_python.git```
3) Follow the instructions in [```core.py```](https://github.com/Social-AI-VU/droomrobot_python/blob/main/droomrobot/core.py)

### Troubleshooting (Windows)
- ```RuntimeError: Could not start SIC on remote device```: Make sure the network you are on is marked as private. Add port 
6379 to inbound and outbound rules at Windows Defender Firewall with advanced security
- ```Failed to connect to mini device```: Add UDP ports 5353 and 6000-6010 to inbound rules at Windows Defender Firewall with advanced security
 
## Credits
_beach_waves.wav_ credits to [Benson_Arizona](https://freesound.org/people/Benson_Arizona/) at [freesound.org](https://freesound.org/). Original sound: [20250814_1150_Herm](https://freesound.org/people/Benson_Arizona/sounds/822525/)
