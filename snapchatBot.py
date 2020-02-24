from selenium.webdriver.common.by import By

import tensorflow as tf
import Slangs.slangExtractor as slangs
import threading
import os
import time
import socket
import sys
import re

from settings import PROJECT_ROOT
from ACA.chatbot.botpredictor import BotPredictor

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'





class Extractor(object):

    def __init__(self):

        # Start Chatbot Session
        corp_dir = os.path.join(PROJECT_ROOT, 'ACA', 'Data', 'Corpus')
        knbs_dir = os.path.join(PROJECT_ROOT, 'ACA', 'Data', 'Variety')
        res_dir = os.path.join(PROJECT_ROOT, 'ACA', 'Data', 'Result')
        rules_dir = os.path.join(PROJECT_ROOT, 'ACA', 'Data', 'Rules')

        self.__init = True
        self.__sess = tf.Session()
        self.__predictor = BotPredictor(self.__sess, corpus_dir=corp_dir, knbase_dir=knbs_dir,
                                        result_dir=res_dir, aiml_dir=rules_dir,
                                        result_file='basic')
        self.__session_id = self.__predictor.session_data.add_session()
        self.reset()
        self.HOST = "localhost"
        self.PORT = 9999


    def __start_appium(self):
        '''start server appium'''
        #os.system("appium")
        os.system("start /wait cmd /c appium")


    def __execute_chat_bot(self, pwdSnap: str):
        #os.system("mvn exec:java -f " + pwdSnap)
        os.system("start /wait cmd /c mvn exec:java -f " + pwdSnap)

    def __bot_socket(self):
        print("Inciando socket")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((self.HOST, self.PORT))
        except socket.error as err:
            print('Bind failed. Error Code : '.format(err))

        s.listen(10)
        print("Socket Listening")
        #os.system("start /wait cmd /c mvn exec:java -f " + pwdSnap)
        #print("Java Listening")
        self.conn, self.addr = s.accept()
        
        

        

    def __init_conversation(self):
        initConversation = False
        start = time.time()
        with tf.Session() as sess:
            while (True):
                question = self.conn.recv(1024).decode(encoding='UTF-8')
                print(question)
                # Structe of the text  nameStager:text
                responseStranger = question.split(":")
                if not initConversation and len(question) > 0:
                    initConversation = True
                    self.__currentName = responseStranger[0]
                ans = self.__analyse(responseStranger[1])
                sys.stdout.write(responseStranger[1])
                sys.stdout.flush()
                elapsed = int(time.time() - start)
                if(elapsed>205):
                    ans = 'Bye. I have to go.'
                self.conn.send(bytes(ans + "\r\n", 'UTF-8'))
                self.__initTimeUserResponse = time.clock();
                if(ans.lower().contains("bye")):
                    break;



    def __openConnection(self):
        """__openConnection()
        """
        # Open telegram with all cache in Chrome

        self.appium = threading.Thread(target=self.__start_appium)
        self.appium.start()
        time.sleep(10)
        
        # Open socket
        self.snapchat = threading.Thread(target=self.__execute_chat_bot , args=("C:\\",))
        self.snapchat.start()

        #self.bot_sock = threading.Thread(target=self.__bot_socket())
        #self.bot_sock.start()

        self.__bot_socket()
        
        
        

        # Same variables as in file omegleBot.py
        self.__conversation = []
        self.__lenConversation = [0]
        self.__timeResponse = [0]
        self.__currentLength = 0
        self.__timeOfConversation = 0
        self.__initTimeUserResponse = 0
        self.__init = False
        self.__currentName = ''
        self.__currentUserWebElement = ''
        self.__timeOut = time.perf_counter()
        self.__limitInitMinutes = 5
        self.__limitAllMinutes = 9
        time.sleep(10)

    def __analyse(self, answer):

        words = ""
        botResponse = ":)"
        for i in range(len(answer)):
            words = answer[-1 - i].split("\n")[-1].strip() + " " + words
            print("============TEXT============")
            print(answer[-1 - i].text)
            print(self.__currentName)
        self.__currentLength = len(answer)
        if (words != ""):
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
            if botResponse.strip() != "" and botResponse is not None:
                print("DEBERIA RESPONDER")
                self.__currentLength += 1
                self.__conversation.append(words)
                self.__lenConversation.append(len(words))
                self.__timeResponse.append(self.__finalTimeUserResponse - self.__initTimeUserResponse)
        return botResponse

        # if ( time.perf_counter() - self.__timeOut > self.__limitAllMinutes*60):
        #    self.__condition.acquire()
        #    self.__condition.notify()
        #    self.__condition.release()
        #    return True
        # return False

    def moti(self):
        self.__openConnection()

    def getSess(self):
        return self.__sess

    def getSessionId(self):
        return self.__session_id

    def getPredictor(self):
        return self.__predictor

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
        self.__init = False
        self.__currentName = ''
        self.__timeOut = time.perf_counter()

    def tradeAccomplish(self, condition):
        self.__conversation = []
        self.__lenConversation = [0]
        self.__timeResponse = [0]
        self.__currentLength = 0
        self.__timeOfConversation = 0
        self.__initTimeUserResponse = 0
        self.__init = False
        self.__currentName = ''
        self.__condition = condition
        self.__timeOut = time.perf_counter()
