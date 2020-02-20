from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from collections import deque
from sys import stdin

import os
import time
import gc
import tensorflow as tf
import SA_Module.sentimentAnalysis as sentimentModule
import analytics as analize
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

        self.__driver = webdriver.Chrome('chromedriver', port=8080)    
        time.sleep(10)
        print("===============================================")
        print("===============================================")
        print("===============================================")
        self.__driver.get("https://www.omegle.com")

        # Stores the convesrsation, user replies
        self.__conversation = []
        # Length of the conversation, only user replies
        self.__lenConversation = [0]
        # Time responses, to analize the metrics
        self.__timeResponse = [0]
        # Current length of the conversation, to make controls
        self.__currentLength = 0
        self.__timeOfConversation = 0
        # Time limit - between initial user response and bot response 
        # if initTimeUserResponse > 5 min breaks
        self.__initTimeUserResponse = 0
        self.__init = False
        userResponse = False
        self.__tradeAccomplish = False

        # Setting Topics
        topics = self.__driver.find_element_by_xpath("//input[contains(@class,'newtopicinput')]")
        topics.send_keys("sex")
        time.sleep(4)
        self.__driver.find_element_by_xpath("//img[contains(@id, 'textbtn')]").click()
        first = True ; first_time = time.clock()
        time.sleep(4)
        
        # Bot init

        while(True):
            if (self.__tradeAccomplish) :
                break
            if ( (time.clock() - first_time)/60 >= 25 ):
                break
            print("=======================TEST3============================") 
            try:
                i = 0
                while ( i < 10 ):
                    self.__driver.find_element_by_xpath("//textarea[contains(@class,'chatmsg disabled')]")
                    i += 1
                    #time.sleep(2)
                    print("esperando")
                    stdin.readline()
                    
                # Analize Data - Conversation Ended
                self.__timeOfConversation = time.clock() - first_time
                print("=================================================SALIO==============================================")
                #self.__driver.find_element_by_xpath("//button[contains(@class, 'disconnectbtn')]").click()
                break
            except :
                try:
                    print("=======================TEST============================") 
                    try:
                        time.sleep(3)
                        self.response( userResponse )
                    except:
                        print("=======================TEST1============================")
                except:
                    print("=======================BREAK============================")
                    break
                if (first):
                    first_time = time.clock()
                    first = False
            time.sleep(2)
        self.__driver.quit()
        return self.__tradeAccomplish
        
    def response(self, userResponse):
        """
            Calculates the response of a reply
        """
        inputs = self.__driver.find_elements(By.XPATH, "//div[contains(@class, 'logitem')]/p[contains(@class, 'msg')]")
        words = ""
        if ( self.__currentLength < len(inputs) ):
            self.__currentLength = len(inputs)
            time.sleep(3)
            while ( "Stranger is typing" in inputs[-1].text ):
                time.sleep(5)
                inputs = self.__driver.find_elements(By.XPATH, "//div[contains(@class, 'logitem')]/p[contains(@class, 'msg')]")
                self.__currentLength = len(inputs)

            for i in range( 0, len(inputs) ):
                if ( "Stranger" in inputs[ len(inputs) - i - 1 ].text ):
                    words = inputs[ len(inputs) - i - 1 ].text[9:] + " " + words
                else:
                    break

            self.__initTimeUserResponse = 0

        if ( words != "" ):
            # Bot Response
            self.__finalTimeUserResponse = time.clock()
            for key, value in slangs.getSlangs().items():
                words = words.replace(" " + key + " ", " " + value + " ")
            print(words)
            botResponse = self.__predictor.predict(self.__session_id, words.lower(), len(self.__conversation))
            if 'Trade:' in botResponse:
                self.__tradeAccomplish = True
                botResponse = botResponse[6:]
            print("FINAL ASW : " + botResponse)
            if ( botResponse.strip() != "" and botResponse != None ): 
                self.__currentLength += 1
                self.__conversation.append(words)
                self.__lenConversation.append( len(words) )
                self.__timeResponse.append( self.__finalTimeUserResponse - self.__initTimeUserResponse )
                textarea = self.__driver.find_element_by_xpath("//textarea[contains(@class,'chatmsg')]")
                for i in botResponse:
                    time.sleep(0.05)
                    textarea.send_keys(i)
                self.__driver.find_element_by_xpath("//button[contains(@class, 'sendbtn')]").click()
            
        elif ( self.__currentLength == 0 ): 
            textarea = self.__driver.find_element_by_xpath("//textarea[contains(@class,'chatmsg')]")
            textarea.send_keys("Hi")
            self.__driver.find_element_by_xpath("//button[contains(@class, 'sendbtn')]").click()
            self.__currentLength += 1
            self.__finalTimeUserResponse = time.clock()

    def moti(self, telegramBot):
        self.__sess = telegramBot.getSess()
        self.__predictor = telegramBot.getPredictor()
        self.__session_id = telegramBot.getSessionId()
        print(self.__sess)
        print(self.__predictor)
        print(self.__session_id)
        return self.__openConnection()

    def getTradeAccomplish(self):
        return self.__tradeAccomplish

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
