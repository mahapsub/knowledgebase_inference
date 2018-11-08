import read, copy
from util import *
from logical_classes import *

verbose = 0
debug = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True
    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []





    def kb_retract(self, fact_or_rule):

        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Student code goes here

        '''
        A Fact is supported if it has both a rule and a fact for support. Same for Rule. 
        '''

        item = None
        if isinstance(fact_or_rule, Fact):
            print("RETRACT BEING CALLED: ", fact_or_rule.statement )
            item = self._get_fact(fact_or_rule)
            if item is not None and len(item.supported_by)>1:
                #Calling remove on fact, then rule infers the fact because it still has supported by
                item.asserted = False
                item = None
        elif isinstance(fact_or_rule, Rule):
            print("RETRACT BEING CALLED: ", fact_or_rule.lhs, fact_or_rule.rhs)
            item = self._get_rule(fact_or_rule)
            if item is not None and item.asserted:
                item = None

        if item is not None:
            rules_supported = item.supports_rules
            facts_supported = item.supports_facts
            nodes_to_check = []
            for rule in rules_supported:
                curr_rule = self._get_rule(rule)
                if curr_rule is not None:
                    delete_items(curr_rule, item)
                    nodes_to_check.append(curr_rule)
            for fact in facts_supported:
                curr_fact = self._get_fact(fact)
                if curr_fact is not None:
                    delete_items(curr_fact, item)
                    nodes_to_check.append(curr_fact)
            if isinstance(item, Fact):
                self.facts.remove(item)
            elif isinstance(item, Rule):
                self.rules.remove(item)

            #check if nodes are good to stay in the KB, otherwise it'll call this function recursively
            for node in nodes_to_check:

                if not check_if_node_is_valid(node):
                    print('##------NODE NOT VALID: ')
                    printHelper('****', node)
                    if isinstance(node, Fact):
                        print("%is a fact", node.statement)
                        node.asserted = True
                    elif isinstance(node, Rule):
                        print('%is a rule: ', node.lhs, node.rhs)
                    self.kb_retract(node)


def check_if_node_is_valid(fact_or_rule):
    facts = []
    rules = []
    for node in fact_or_rule.supported_by:
        if isinstance(node, Fact):
            facts.append(node)
        if isinstance(node, Rule):
            rules.append(node)

    if len(facts)==0 or len(rules)==0:
        print('---!RETRACT!---')
        printHelper("...",fact_or_rule)
        if isinstance(fact_or_rule, Fact):
            if fact_or_rule.asserted:
                return True
        return False
    # else:
    #     for fact in facts:
    #         for rule in rules:
    #             bindings = match(fact.statement, rule.lhs[0])
    #             print(bindings)




def printHelper(str, fact_or_rule):
    if isinstance(fact_or_rule, Fact):
        print(str,'printing fact:' ,fact_or_rule.statement)
    elif isinstance(fact_or_rule, Rule):
        print(str,'printing rule: ', fact_or_rule.lhs, fact_or_rule.rhs)



def delete_items(fact_or_rule, item):
    supported_list = fact_or_rule.supported_by
    for idx, l in enumerate(supported_list):
        if type(l) == type(item):
            if isinstance(l, Fact):
                if l.statement == item.statement:
                    supported_list.remove(l)
            elif isinstance(l, Rule):
                if l.lhs == item.lhs and l.rhs == item.rhs:
                    supported_list.remove(l)



class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here

        first_statement = rule.lhs[0]
        bindings = match(fact.statement, first_statement)
        if bindings:
            if len(rule.lhs)==1:
                new_fact = Fact(instantiate(rule.rhs, bindings))
                if new_fact not in kb.facts:
                    rule.supports_facts.append(new_fact)
                    fact.supports_facts.append(new_fact)
                    new_fact.supported_by.append(fact)
                    new_fact.supported_by.append(rule)
                    new_fact.asserted = False
                    kb.kb_add(new_fact)
                else:
                    fact_pointer= kb._get_fact(new_fact)
                    rule.supports_facts.append(fact_pointer)
                    fact.supports_facts.append(fact_pointer)
                    fact_pointer.supported_by.append(fact)
                    fact_pointer.supported_by.append(rule)
            else:
                left = []
                for l in rule.lhs:
                    left.append(instantiate(l, bindings))
                new_rule = Rule([left[1:], instantiate(rule.rhs, bindings)])
                rule.supports_rules.append(new_rule)
                fact.supports_rules.append(new_rule)
                new_rule.supported_by.append(fact)
                new_rule.supported_by.append(rule)
                new_rule.asserted = False
                kb.kb_add(new_rule)
