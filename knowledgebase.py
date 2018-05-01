'''
amadeus.logic - A Simple Logic
@author: Sh'kyra Jordon
------------------------------
'''
from logic import Clause, Literal, Rule
from argumentation import Case

class KnowledgeBase():
    """
    A knowledge base (KB) which is capable of:
        - Reading in simple logic* KB contents from a text file in prolog
            syntax, and store them in the appropriate format (i.e. as the
            Clause and Rule instances [defined in logic.py] they represent).
        - Forming arguments** inferred from these contents.
     
    (*) This system assumes the same (simple) base logic (Besnard & Hunter
        2014) and consistency with prolog syntax as logic.py (see preamble of
        logic.py).
    (**)This system also uses the notion of Cases, Arguments and "support"
        used by argumentation.py (see preamble of argumentation.py).
        
    Note that this knowledge base forbids the inclusion of cycles.
    
    Properties:
        clauses (set of Clauses):
             A set of all Clauses in the KB
        rules (set of Rules):
            A set of all Rules in the KB
    """
  
    def __init__(self, *contents):
        """
        Parameters:
            contents (iterable of Clauses and Rules | str):
                The contents intended for this KB.
                This may be:
                    - a variable number of Clause and Rule objects
                    - a str representing either a simple logic prolog-syntax KB,
                        or the filename of text-file containing the same. 
        Return type: None
        """
        # GETTING KB CLAUSES, RULES AND LITERALS:
        
        # If contents has only one element, if it is of type str, assume it is
        #     a simple logic prolog-syntax string, or the filename to a
        #     text-file containing the same.
        if len(contents) == 1 and isinstance(contents[0], str):
            # Use PrologString to convert contents[0] into a set of Clauses and
            #     a set of Rules, where contents[0] can be either a simple
            #     logic prolog-syntax string, or a filename to a text-file
            #     containing the same.
            ps = PrologString(contents[0]) 
            
            # Get the dict mapping the str reprsentation of Literal instances to
            #     their unique instances. Note that these are the exact Literal 
            #     instances ps's Clauses and Rules reference. 
            self._literals_dict = ps.literals 
            self._clauses = ps.clauses  # Set of all Clauses
            self._rules = ps.rules      # Set of all Rules
        
        # Otherwise, assume contents are all Clause and Rule instances that
        #    possibly do not all reference the exact same set of Literal
        #    instances, in which case, these need consolidation (recreating so
        #    they all use the same Literal instances).
        else:      
            # The dict mapping the str reprsentation of Literal instances to
            #     their unique instances. Note that these will be the exact
            #     Literal instances our Clauses and Rules will reference.
            self._literals_dict = dict()   
            self._clauses = set()  # to store Clause instances
            self._rules = set()    # to store Rule instances

            for content in contents:
                if isinstance(content, Clause):
                    # Consolidation of the Literals in content.literals
                    literals = self._consolidate_literals(content.literals)
                    # Creating a new Clause from these literals and storing.
                    self._clauses.add(Clause(*literals))
                elif isinstance(content, Rule):
                    # Consolidation of the Literal in content.head
                    head = self._consolidate_literal(content.head)
                    # Consolidation of the Literals in content.body
                    body = self._consolidate_literals(content.body)
                    # Creating a new Rule from this head and body, then storing.
                    self._rules.add(head, body)
                else:
                    raise TypeError("Cannot add content of type {} to a KnowledgeBase".format(type(content).__name__))
        
        self._clauses, self._rules = frozenset(self._clauses), frozenset(self._rules)  # helps with hashability of KB
        # TODO: Add cycle checking and forbid KB contents (abort) if cyclic.
        
        
        # GETTING MAPPINGS FROM STR REPRESENTATIONS OF LITERALS TO:
        #     - THE CLAUSES THAT ASSERT THEM
        #     - THE RULES THAT ASSERT THEM
        
        # For each Literal L in self._literals_dict.values(), get the set of Clauses
        #     that assert it in a dict, indexed by str(L).
        self._asserting_clauses = self._get_asserting_clauses()

        # And do the same for Rules;
        # For each Literal L in self._literals_dict.values(), get the set of Rules
        # that assert it (as its head) in a dict, indexed by str(L).
        self._asserting_rules = self._get_asserting_rules()
        
        # For each Literal L in self._literals_dict.values(), create a Case instance
        # C such that L.case = C and C.claim = L.
        self._supporting_cases = self._generate_supporting_cases()
        
        # CREATING ARGUMENTS FOR EACH LITERAL INSTANCE:
        self._supported_literals = {k : v for k,v in self._literals_dict.items() if v.is_supported}
    
    @property  # no setter for clauses
    def clauses(self):
        return self._clauses
    
    @property  # no setter for rules
    def rules(self):
        return self._rules
    

    
    def _consolidate_literal(self, l):
        """
        Function that returns the original version of Literal l in self._literals_dict, or adds it if there is no original, and returns l.
        """
        if not str(l) in self._literals_dict:  # If l is a new Literal
            self._literals_dict[str(l)] = l  # Add it to self._literals_dict
        else:  # Otherwise, if l has been encountered before
            l = self._literals_dict[str(l)]  # Reference the original instead
        return l
    
    def _consolidate_literals(self, literals):
        """
        Function that runs self._consolidate_literal on an iterable of Literals
        """
        return set([self._consolidate_literal(l) for l in literals])
        
    def _get_asserting_clauses(self):
        """
        # For each Literal in literals, get the set of Clauses that assert it
        # Then put these sets in a dictionary, indexed by the str representation of the Literal they assert.
        """
        literals = self._literals_dict.values()  # Set of all Literal instances
        return {str(l) : set([clause for clause in self.clauses if l in clause.literals]) for l in literals}
    
    def _get_asserting_rules(self):
        """
        For each Literal in literals, get the set of Rules that assert it as its head
        # Then put these sets in a dictionary, indexed by the str representation of the Literal they assert.
        """
        literals = self._literals_dict.values()  # Set of all Literal instances
        return {str(l) : set([rule for rule in self.rules if l == rule.head]) for l in literals}
    
    def _generate_supporting_cases(self):
        """
        For each Literal l in literals, create a Case instance associated with both it and this KB, and assign it to l.case.
        """
        literals = self._literals_dict.values()  # Set of all Literal instances
        cases = set()
        for l in literals:
            # Assign a Case instance to each literal (calling l's one-time
            #     setter for l.case)
            l.case = Case(l, self)
            cases.add(l.case)  # Then add this Case instance to cases.
        return cases
    
