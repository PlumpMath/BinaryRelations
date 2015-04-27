from enum import Enum
from .decorators import requires_int_or_bool, requires_bool
import math
import os
#   Example: "[12,14,15,26]$[%10%3| <= |/10%3]@[/10%3| >= |%10%3]$[ not @ ]$[ and @...]"
#   Elements: 12, 14, 15, 26
#   Triplets: ab%10%3 <= cd/10%3
#             ab/10%3 >= cd%10%3
#   UnaryMods: not ab%10%3 <= cd/10%3; ab/10%3 >= cd%10%3
#   BinaryRel: and
#   $ between Elements, Triplets, UnaryMods, BinaryRels
#   @ between elements of array of triplets, unaryMods, BinaryRels
#   | between parts of each triplet
#   Object to ^
#   Object to human-readable


class UnaryRelation(Enum):
    unary_not = ' not '
    unary_neutral = ' '

    @requires_bool
    def apply_unary_relation(self, argument):
        """
        :rtype:
        :param argument: boolean to apply unary operation to
        :return: argument itself
        """
        if self == UnaryRelation.unary_not:
            return not argument
        else:
            return argument

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()


class BinaryRelation(Enum):
    equal = ' == '
    less_than = ' < '
    greater_than = ' > '
    less_than_or_equal = ' <= '
    greater_than_or_equal = ' >= '
    not_equal = ' != '
    logic_or = ' or '
    logic_and = ' and '
    logic_xor = ' ^ '

    @requires_int_or_bool
    def apply_binary_relation(self, value1, value2):
        expression = str(value1) + self.value + str(value2)
        return eval(expression)

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()


class RelationElement:
    def __init__(self, element, modifier):
        self.element = element
        self.modifier = modifier

    def get_modified(self):
        expression = str(self.element) + self.modifier
        return math.trunc(eval(expression))


class RelationTriplet:
    def __init__(self, mod1, rel, mod2):
        self.mod1 = mod1  # String
        self.relation = rel  # BinaryRelation
        self.mod2 = mod2  # String

    def check(self, val1, val2):
        elem1 = RelationElement(val1, self.mod1).get_modified()
        elem2 = RelationElement(val2, self.mod2).get_modified()
        return self.relation.apply_binary_relation(elem1, elem2)

    def __str__(self):
        res = self.mod1 + self.relation.value + self.mod2
        return res

    def __repr__(self):
        return self.__str__()


class Task:
    def __init__(self, elements, triplets, triplet_modifiers, triplets_triplets_rel):
        """
        :rtype: Task
        :param elements: Array of ints
        :param triplets: Array of RelationTriplet
        :param triplet_modifiers: Array of UnaryRelation
        :param triplets_triplets_rel: Array of BinaryRelation (logic)
        :return: instance of Task
        """
        self.elements = elements
        self.triplets = triplets
        self.triplet_modifiers = triplet_modifiers
        self.triplets_triplets_rel = triplets_triplets_rel

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_string(cls, task_string):
        """
        :rtype : Task
        :param task_string: String in "[12,14,15,26]$[%10%3| <= |/10%3]@[/10%3| >= |%10%3]$[ not @ ]$[ and @...]" format
        :return: initialized instance of Task
        """
        task_elements = task_string.split('$')
        elements = [int(int_str) for int_str in task_elements[0][1:-1].split(',')]
        triplets = [RelationTriplet(*arg_tuple)
                    for arg_tuple in [(rel_elements[0][1:], BinaryRelation(rel_elements[1]), rel_elements[2][:-1])
                                      for rel_elements in [single_rel.split('|')
                                                           for single_rel in task_elements[1].split('@')]]]
        triplet_modifiers = [UnaryRelation(mod) for mod in task_elements[2][1:-1].split('@')]
        triplets_triplets_rel = [BinaryRelation(mod) for mod in task_elements[3][1:-1].split('@')]
        return Task(elements, triplets, triplet_modifiers, triplets_triplets_rel)

    def to_string(self):
        """
        :rtype: str
        :param self
        :return: String in "[12,14,15,26]$[%10%3| <= |/10%3]@[/10%3| >= |%10%3]$[ not @ ]$[ and @...]" format
        """
        elem_str = str(self.elements)
        str_triplets_list = '@'.join(['[' + tri.mod1 + '|' + tri.relation.value + '|' + tri.mod2 + ']'
                                      for tri in self.triplets])
        trip_mod_list = '[' + '@'.join(mod.value for mod in self.triplet_modifiers) + ']'
        trip_rel_list = '[' + '@'.join(rel.value for rel in self.triplets_triplets_rel) + ']'
        return '$'.join([elem_str, str_triplets_list, trip_mod_list, trip_rel_list])

    def solve_for_xy(self, e1, e2):
        triplets = [self.triplet_modifiers[i].apply_unary_relation([elem.check(e1, e2) for elem in self.triplets][i])
                    for i in range(0, len(self.triplets)-1)]
        def is_in_parenthesis(ind):
            res = False

    def solve(self):
        """
        :rtype: list
        :return: two-dimensional array of booleans with answers for Adjacency matrix of current Binary relation
        """
        results = []
        for e1 in self.elements:
            results_row = []
            for e2 in self.elements:
                triplets = [elem.check(e1, e2) for elem in self.triplets]
                for i in (0, len(triplets)-1):
                    triplets[i] = self.triplet_modifiers[i].apply_unary_relation(triplets[i])
                res = triplets[0]
                for i in (1, len(triplets)-1):
                    res = self.triplets_triplets_rel[i-1].apply_binary_relation(res, triplets[i])
                results_row.append(res)
            results.append(results_row)
        return results

    def print_solve(self):
        """
        :rtype: str
        :returns: String with a matrix of answers (+/-)
        """
        res = ""
        results = self.solve()
        for row in results:
            for item in row:
                if item:
                    res += '+ '
                else:
                    res += '- '
            res = res[:-1] + os.linesep
        return res