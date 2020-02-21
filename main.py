from omegleBot import Extractor as omegleExtractor
#from telegramBot import Extractor as telegramExtractor
from snapchatBot import Extractor as snapExtractor
from settings import PROJECT_ROOT
from threading import Thread
import threading

import SA_Module.sentimentAnalysis as sentimentModule
import EC_Module.emotional_classifier as emotionalModule
import analytics
import Slangs.slangExtractor as slangs

import statistics
import datetime

BOTS_N = 1

def startBot( bot ):
    """ Starts the Bot ... This is created in order to start many bots in parallel"""
    bot.moti()

def saveReplies( bots ):
    """
        saveReplies: Saves all interaction that our bot manage.
    """
    # each bot interaction is stored in each name of file (in files)
    files = list()
    # Responses given by the user
    userResponses = list()
    for bot in bots:
        userResponses += bot.getConversation()
    fileName = PROJECT_ROOT + "\\UsersReplies\\" + str(datetime.datetime.now()).replace(":","_").replace("-","_").replace(" ","_").replace(".","_") + ".txt"
    files.append(fileName)        
    with open(fileName, 'w+') as file:
        for response in userResponses:
            for i in response:
                try:
                    file.write(i)
                except:
                    print("fail")
            file.write("\n")
    return(files)
        
def saveMetrics( sentiments, emotions, timeMetric, rulesMetric, files ):
    """
        saveMetrics: Store the metrics that we create.
    """
    i = 0
    for file in files:
        with open(file.replace(".txt","_Metrics.txt"), 'w+') as resultfile:
            resultfile.write("Opinion Metric,Emotion Metric,Time Metric,Rules Triggered Metric\n")
            # SENTIMENT PROPOTION
            sentResult = 0.0 if len(sentiments[i]) == 0 else statistics.mean(sentiments[i])
            # EMOTION PROPOTION
            emotResult = 0.0 if len(emotions[i]) == 0 else statistics.mean(emotions[i])
            resultfile.write( str( sentResult ) + "," + str( emotResult ) + "," + str( timeMetric[i] ) + "," + str( rulesMetric[i] ) + "\n")
        i += 1
            

def analyze( repFiles ):
    """
        Performs the sentiment analysis
    """
    # Sentiments Classfied
    sentiments = []
    # Emotions Classfied
    emotions = []
    for file in repFiles:
        # Sentiment Analysis
        try:
            sentiments.append( sentimentModule.sa_measure(file) )
        except:
            sentiments.append( [] ) 
        emotions.append( emotionalModule.ec_measure(file) )
    return sentiments, emotions

def firstImplementation():
    """
        Threads of bot, initializer.
    """
    bots = list()
    threads = list()
    for i in range(0,BOTS_N):
        a = omegleExtractor()
        bots.append(a)
        thread = Thread(target = startBot, args = (a, ))
        threads.append( thread )
    for t in threads:
        t.start()
        t.join()
    for t in threads:
        t.join()
    print("==============================================================================================================")
    # repFiles is an array with all files names
    repFiles = saveReplies(bots)
    emotionsAndSentiments = analyze(repFiles)
    metrics = analytics.getMetrics( bots )
    #saveMetrics( emotionsAndSentiments[0], emotionsAndSentiments[1], metrics, repFiles )

if __name__ == '__main__':
    snapchat = snapExtractor()
    omegle = omegleExtractor()
    while (True):
        omegle.moti(snapchat)
        tradeSnapchat = omegle.getTradeAccomplish()
        if(tradeSnapchat){
            snapchat.moti()
        }
        repFiles = saveReplies([omegle]) # Save omegle and telegram replies
        emotionsAndSentiments = analyze(repFiles)
        timeMetric, rulesMetric = analytics.getMetrics( [omegle] )
        saveMetrics( emotionsAndSentiments[0], emotionsAndSentiments[1], timeMetric, rulesMetric, repFiles )
        # OMEGLE NOTIFICATION
        omegle.reset()

"""
if __name__ == '__main__':
    telegram = telegramExtractor()
    omegle = omegleExtractor()
    threadTelegram = Thread(target = startBot, args = (telegram, ))
    threadTelegram.start()
    condition = threading.Condition()
    while (True):
        tradeTelegram = omegle.moti(telegram) 
        # TELEGRAM NOTIFICATION
        # omegle.getTradeAccomplish() # Trade Accomplish to notify telegram
        if ( tradeTelegram ):         
            # End of telegram conversation
            # Get telegram user replies
            print("========LOLACQUIRE==============")
            condition.acquire()
            print("========LOLTRADE==============")
            telegram.tradeAccomplish( condition )
            condition.wait()
            print("========LOLWAIT==============")
            condition.release()
            print("========LOL==============")
        repFiles = saveReplies([omegle,telegram]) # Save omegle and telegram replies
        emotionsAndSentiments = analyze(repFiles)
        timeMetric, rulesMetric = analytics.getMetrics( [omegle,telegram] )
        saveMetrics( emotionsAndSentiments[0], emotionsAndSentiments[1], timeMetric, rulesMetric, repFiles )
        # OMEGLE NOTIFICATION
        omegle.reset()
"""

##if __name__ == '__main__':
##    omegle = omegleExtractor()
##    while (True):
##        omegle.moti()
##        print("------> OMEGLE TRANSACTION : " + str(omegle.getTradeAccomplish()))
##        repFiles = saveReplies([omegle])
##        emotionsAndSentiments = analyze(repFiles)
##        timeMetric, rulesMetric = analytics.getMetrics( [omegle] )
##        saveMetrics( emotionsAndSentiments[0], emotionsAndSentiments[1], timeMetric, rulesMetric, repFiles )
##        omegle.reset()
