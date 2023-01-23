import configparser

config = configparser.ConfigParser()

config.add_section('user_info')
config.set('user_info', 'username', 'your-username')
config.set('user_info', 'password', 'your-password')

with open("configfile.ini", 'w') as configfile:
    config.write(configfile)