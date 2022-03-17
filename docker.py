import os
import requests

cloneURL = 'https://github.com/JGBMichalski/House-Hunter.git'
versionURL = 'https://raw.githubusercontent.com/JGBMichalski/House-Hunter/master/VERSION'
filesRequired = ['/House-Hunter/hunter.py', '/House-Hunter/config.yaml', '/House-Hunter/ads.json', '/House-Hunter/VERSION']

print('Running Setup...')
# Check if House-Hunter main file exists
if os.path.exists(filesRequired[0]):
    print(' - Repository exists locally.\n - Checking for updates...')

    # Get the html data from the version URL
    page = requests.get(versionURL)
    gitVersion = page.content.decode('utf-8')

    with open(filesRequired[3], "r") as versionFile:
        localVersion = versionFile.readline()

    if (gitVersion != localVersion):
        print('   - The local version is out of date.')
        print('     - Current version: {}'.format(localVersion))
        print('     - Latest version: {}'.format(gitVersion))
        print('   - It is suggested that you upgrade to the latest version.')

    print(' - Skipping setup.\n\n')
else:
    print(' - Repository does not exist locally.\n - Cloning repository into the root directory...')
    
    # Clone the repo
    os.system('git clone {} /House-Hunter'.format(cloneURL))
    
    # Verify that core files exist after the clone
    print(' - Verifying that files exist...')
    for file in filesRequired:
        if not os.path.exists(file):
            print('   - ERROR: {} not found.'.format(file))
            exit(1)
    
    print(' - All files exist.\nSetup Complete!\n\n')
