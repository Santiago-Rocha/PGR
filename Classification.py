import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class Classification:
    """
   A class used
   :param length_conversation:
   :type length_conversation: int
   :returns: a Classification
   :rtype: Node
   """
    def __init__(self, length_conversation):
        self.length_conversation = 10
        self.create_domains()
        self.create_function()
        self.create_consequent()
        self.custom_functions()
        self.define_ctrl();

    def create_domains(self):
        self.opinion_universe = np.arange(0, 1.1, 0.5)
        self.emotion_universe = np.arange(0, 1.1, 0.5)
        self.rules_universe = np.arange(0, self.length_conversation, 1)
        self.time_universe = np.arange(0, 3, 0.2)
        self.suspect_universe = np.arange(0, 1.1, 0.5)

    def create_function(self):
        self.opinion = ctrl.Antecedent(self.opinion_universe, 'opinion')
        self.emotion = ctrl.Antecedent(self.emotion_universe, 'emotion')
        self.time = ctrl.Antecedent(self.time_universe, 'time')
        self.rules = ctrl.Antecedent(self.rules_universe, 'rules')

    def create_consequent(self):
        self.suspect = ctrl.Consequent(self.suspect_universe, 'suspect')

    def custom_functions(self):
        self.custom_emotion_function_membership()
        self.custom_opinion_function_membership()
        self.custom_rules_function_membership()
        self.custom_time_function_membership()
        self.custom_suspect_function_membership()

    def custom_rules_function_membership(self):
        self.time['less'] = fuzz.trimf(self.time.universe, [0, 0, self.length_conversation//2])
        self.time['medium'] = fuzz.trimf(self.time.universe, [0, self.length_conversation//2, self.length_conversation])
        self.time['high'] = fuzz.trimf(self.time.universe, [self.length_conversation // 2, self.length_conversation, self.length_conversation])

    def custom_time_function_membership(self):
        self.rules['high'] = fuzz.trimf(self.rules.universe, [0, 90, 180])
        self.rules['medium'] = fuzz.trimf(self.rules.universe, [0, 90, 180])
        self.rules['less'] = fuzz.trimf(self.rules.universe, [90, 180, 180])

    def custom_opinion_function_membership(self):
        self.opinion['low'] = fuzz.trimf(self.opinion.universe, [0.0, 0.0, 0.5])
        self.opinion['medium'] = fuzz.trimf(self.opinion.universe, [0.0,  0.5, 1.0])
        self.opinion['high'] = fuzz.trimf(self.opinion.universe, [0.5, 1.0, 1.0])

    def custom_emotion_function_membership(self):
        self.emotion['low'] = fuzz.trimf(self.emotion.universe, [0.0, 0.0, 0.5])
        self.emotion['medium'] = fuzz.trimf(self.emotion.universe, [0.0,  0.5, 1.0])
        self.emotion['high'] = fuzz.trimf(self.emotion.universe, [0.5, 1.0, 1.0])

    def custom_suspect_function_membership(self):
        self.suspect['low'] = fuzz.trimf(self.suspect.universe, [0.0, 0.0, 0.5])
        self.suspect['medium'] = fuzz.trimf(self.suspect.universe, [0.0,  0.5, 1.0])
        self.suspect['high'] = fuzz.trimf(self.suspect.universe, [0.5, 1.0, 1.0])

    def define_rule(self):
        rules = []
        rules.append(ctrl.Rule(self.time['high'] | self.emotion['high'] | rules['high'] | self.opinion['high'], self.suspect['high']))
        rules.append(ctrl.Rule(self.time['less'] | self.emotion['high'], self.suspect['high']))
        rules.append(ctrl.Rule(self.opinion['medium'] | self.emotion['medium'], self.time['medium'], self.suspect['medium']))
        return rules

    def define_ctrl(self):
        self.classification_suspect = ctrl.ControlSystemSimulation(self.define_rule())

    def set_state_metric(self, value_opinion : int , type : str):
        self.classification_suspect[type] = value_opinion

    def compute(self):
        self.classification_suspect.compute()





