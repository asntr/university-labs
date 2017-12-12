from PyQt5.QtWidgets import QInputDialog


class Analyzer(object):
    def __init__(self, rules, target, possible_values):
        self.rules = rules
        self.target = target
        self.possible_values = possible_values

    def check_for_rule(self, target, rules):
        for rule in rules:
            if target in rule['conclusion'] and self.target not in rule['conditions']:
                return rule, id(rule)
        return None, None

    @staticmethod
    def check_rule(rule, context):
        for key in rule['conditions'].keys():
            if key not in context:
                return None, key
        rule_is_met = all([value == context[key] for key, value in rule['conditions'].items()])
        return rule_is_met, None

    def ask_question(self, key):
        answer, clicked = QInputDialog.getItem(None, key, 'What is the value of attribute "{}"?'.format(key), self.possible_values[key])
        if clicked:
            return answer
        return None

    def analyze(self):
        context = {}
        rules = [rule for rule in self.rules]
        targets = [(self.target, None)]

        while True:
            target, rule = targets[-1]
            rule_for_target, rule_id = self.check_for_rule(target, rules)

            if not rule_for_target:
                targets.pop()
                if target == self.target:
                    break
                answer = self.ask_question(target)
                context[target] = answer
                if rule:
                    rule_for_target = next(filter(lambda x: id(x) == rule, self.rules))
                    rule_id = rule
            if rule_for_target:
                rule_condition, failed_feature = Analyzer.check_rule(rule_for_target, context)
                if rule_condition is None:
                    targets.append((failed_feature, rule_id))
                    continue
                elif rule_condition:
                    targets.pop()
                    context.update(rule_for_target['conclusion'])
                    if not targets:
                        break
                rules = list(filter(lambda x: id(x) != rule_id, rules))

        return context.get(self.target)
