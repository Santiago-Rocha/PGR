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
        self.length_conversation = length_conversation
        self.create_domains()
        self.create_function()
        self.create_consequent()
        self.custom_functions()
        self.define_ctrl()

    def create_domains(self):
        self.opinion_universe = np.arange(0, 1.1, 0.5)
        self.emotion_universe = np.arange(0, 1.1, 0.5)
        self.rules_universe = np.arange(0, self.length_conversation + 1)
        self.time_universe = np.arange(0, 180)
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
        self.rules['less'] = fuzz.trimf(self.rules.universe, [0, 0, self.length_conversation // 2])
        self.rules['medium'] = fuzz.trimf(self.rules.universe,
                                          [0, self.length_conversation // 2, self.length_conversation])
        self.rules['high'] = fuzz.trimf(self.rules.universe, [self.length_conversation // 2, self.length_conversation,
                                                              self.length_conversation])

    def custom_time_function_membership(self):
        self.time['high'] = fuzz.trimf(self.time.universe, [0, 90, 180])
        self.time['medium'] = fuzz.trimf(self.time.universe, [0, 90, 180])
        self.time['less'] = fuzz.trimf(self.time.universe, [90, 180, 180])

    def custom_opinion_function_membership(self):
        self.opinion['negativeO'] = fuzz.trimf(self.opinion.universe, [0.0, 0.0, 0.5])
        self.opinion['neutralO'] = fuzz.trimf(self.opinion.universe, [0.0, 0.5, 1.0])
        self.opinion['positiveO'] = fuzz.trimf(self.opinion.universe, [0.5, 1.0, 1.0])

    def custom_emotion_function_membership(self):
        self.emotion['negativeE'] = fuzz.trimf(self.emotion.universe, [0.0, 0.0, 0.5])
        self.emotion['neutralE'] = fuzz.trimf(self.emotion.universe, [0.0, 0.5, 1.0])
        self.emotion['positiveE'] = fuzz.trimf(self.emotion.universe, [0.5, 1.0, 1.0])

    def custom_suspect_function_membership(self):
        self.suspect['indifferent'] = fuzz.trimf(self.suspect.universe, [0.0, 0.0, 0.5])
        self.suspect['interested'] = fuzz.trimf(self.suspect.universe, [0.0, 0.5, 1.0])
        self.suspect['pervert'] = fuzz.trimf(self.suspect.universe, [0.5, 1.0, 1.0])

    def define_rule(self):
        rules = []
        # Pervert rules
        rules.append(
            ctrl.Rule(self.time['high'] & self.emotion['positiveE'] & self.rules['high'] & self.opinion['positiveO'],
                      self.suspect['pervert']))
        rules.append(
            ctrl.Rule(self.time['medium'] & self.emotion['positiveE'] & self.rules['high'] & self.opinion['positiveO'],
                      self.suspect['pervert']))
        rules.append(
            ctrl.Rule(self.time['less'] & self.emotion['positiveE'] & self.rules['high'] & self.opinion['positiveO'],
                      self.suspect['pervert']))
        rules.append(
            ctrl.Rule(self.time['high'] & self.emotion['positiveE'] & self.rules['less'] & self.opinion['positiveO'],
                      self.suspect['pervert']))

        rules.append(
            ctrl.Rule(self.time['high'] & self.emotion['positiveE'] & self.rules['medium'] & self.opinion['positiveO'],
                      self.suspect['pervert']))

        rules.append(
            ctrl.Rule(self.time['medium'] & self.emotion['positiveE'] & self.rules['high'] & self.opinion['positiveO'],
                      self.suspect['pervert']))

        # interested rules
        rules.append(
            ctrl.Rule(self.time['less'] & self.emotion['positiveE'] & self.rules['less'] & self.opinion['positiveO'],
                      self.suspect['interested']))
        rules.append(
            ctrl.Rule(self.time['less'] & self.emotion['positiveE'] & self.rules['high'] & self.opinion['neutralO'],
                      self.suspect['interested']))

        rules.append(
            ctrl.Rule(self.time['less'] & self.emotion['positiveE'] & self.rules['high'] & self.opinion['neutralO'],
                      self.suspect['interested']))

        rules.append(
            ctrl.Rule(self.time['high'] & self.emotion['neutralE'] & self.rules['medium'] & self.opinion['neutralO'],
                      self.suspect['interested']))

        rules.append(
            ctrl.Rule(self.time['less'] & self.emotion['neutralE'] & self.rules['medium'] & self.opinion['neutralO'],
                      self.suspect['interested']))


        # indifferent rules
        rules.append(
            ctrl.Rule(self.time['less'] & self.emotion['negativeE'] & self.rules['medium'] & self.opinion['negativeO'],
                      self.suspect['indifferent']))
        rules.append(
            ctrl.Rule(self.time['high'] & self.emotion['negativeE'] & self.rules['less'] & self.opinion['negativeO'],
                      self.suspect['indifferent']))
        rules.append(
            ctrl.Rule(self.time['less'] & self.emotion['negativeE'] & self.rules['less'] & self.opinion['negativeO'],
                      self.suspect['indifferent']))

        return ctrl.ControlSystem(rules)

    def define_ctrl(self):
        rules = self.define_rule()
        self.classification_suspect = ctrl.ControlSystemSimulation(rules)

    def set_state_metric(self, value_opinion: int, type: str):
        self.classification_suspect.input[type] = value_opinion

    def compute(self):
        self.classification_suspect.compute()

    def show(self):
        self.suspect.view(sim=self.classification_suspect)
        print(self.classification_suspect.output['suspect'])

    def show_suspect(self):
        self.suspect.view()


if __name__ == '__main__':
    classificator = Classification(110)
    classificator.set_state_metric(180, 'time')
    classificator.set_state_metric(1.0, 'emotion')
    classificator.set_state_metric(1.0, 'opinion')
    classificator.set_state_metric(110, 'rules')
    classificator.compute()
    classificator.show()
