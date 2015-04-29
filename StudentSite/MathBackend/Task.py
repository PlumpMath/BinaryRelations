from .RelationTriplet import RelationTriplet
from .UnaryRelation import UnaryRelation
from .BinaryRelation import BinaryRelation
import os


class Task:
    def __init__(self, elements, triplets, triplet_modifiers, triplets_triplets_rel, parenthesis):
        """
        :rtype: Task
        :param elements: Array of ints
        :param triplets: Array of RelationTriplet
        :param triplet_modifiers: Array of UnaryRelation
        :param triplets_triplets_rel: Array of BinaryRelation (logic)
        :type elements: list [int]
        :type triplets: list [RelationTriplet]
        :type triplet_modifiers: list [UnaryRelation]
        :type triplets_triplets_rel: list [BinaryRelation]
        :type parenthesis: list [(int,int)]
        :return: instance of Task
        """

        self.elements = elements
        self.triplets = triplets
        self.triplet_modifiers = triplet_modifiers
        self.triplets_triplets_rel = triplets_triplets_rel
        self.parenthesis = parenthesis
        self.results = None
        """type : list [list [bool]] | None"""

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_string(cls, task_string):
        """
        :rtype : Task
        :param task_string: String in
                            "[12,14,15,26]$[%10%3| <= |/10%3]@[/10%3| >= |%10%3]$[ not @ ]$[ and ]$[(0, 1)]" format
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
        parenthesis = eval(task_elements[4])
        return Task(elements, triplets, triplet_modifiers, triplets_triplets_rel, parenthesis)

    def to_string(self):
        """
        :rtype: str
        :param self
        :return: String in "[12,14,15,26]$[%10%3| <= |/10%3]@[/10%3| >= |%10%3]$[ not @ ]$[ and ]$[(0, 1)]" format
        """
        elem_str = str(self.elements)
        str_triplets_list = '@'.join(['[' + tri.mod1 + '|' + tri.relation.value + '|' + tri.mod2 + ']'
                                      for tri in self.triplets])
        trip_mod_list = '[' + '@'.join(mod.value for mod in self.triplet_modifiers) + ']'
        trip_rel_list = '[' + '@'.join(rel.value for rel in self.triplets_triplets_rel) + ']'
        parenthesis = str(self.parenthesis)
        return '$'.join([elem_str, str_triplets_list, trip_mod_list, trip_rel_list, parenthesis])

    def solve_for_xy(self, e1, e2):
        """
        Returns True, if e1 and e2 are in a binary relation. (Nested parenthesis are not supported).
        :rtype: bool
        :param e1: First element of relation (ab)
        :param e2: Second element of relation (cd)
        :return: abRcd (True/ False)
        """
        triplets = [self.triplet_modifiers[i].apply_unary_relation([elem.check(e1, e2) for elem in self.triplets][i])
                    for i in range(0, len(self.triplets))]

        def is_in_parenthesis(ind):
            for parenthesis_pair in self.parenthesis:
                if parenthesis_pair[0] <= ind < parenthesis_pair[1]:
                    return True
                return False

        for par_pair in self.parenthesis:
            res = triplets[par_pair[0]]
            for i in range(par_pair[0], par_pair[1]):
                res = self.triplets_triplets_rel[i].apply_binary_relation(res, triplets[i+1])
            triplets[par_pair[0]] = res

        res = triplets[0]
        for i in range(0, len(self.triplets_triplets_rel)):
            if not is_in_parenthesis(i):
                res = self.triplets_triplets_rel[i].apply_binary_relation(res, triplets[i+1])

        return res

    def solve(self):
        """
        :rtype: list
        :return: two-dimensional array of booleans with answers for Adjacency matrix of current Binary relation
        """
        results = []
        for e1 in self.elements:
            results_row = []
            for e2 in self.elements:
                results_row.append(self.solve_for_xy(e1, e2))
            results.append(results_row)
        self.results = results
        return results

    def print_solve(self):
        """
        :rtype: str
        :returns: String with a matrix of answers (+/-)
        """
        res = ""
        if type(self.results) == list:
            # noinspection PyTypeChecker
            for row in self.results:
                for item in row:
                    if item:
                        res += '+ '
                    else:
                        res += '- '
                res = res[:-1] + os.linesep
            return res