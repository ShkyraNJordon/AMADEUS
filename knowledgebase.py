'''
Created on 12 Mar 2018

@author: Coder
'''
from logic import Clause, Literal, Rule

class KnowledgeBase():
    """A knowledge base of Literals and Rules as sets."""
    
    # TODO Make KnowledgeBase initialisable from PrologString input
    
    def __init__(self):
        self._literals = set()  # Or should I treat all Literals in the KB as one Clause?
        self._rules = set()
    
    def _add_clause(self, clause):
        for literal in clause:
            self._add_literal(literal)
    
    def _add_literal(self, literal):
        self._literals.add(literal)
    
    def _add_rule(self, rule):
        self._rules.add(rule)
    
    def add_entry(self, entry):
        if isinstance(entry, Clause):
            self._add_clause(entry)
        elif isinstance(entry, Literal):
            self._add_literal(entry)
        elif isinstance(entry, Rule):
            self._add_rule(entry)
        else:
            raise TypeError("entry is not of type Clause, Literal, or Rule. Cannot add {} to a KnowledgeBase".format(repr(entry)))
        
    # TODO Make add_entries, and __iadd__
        
    def __str__(self):
        """Prints the KnowledgeBase instance contents as a "program" in prolog syntax"""
        return "".join(["{}.\n".format(s) for s in self._literals.union(self._rules)])
    
    
class PrologString(KnowledgeBase):
    """A representation of simple logic Clauses and Rules in prolog syntax."""
    
    def __init__(self, s):
        if isinstance(s, str):
            try:
                with open(s) as infile:
                    s = infile.read()
            except (FileNotFoundError, OSError) as err:
                pass  # Assume s is a string in prolog syntax, or am invalid data type.
                # TODO: check to see if s is in prolog syntax can be made. If it is not in prolog syntax, raise. Otherwise, pass.
            self._literals, self._rules = self.parse(s)
        else:
            raise TypeError("PrologString takes a str input of a prolog-syntax 'program'/knowledge base (or the filename of a file containing the same). Invalid input: {}".format(repr(s)))
    
    def parse(self, s):
        """Turns a string s in Prolog syntax into a set of Literals and Rules."""
        
        literals = set()
        rules = set()
        # TODO: Add syntax checks before assuming p is a Literal/Clause/Rule. 
        for p in s.split("."):  # Splitting s into propositions
            p = p.strip()
            if p == "":  # Ignore empty strings (e.g trailing whitespace after last '.').
                continue
            elif ":-" in p:  # If p is a Rule
                rules.add(self._parse_rule(p))
            elif "," in p:  # If p is a Clause
                p = self._parse_clause(p)  # p is now a Clause instance
                literals = literals.union(p.literals)
            else:  # Otherwise p is a Literal
                literals.add(self._parse_literal(p))
                
        return literals, rules
                
    def _parse_rule(self, s):
        """Takes a string s, splits it around ':-', and assumes only 2 substrings will result from this.
        """
        head, body = s.split(":-")
        if head == "":
            raise ValueError("Could not find any Literal proceeding ':-' in {}".format(s))
        if body == "":
            raise ValueError("Could not find any Clause proceeding ':-' in {}".format(s))
        
        head = self._parse_literal(head.strip())
        body = self._parse_clause(body)
        return Rule(head, body)
        
    def _parse_literal(self, s):
        """Takes a string s, strips whitespace from s, and check for '~' in s[0]:
                If s[0] != '~', s is taken as a positive literal, and Literal(s) is returned.
                Otherwise, s is taken as a negative literal, and Literal(s, positivity=False) is returned.
        """
        s = s.strip()
        if s[0] == "~":
            return Literal(s[1:], False)
        return Literal(s)
    
    def _parse_clause(self, s):
        """Takes a string s, splits it around ','s, and strips the whitespace from these substrings.
        The substrings are assumed to be literals and are converted as such with _parse_literal(s).
        The resulting Literals are used to instantiate a Clause, which is then returned.
        """
        literals = set()
        for l in s.split(","):  # Split s into literals
            l = l.strip()
            if l != "":  # Ignore e.g the railing whitespace after the last ','
                literals.add(self._parse_literal(l))
        return Clause(*literals)
    
    def __str__(self):
        return super().__str__()
    
    # TODO: Make add_entry (and other _add_... functions) for PrologString that take string inputs.
    
    
if __name__ == "__main__":
    


#         with open("throwaway.txt", "w") as outfile:
#             outfile.write(ps)
#         print(PrologString("throwaway.txt"))
    
#     kb = KnowledgeBase()
#     # Checking Literals add
#     kb.add_entry(Literal("alpha"))
#     print(kb)
#     # Checking Clauses add
#     kb.add_entry(Clause(Literal("beta"), Literal("gamma")))
#     print(kb)
#     # Checking Rules add
#     kb.add_entry(Rule(Literal("ganma", False), Clause(Literal("alpha"))))
#     print(kb)
#     # Checking duplicates don't repeat
#     kb.add_entry(Literal("alpha"))
#     kb.add_entry(Clause(Literal("beta"), Literal("gamma"), Literal("theta")))
#     kb.add_entry(Rule(Literal("ganma", False), Clause(Literal("alpha"))))
#     print(kb)

