from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from collections import deque

from selenium.webdriver.chrome.options import Options

import os
import time
import gc
import tensorflow as tf
import Slangs.slangExtractor as slangs

from settings import PROJECT_ROOT
from ACA.chatbot.botpredictor import BotPredictor

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class Extractor(object):

    def __init__(self):

        self.__init = True
        

    def __openConnection(self):
        """__openConnection()

        """
        # Start Chatbot Session
        corp_dir = os.path.join(PROJECT_ROOT, 'ACA', 'Data', 'Corpus')
        knbs_dir = os.path.join(PROJECT_ROOT, 'ACA', 'Data', 'Variety')
        res_dir = os.path.join(PROJECT_ROOT, 'ACA', 'Data', 'Result')
        rules_dir = os.path.join(PROJECT_ROOT, 'ACA', 'Data', 'Rules')

        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=C:/Users/sebastian.moreno-r/AppData/Local/Google/Chrome/User Data") # change to profile path
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--profile-directory=Default')

        self.__driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)
        self.__driver.get("https://web.telegram.org/#/im")
        
        if ( self.__init ):
            self.__sess = tf.Session()
            self.__predictor = BotPredictor(self.__sess, corpus_dir=corp_dir, knbase_dir=knbs_dir,
                                    result_dir=res_dir, aiml_dir=rules_dir,
                                    result_file='basic')
        self.__session_id = self.__predictor.session_data.add_session()
        self.__conversation = []
        self.__lenConversation = [0]
        self.__timeResponse = [0]
        self.__currentLength = 0
        self.__timeOfConversation = 0
        self.__initTimeUserResponse = 0
        self.__init = False
        self.__currentName = ''
        self.__currentUserWebElement = ''

        time.sleep(10)


        # self.__login()
        self.__response()

    def __response(self):
        while (True):
            time.sleep(5)
            try:
                inputs = self.__driver.find_element_by_xpath("//ul[contains(@class,'nav nav-pills nav-stacked')]")
                inputs = inputs.find_elements(By.XPATH, "//li[contains(@class, 'im_dialog_wrap')]")
                print(len(inputs))
                break
            except:
                print("lol_response")
        
        while (True):
            time.sleep(5)
            for i in inputs:
                name = i.find_element_by_xpath("//div[contains(@class,'im_dialog_peer')]")
                data = i.text.split("\n")
                if ( len(data) > 3 and str.isdigit(data[1]) ): 
                    print("==================LOL=======================")
                    self.__timeOfConversation = time.clock()
                    i.find_element_by_xpath("//div[contains(@class,'im_dialog_message_wrap')]").click()
                    self.__currentName = data[2]
                    first = True ; first_time = time.clock()
                    time.sleep(4)
                    while(True):
                        try:
                            time.sleep(3)
                            end = self.responseCurrentWindow(  )
                            if( end): break
                        except:
                            print("=======================TEST1==========================")
                        time.sleep(2)
                    break
                    #self.__driver.quit()

    def responseCurrentWindow(self):
        firstInputs = self.__driver.find_elements(By.XPATH, "//div[contains(@class, 'im_history_message_wrap')]")
        if ( self.__currentLength < len(firstInputs) ):
            print("==========================ENTRA LOL===================================")
            self.__currentLength = len(firstInputs)
            time.sleep(3)
            while ( True ):
                try:
                    noDeberia = self.__driver.find_elements(By.XPATH, "//span[contains(@my-i18n-format, 'im_one_typing')]")
                    print(noDeberia.get_attribute('innerHTML'))
                    time.sleep(3)
                except:
                    firstInputs = self.__driver.find_elements(By.XPATH, "//div[contains(@class, 'im_history_message_wrap')]")
                    words = ""
                    for i in range(len(firstInputs)):
                        words = firstInputs[-1-i].text.split("\n")[-1].strip() + " " + words
                        print("============TEXT============")
                        print(firstInputs[-1-i].text)
                        print(self.__currentName)
                        if ( firstInputs[-1-i].get_attribute("class") == "im_history_message_wrap" ):
                            if ( "Zek" in firstInputs[-1-i].text ):
                                words = ""
                            break
                    self.__currentLength = len(firstInputs)
                    break
                time.sleep(5)

            self.__initTimeUserResponse = 0

        if ( words != "" ):
            # Bot Response
            self.__finalTimeUserResponse = time.perf_counter()
            for key, value in slangs.getSlangs().items():
                words = words.replace(" " + key + " ", " " + value + " ")
            print("=======================WORDS==========================")
            print(words)
            print("=======================WORDS==========================")
            botResponse = self.__predictor.predict(self.__session_id, words.lower(), len(self.__conversation))
            print("===========BOT RESPONSE===========")
            print(botResponse)
            print("===========BOT RESPONSE===========")
            if ( botResponse.strip() != "" and botResponse != None ): 
                print("DEBERIA RESPONDER")
                self.__currentLength += 1
                self.__conversation.append(words)
                self.__lenConversation.append( len(words) )
                self.__timeResponse.append( self.__finalTimeUserResponse - self.__initTimeUserResponse )
                textarea = self.__driver.find_element_by_xpath("//div[contains(@class,'composer_rich_textarea')]")

                for i in botResponse:
                    time.sleep(0.05)
                    print(i)
                    textarea.send_keys(i)
                self.__driver.find_element_by_xpath("//button[contains(@class, 'btn btn-md im_submit im_submit_send')]").click()
        else:
            print("========LOL============")
        if ( time.perf_counter() - self.__timeOfConversation > 5*60):
            return True
        return False

    def __login(self):
        indicative = self.__driver.find_element_by_xpath("//input[contains(@name,'phone_number')]")
        number = self.__driver.find_element_by_xpath("//input[contains(@name,'phone_number')]")
        number.send_keys("3214894348")
        self.__driver.find_element_by_xpath("//a[contains(@class,'login_head_submit_btn')]").click()
        self.__driver.find_element_by_xpath("//button[contains(@class,'btn btn-md btn-md-primary')]").click()
        while (True):
            time.sleep(5)
            try:
                number = self.__driver.find_element_by_xpath("//input[contains(@name,'phone_code')]")
                print("SALE")
                break
            except:
                print("lol")
    
    def moti(self):
        self.__openConnection()

    def getConversation(self):
        return self.__conversation

    def getTimeOfConversation(self):
        return self.__timeOfConversation

    def getTimeEachResponse(self):
        return self.__timeResponse 

    def getNumberRulesMatched(self):
        return self.__predictor.getNumberMatchedRules()

    def getLenEachPost(self):
        return self.__lenConversation

    def getNumberOfInteractions(self):
        return len(self.__conversation)

    def reset(self):
        self.__conversation = []
        self.__lenConversation = [0]
        self.__timeResponse = [0]
        self.__currentLength = 0
        self.__timeOfConversation = 0
        self.__initTimeUserResponse = 0
    
    def tradeAccomplish(self):
        self.__conversation = []
        self.__lenConversation = [0]
        self.__timeResponse = [0]
        self.__currentLength = 0
        self.__timeOfConversation = 0
        self.__initTimeUserResponse = 0
        self.__init = False
        self.__currentName = ''

    def blockUser(self):
        self.__driver.find_element_by_xpath("//a[contains(@class,'pull-right im_panel_peer_photo peer_photo_init')]").click()
        time.sleep(3)
        self.__driver.find_element_by_xpath("//a[contains(@class,'md_modal_section_link')]").click()

a = Extractor()
a.moti()