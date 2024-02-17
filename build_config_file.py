import configparser

config = configparser.ConfigParser()

config.add_section('user_info')
config.set('user_info', 'username', 'your-username')
config.set('user_info', 'password', 'your-password')
config.set('user_info', 'looking_username', 'looking-username')

with open("config/config_file.ini", 'w') as configfile:
    config.write(configfile)