#     def get_arguments(self):
#         if hasattr(self, _arguments):
#             return self._arguments#
#         # WRITE CODE TO ADD ARGUMENTS
#         # FIX COMMENTS
#         # MAKE LESS UGLY

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
    """
    A string representation of (simple logic) prolog-syntax Clauses and Rules
        that can be converted to a set of corresponding Clause and Rule objects.
    
    Properties:
    
        
    
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
            
            self._literals_dict = dict()  # to hold the Literal instances shared between Clauses and Rules
            self._clauses, self._rules = self._parse(s)
        else:
            raise TypeError("PrologString takes a str input of a (simple logic) prolog-syntax knowledge base, or the filemame of a textfile containing the same. Invalid input: {}".format(repr(s)))
  
    @property  # no setter for clauses
    def clauses(self):
        return self._clauses

    @property  # no setter for rules
    def rules(self):
        return self._rules
    
    @property  # no setter for literals
    def literals(self):
        return self._literals_dict

    def _parse(self, s):
        """Turns a string s in Prolog syntax into a set of Clauses and a set of Rules."""
        
        clauses = set()
        rules = set()
        # TODO: Add syntax checks to ensure Clauses and Rules are in correct prolog-syntax before passing to the parsers.
        for p in s.split("."):  # Splitting s into statements
            p = p.strip()
            if p == "":  # Ignore empty strings (e.g trailing whitespace after last '.').
                continue
            elif ":-" in p:  # If ":-" in p, assume p is a Rule
                rules.add(self._parse_rule(p))
            else:  # Otherwise assume p is a Clause
                clauses.add(self._parse_clause(p))
        return clauses, rules
                
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
        if not s in self._literals_dict:  # If we have not encountered this literal before
            if s[0] == "~":  # If this is a negative Literal
                literal = Literal(s[1:], False)
            else:  # Otherwise this is a positive Literal
                literal = Literal(s)
            self._literals_dict[s] = literal  # Add this Literal to all the set of all Literals
        return self._literals_dict[s]  # And return it
    
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

        
if __name__ == "__main__":
    
    kb = """
beta. alpha, beta.
beta:- alpha. gamma:- beta."""
    KB = KnowledgeBase(kb)
    print("KB:", str(KB).replace("\n", " "))
    print("KB's Literals:", *KB._literals_dict.values())
    print("KB's dict of asserting clauses:", KB._asserting_clauses)
    print("KB's dict of asserting rules:", KB._asserting_rules)
    cases = KB._supporting_cases
#     for case in cases:
#         claim = case.claim
#         print(claim, claim.case)
