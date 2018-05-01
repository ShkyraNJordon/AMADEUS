'''
Created on 12 Mar 2018

@author: Coder
'''
from logic import Clause, Literal, Rule
from distutils.tests import support

class KnowledgeBase():
    """!
    A knowledge base (KB) which is capable of:
        - Reading in simple logic* KB contents from a text file in prolog
            syntax, and store them in the appropriate format (i.e. as the
            Clause and Rule instances [defined in logic.py] they represent).
        - Forming arguments inferred from these contents.
     
    (*) This system assumes the same (simple) base logic (Besnard & Hunter
        2014) and consistency with prolog syntax as logic.py (see preamble of
        logic.py). This system also uses the notion of Arguments and "support"
        used by logic.py (see again the preamble of logic.py).
        
    Note that this knowledge base forbids the inclusion of cycles.
    
    @param contents: The Clause and Rule objects intended to populate this KnowledgeBase, or a string representing a simple logic prolog-syntax knowledge base, or the filename to a text-file containing the same.
    @type contents: A variable number of Clauses and Rules | A tuple with exactly one entry that is a valid parameter for PrologString.__init__
    """
  
    #TODO Add cycle checking to __init__, and forbid cycles.
    def __init__(self, *contents):
        self._clauses = set()  # to store Clause instances
        self._rules = set()  # to store Rule instances
        # thus Clause and Rule objects should be immutable hashable types.

        if len(contents) == 1 and isinstance(contents[0], str):  # If contents is of type str, assume it is a simple logic prolog-syntax string, or the filename to a text-file containing the same.
            ps = PrologString(contents[0])
            
            contents = ps.contents  # Get a set of Clauses and Rules from ps
            for content in contents:
                if isinstance(content, Clause):
                    self._clauses.add(content)
                elif isinstance(content, Rule):
                    self._rules.add(content)
                else:
                    raise TypeError("Cannot add content of type {} to a KnowledgeBase".format(type(content).__name__))
            self._literals = ps.literals  # And get the unique dictionary of all Literals from ps, indexed by their str representation
            
        else:  # Otherwise, assume contents are all Clause and Rule instances
            # Add Clauses and Rules, consolidating (recreating) them so they reference the same Literal instances.
            self._literals = dict()  # To be a dictionary of unique Literals, indexed by their str representation
            for content in contents:
                if isinstance(content, Clause):  # If content is a Clause
                    # Consolidation:
                    literals = self._consolidate_literals(content.literals)  # Create a set of consolidated Literals from the Literals in content.literals
                    self._clauses.add(Clause(*literals))  # And add a Clause with this set as its contents
                elif isinstance(content, Rule):  # If content is a Rule
                    # Consolidation:
                    head = self._consolidate_literal(content.head)  # Consolidate the Literal in content.head
                    # onsolidate the Literals in content.body
                    body = self._consolidate_literals(content.body)
                    self._rules.add(head, body)
                else:
                    raise TypeError("Cannot add content of type {} to a KnowledgeBase".format(type(content).__name__))
        self._clauses, self._rules = frozenset(self._clauses), frozenset(self._rules)  # helps with hashability of KBs
               
        # For each Literal in self._literals.values(), get the set of Clauses that assert it
        # Then put these sets in a dictionary, indexed by the str representation of the Literal they assert.
        self._asserting_clauses = self._get_asserting_clauses(self._literals.values())

        # And do the same for Rules;
        # For each Literal in self._literals.values(), get the set of Rules that assert it as its head
        # Then put these sets in a dictionary, indexed by the str representation of the Literal they assert.
        self._asserting_rules = self._get_asserting_rules(self._literals.values())
        
        # For each Literal l in self._literals.values(), create a Case instance associated with both it and this KB, and assign it to l.case.
        self._supporting_cases = self._generate_supporting_cases(self._literals.values())
                    
    @property  # no setter for clauses
    def clauses(self):
        return self._clauses
    
    @property  # no setter for rules
    def rules(self):
        return self._rules
    
    def _consolidate_literal(self, l):
        """
        Function that returns the original version of Literal l in self._literals, or adds it if there is no original, and returns l.
        """
        if not str(l) in self._literals:  # If l is a new Literal
            self._literals[str(l)] = l  # Add it to self._literals
        else:  # Otherwise, if l has been encountered before
            l = self._literals[str(l)]  # Reference the original instead
        return l
    
    def _consolidate_literals(self, literals):
        """
        Function that runs self._consolidate_literal on an iterable of Literals
        """
        return set([self._consolidate_literal(l) for l in literals])
        
    def _get_asserting_clauses(self, literals):
        """
        # For each Literal in literals, get the set of Clauses that assert it
        # Then put these sets in a dictionary, indexed by the str representation of the Literal they assert.
        """
        return {str(l) : set([clause for clause in self.clauses if l in clause.literals]) for l in literals}
    
    def _get_asserting_rules(self, literals):
        """
        For each Literal in literals, get the set of Rules that assert it as its head
        # Then put these sets in a dictionary, indexed by the str representation of the Literal they assert.
        """
        return {str(l) : set([rule for rule in self.rules if l == rule.head]) for l in literals}
    
    def _generate_supporting_cases(self, literals):
        """
        For each Literal l in literals, create a Case instance associated with both it and this KB, and assign it to l.case.
        """
        cases = set()
        for l in literals:
            l.case = Case(l, self)
            cases.add(l.case)
        return cases
    
    def populate(self):
        for l in self._literals.values():
            l.is_supported()  # prompts a l.case.is_supported() call to populate

    def __str__(self):
        """Returns a string representation of the KnowledgeBase contents in prolog syntax"""
        return "".join(["{}\n".format(str(s)) for s in self.clauses.union(self.rules)])
    
    def __hash__(self):
        return hash((self.clauses, self.rules))
    
    def __eq__(self, other):
        if isinstance(other, KnowledgeBase):
            return (self.clauses == other.clauses) and (self.rules == other.rules)
        return False
    
