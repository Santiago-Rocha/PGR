# Copyright 2017 Bo Shao. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import nltk
import os
import string
import aiml
import tensorflow as tf
import re

from ACA.chatbot.tokenizeddata import TokenizedData
from ACA.chatbot.modelcreator import ModelCreator
from ACA.chatbot.knowledgebase import KnowledgeBase
from ACA.chatbot.sessiondata import SessionData
from ACA.chatbot.patternutils import check_patterns_and_replace
from ACA.chatbot.patternutils import remove_chars_re
from ACA.chatbot.functiondata import call_function

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
BRAIN_FILE = "brain.dump"
AIMLS_FILE = "game-theory.aiml"
EN_BLACKLIST = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\''




class BotPredictor(object):
    def __init__(self, session, corpus_dir, knbase_dir, result_dir, aiml_dir, result_file):
        """
        Args:
            session: The TensorFlow session.
            corpus_dir: Name of the folder storing corpus files and vocab information.
            knbase_dir: Name of the folder storing data files for the knowledge base.
            result_dir: The folder containing the trained result files.
            result_file: The file name of the trained model.
        """
        self.session = session

        # Prepare data and hyper parameters
        print("# Prepare dataset placeholder and hyper parameters ...")
        tokenized_data = TokenizedData(corpus_dir=corpus_dir, training=False)

        self.knowledge_base = KnowledgeBase()
        self.knowledge_base.load_knbase(knbase_dir)

        self.session_data = SessionData()

        self.hparams = tokenized_data.hparams
        self.src_placeholder = tf.placeholder(shape=[None], dtype=tf.string)
        src_dataset = tf.data.Dataset.from_tensor_slices(self.src_placeholder)
        self.infer_batch = tokenized_data.get_inference_batch(src_dataset)
        
        # Create Retrival model
        self.kmodel = aiml.Kernel()
        brain_file_name = os.path.join(aiml_dir, BRAIN_FILE)
        print(aiml_dir)

        # Match rules
        self.__numberMatchedRules = 0
        self.__totalSupectMsg = 0

        self.__terrorismPost = []

        self.__urls = []

        # Restore model rules
        """if os.path.exists(brain_file_name):
            print("# Loading from brain file ... ")
            self.kmodel.loadBrain(brain_file_name)
        else:
            print("# Parsing aiml files ...")
            aimls_file_name = os.path.join(aiml_dir, AIMLS_FILE)
            self.kmodel.bootstrap(learnFiles=os.path.abspath(aimls_file_name), commands="load aiml b")
            print("# Saving brain file: " + BRAIN_FILE)
            self.kmodel.saveBrain(brain_file_name)
        """
        # Create Generative model
        print("# Creating inference model ...")
        self.model = ModelCreator(training=False, tokenized_data=tokenized_data,
                                  batch_input=self.infer_batch)
        # Restore model weights
        print("# Restoring model weights ...")
        self.model.saver.restore(session, os.path.join(result_dir, result_file))

        self.session.run(tf.tables_initializer())

    def getNumberMatchedRules(self):
        return self.__numberMatchedRules

    def getTerrorismPost(self):
        return self.__terrorismPost

    def checkIfExistURL(self,question):
        url_tup = re.findall("(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?",question)
        if url_tup and len(url_tup[0])>=2:
            url_list = list(url_tup[0])
            defitive_url = url_list[0]+"://"+url_list[1]
            defitive_url = defitive_url + "".join(url_list[1:])
            self.__urls.append(defitive_url)

    def getSizeUrls(self):
        return len(self.__urls)

    def predict(self, session_id, question, totalTime, unitTime, idPost = -1):
        chat_session = self.session_data.get_session(session_id)
        chat_session.before_prediction()  # Reset before each prediction
        self.__totalMsgSent +=1
        if question.strip() == '':
            answer = "Don't you want to say something to me?"
            chat_session.after_prediction(question, answer)
            return answer
        self.checkIfExistURL(question);
        pat_matched, new_sentence, para_list = check_patterns_and_replace(question)
        # Preprocess question by removing undesirable characters
        retrival_question = remove_chars_re(question, EN_BLACKLIST)
        print("RETRIVAL QUST : " + "s " + retrival_question + " s")
        ##retrival_response = self.kmodel.respond("s " + retrival_question + " s")
        retrival_response = function_response(totalTime,unitTime,retrival_question)
        print("RETRIVAL ANSW : " + retrival_response)
        if 'XNOANSWER' not in retrival_response:
            self.__numberMatchedRules += 1
            print("VAN",self.__numberMatchedRules,"REGLAS")
            if 'Terrorsism:' in retrival_response:
                self.__terrorismPost.append( (question, idPost) )
                retrival_response = retrival_response[11:]
            elif 'Pervert:' in retrival_response:
                self.__terrorismPost.append( (question, idPost) )
                retrival_response = retrival_response[8:]
            elif 'Trade:' in retrival_response:
                self.__terrorismPost.append( (question, idPost) )
            return retrival_response
        for pre_time in range(2):
            tokens = nltk.word_tokenize(new_sentence.lower())
            tmp_sentence = [' '.join(tokens[:]).strip()]
            self.session.run(self.infer_batch.initializer,
                             feed_dict={self.src_placeholder: tmp_sentence})
            outputs, _ = self.model.infer(self.session)

            if self.hparams.beam_width > 0:
                outputs = outputs[0]
            eos_token = self.hparams.eos_token.encode("utf-8")
            outputs = outputs.tolist()[0]

            if eos_token in outputs:
                outputs = outputs[:outputs.index(eos_token)]
            if pat_matched and pre_time == 0:
                out_sentence, if_func_val = self._get_final_output(outputs, chat_session,
                                                                   para_list=para_list)
                if if_func_val:
                    chat_session.after_prediction(question, out_sentence)
                    return out_sentence
                else:
                    new_sentence = question
            else:
                out_sentence, _ = self._get_final_output(outputs, chat_session)
                chat_session.after_prediction(question, out_sentence)
                return out_sentence

    def _get_final_output(self, sentence, chat_session, para_list=None):
        sentence = b' '.join(sentence).decode('utf-8')
        if sentence == '':
            return "I don't know what to say.", False

        if_func_val = False
        last_word = None
        word_list = []
        for word in sentence.split(' '):
            word = word.strip()
            if not word:
                continue

            if word.startswith('_func_val_'):
                if_func_val = True
                word = call_function(word[10:], knowledge_base=self.knowledge_base,
                                     chat_session=chat_session, para_list=para_list)
                if word is None or word == '':
                    continue
            else:
                if word in self.knowledge_base.upper_words:
                    word = self.knowledge_base.upper_words[word]

                if (last_word is None or last_word in ['.', '!', '?']) and not word[0].isupper():
                    word = word.capitalize()

            if not word.startswith('\'') and word != 'n\'t' \
                and (word[0] not in string.punctuation or word in ['(', '[', '{', '``', '$']) \
                and last_word not in ['(', '[', '{', '``', '$']:
                word = ' ' + word

            word_list.append(word)
            last_word = word

        return ''.join(word_list).strip(), if_func_val

    def reset(self):
        # Match rules
        self.__numberMatchedRules = 0
        self.__terrorismPost = []
        self.__urls = []
    

    def function_response(total_time, unit_time,msg):
        rules_not_matched = self.__totalSupectMsg-self.rules_matched
        rules_value = self.rules_matched/rules_not_matched if rules_not_matched != 0 else self.rules_matched
        time_average = (total_time/unit_time)/ self.__totalSupectMsg if self.__totalSupectMsg != 0 else 0
        final_value = time_average*rules_value
        print(rules_value,time_average,final_value)
        self.kmodel = aiml.Kernel()
        self.kmodel.learn("game-theory.xml")
        if(final_value < 0.5):
            self.kmodel.respond("RHAEGAL")
        elif(final_value >= 0.5 and final_value < 2.0):
            self.kmodel.respond("VISERION")
        elif(final_value >= 2.0 and final_value < 4.0):
            self.kmodel.respond("DROGON") 
        else:
            return "XNOANSWER"
        return self.kmodel.respond(msg)

