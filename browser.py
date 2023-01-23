import configparser
# from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from msedge.selenium_tools import Edge
from msedge.selenium_tools import EdgeOptions
import pickle
import time
import os

class Driver:
    def __init__(self,link):
        self.link = link
        # self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')
        # self.options.add_argument('--disable-gpu')
        # self.driver = webdriver.Chrome(chrome_options=self.options)
        self.options = EdgeOptions()
        self.options.add_argument('disable-gpu')
        self.driver = Edge(EdgeChromiumDriverManager().install(), options=self.options)
        self.cookies = "cookies"
        self.goWebSite()
        self.username = 0
        self.password = 0

    def setUserInfo(self):
        file = 'configfile.ini'
        config = configparser.ConfigParser()
        config.read(file)

        self.username = config['user_info']['username']
        self.password = config['user_info']['password']

    def goWebSite(self):
        if os.path.isfile(self.cookies):
            cookies = pickle.load(open(self.cookies, "rb"))
            self.driver.get(self.link)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        else:
            self.driver.get(self.link)

    def login(self):
        self.driver.implicitly_wait(10)
        element_username = self.driver.find_element("name", "username")
        self.driver.implicitly_wait(10)
        element_password = self.driver.find_element("name", "password")
        self.driver.implicitly_wait(10)

        element_username.send_keys(self.username)
        element_password.send_keys(self.password)
        self.driver.implicitly_wait(1)
        element_login = self.driver.find_element("xpath", "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]")
        element_login.click()
        self.driver.implicitly_wait(10)
        pickle.dump(self.driver.get_cookies(), open(self.cookies, "wb"))
        print(self.driver.get_cookies())

    def profile(self):
        # self.driver.get(self.link + "/" + self.username)
        self.driver.implicitly_wait(10)
        button = self.driver.find_element("xpath", "/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]")
        button.click()
        self.driver.implicitly_wait(10)
        profile_button = self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[7]/div/div/a")
        profile_button.click()
        self.driver.implicitly_wait(10)

    def scrollDown(self):
        time.sleep(2)
        jsCode = """
        page = document.querySelector("._aano");
        page.scrollTo(0, page.scrollHeight);
        var last_height = page.scrollHeight;
        return last_height 
        """
        last_height = self.driver.execute_script(jsCode)
        while True:
            new_height = last_height
            time.sleep(1)
            last_height = self.driver.execute_script(jsCode)
            if new_height == last_height:
                break
    
    def getUsers(self,xPath):
        self.scrollDown()
        user_list = []
        user_elements = self.driver.find_elements(By.XPATH, xPath)
        for user in user_elements:
            user_list.append(user.text.replace("\nDoğrulanmış",""))
        return user_list
        
    def getFollows(self):
        follows_button = self.driver.find_element("xpath", "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/ul/li[3]/a/div")
        follows_button.click()
        follows_list = self.getUsers("/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div/div[2]/div[1]/div/div/span/a/span/div")
        # print(follows_list)
        close_button = self.driver.find_element("xpath", "/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button")
        close_button.click()
        return follows_list

    def getFollowers(self):
        followers_button = self.driver.find_element("xpath", "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/ul/li[2]/a/div")
        followers_button.click()
        followers_list = self.getUsers("/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/div/div/div[2]/div[1]/div/div/span/a/span/div")
        # print(followers_list)
        close_button = self.driver.find_element("xpath", "/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button")
        close_button.click()
        return followers_list
    
    def compare(self):
        follows_list = self.getFollows()
        self.driver.implicitly_wait(10)
        followers_list = self.getFollowers()
        target_list = []
        for follow in follows_list:
            if not follow in followers_list:
                target_list.append(follow)
        print(target_list)
                
    def run(self):
        self.setUserInfo()
        self.login()
        self.profile()
        self.compare()