class PrologString():
    """!
    A string representation of (simple logic) prolog-syntax Clauses and Rule
        that can be converted to a set of corresponding Clause and Rule objects.
    
    @param s: A (simple logic) prolog-syntax string of Clauses and Rules, or the
        filename of a text-file containing the same.
    @type s: str
    """
    
    def __init__(self, s):
        if isinstance(s, str):
            try:
                with open(s) as infile:
                    s = infile.read()
            except (FileNotFoundError, OSError) as err:
                pass  # If not a file, assume s is intended to be a prolog-syntax string.
                # TODO: A check to see if s is in prolog syntax can be implemented; If it is not in prolog syntax, raise. Otherwise, pass.
            
            self._literals = dict()  # to hold the Literal instances shared between Clauses and Rules
            self._contents = self._parse(s)
        else:
            raise TypeError("PrologString takes a str input of a (simple logic) prolog-syntax knowledge base, or the filemame of a textfile containing the same. Invalid input: {}".format(repr(s)))

    @property  # no setter for contents
    def contents(self):
        return self._contents
    
    @property  # no setter for literals
    def literals(self):
        return self._literals

    def _parse(self, s):
        """Turns a string s in Prolog syntax into a set of clauses and Rules."""
        
        contents = set()
        # TODO: Add syntax checks to ensure Clauses and Rules are in correct prolog-syntax before passing to the parsers.
        for p in s.split("."):  # Splitting s into statements
            p = p.strip()
            if p == "":  # Ignore empty strings (e.g trailing whitespace after last '.').
                continue
            elif ":-" in p:  # If ":-" in p, assume p is a Rule
                contents.add(self._parse_rule(p))
            else:  # Otherwise assume p is a Clause
                contents.add(self._parse_clause(p))
        return contents
                
    def _parse_rule(self, s):
        """Takes a string s, splits it around ':-', and assumes only 2 substrings will result from this, s1 and s2.
            Strips whitespace from s1 and assumes it is a (simple logic) prolog-syntax Literal.
            Converts s1 to its corresponding Literal with _parse_literal(s), and sets head equal to this Literal.
            Strips whitespace from s2 and assumes it is a string of comma separated (simple logic) prolog-syntax Literals.
            Converts s2 to a set of the corresponding Literals with _parse_literals(s), and sets body equal to this set.
        """
        head, body = s.split(":-")    
        head = self._parse_literal(head.strip())
        body = self._parse_literals(body.strip())
        return Rule(head, *body)
        
    def _parse_literal(self, s):
        """
        s is assumed to be a string of a (simple logic) prolog-syntax Literal.
        Takes a string s, strips whitespace from s, and checks for '~' in s[0]:
            If s[0] != '~', s is taken as a positive literal, and Literal(s) is returned.
            Otherwise, s is taken as a negative literal, and Literal(s, False) is returned.
        """
        s = s.strip()  # shouldn't need this since all functions that call this method strip s before call, but redundancy just in case.
        if not s in self._literals:  # If we have not encountered this literal before
            if s[0] == "~":  # If this is a negative Literal
                literal = Literal(s[1:], False)
            else:  # Otherwise this is a positive Literal
                literal = Literal(s)
            self._literals[s] = literal  # Add this Literal to all the set of all Literals
        return self._literals[s]  # And return it
    
    def _parse_literals(self, s):
        """
        s is assumed to be a string of comma separated (simple logic) prolog-syntax Literals.
        This function:
            Takes s, splits it around ','s, and strips the whitespace from these substrings.
            The substrings are assumed to be literals and are converted as such with _parse_literal(s).
            The resulting Literals are returned in a set.
        """
        literals = set()
        for l in s.split(","):  # Split s into literals
            l = l.strip()
            if l != "":  # Ignore e.g the railing whitespace after the last ','
                literals.add(self._parse_literal(l))
        return literals
    
    def _parse_clause(self, s):
        """
        s is assumed to be a (simple logic) prolog-syntax Clause.
        This function:
            Takes s, obtains a set of its Literals with with _parse_literals(s).
            These Literals are used to instantiate a Clause, which is then returned.
        """
        literals = self._parse_literals(s)
        return Clause(*literals)
    
    def __str__(self):
        return super().__str__()    

class Case():
    
    def __init__(self, literal, knowledgebase):
        self._claim = literal
        self._kb = knowledgebase
        self.support_clauses, self.support_rules = set(), set()
    
    @property  # no setter for claim
    def claim(self):
        return self._claim
    
    @property  # no setter for kb
    def kb(self):
        return self._kb
    
    def is_supported(self):
        if hasattr(self, "_supported"):
            return self._supported
        supported = False  # Assume self.claim is not supported
        
        # Check for supporting clauses in the KB
        self.support_clauses = self.kb._asserting_clauses[str(self.claim)]  # Discarding previous value of self.support_clauses
        if len(self.support_clauses) != 0:  # if there is at least one supporting clause for self.claim
            supported = True
        
        # Check for supporting Rules in the KB (i.e supported Rules that assert self.claim)
        self.support_rules = set()  # Discarding previous value of self.support_rules
        for r in self.kb._asserting_rules[str(self.claim)]:
            if r.is_supported():
                supported = True
                self.support_rules.add(r)
        
        self.support_clauses, self.support_rules = frozenset(self.support_clauses), frozenset(self.support_rules)  # for hashability
        
        self._supported = supported
        return self._supported
    
    def __str__(self): ###### TEMPORARY
        return "({" + " ".join([str(c) for c in self.support_clauses] + [str(r) for r in self.support_rules]) + "}, " + str(self.claim) + ")" 
    
    def __repl__(self):
        return str(self)
    
    def __hash__(self):
        return hash((self.claim, self.kb))
    
    def __eq__(self, other):
        if isinstance(other, Case):
            return (self.claim == other.claim) and (self.kb == other.kb)
        return False
        
if __name__ == "__main__":
    
    kb = """
beta. alpha, beta.
beta:- alpha. gamma:- beta."""
    KB = KnowledgeBase(kb)
    print("KB:", str(KB).replace("\n", " "))
    print("KB's Literals:", *KB._literals.values())
    print("KB's dict of asserting clauses:", KB._asserting_clauses)
    print("KB's dict of asserting rules:", KB._asserting_rules)
    cases = KB._supporting_cases
#     for case in cases:
#         claim = case.claim
#         print(claim, claim.case)
    print("\nTIME TO POPUALTE")
    KB.populate()
    for case in cases:
        claim = case.claim
        print("Case for {}:".format(claim), claim.case)
