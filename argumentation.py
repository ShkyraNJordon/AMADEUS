'''
amadeus.logic - A Simple Logic
@author: Sh'kyra Jordon
------------------------------

This system assumes the same (simple) base logic (Besnard & Hunter 2014) and
    consistency with prolog syntax as logic.py (see preamble of logic.py).

This system also uses a notion of arguments, cases and "support" built on this
(simple logic) base logic:
    Argument:
        An argument is in the form:
            (support, claim)
        where:
            - claim is a literal.
            - support is a complete collection of supporting evidence (CCoSE)*
                for claim, and may consist of a combination of clauses and
                supporting rules from its KB.
    
    Case:
        A case is in the form:
            (supports, claim)
        where:
            - claim is a literal.
            - supports is a set of all CCoSEs for claim, as described above,
            
        Note: All arguments for a claim can be produced from a claim's case.
        
    (*) The notion of SUPPORTING a Literal or Rule, and what a COMPLETE
        collection of supporting EVIDENCE (CCoSE) for these items is:
    
        For a LITERAL:
            A SUPPORTED LITERAL:
                A Literal L is supported iff there exists in its KB at least
                one supporting clause or rule.
            A CCoSE FOR A SUPPORTED LITERAL:
                L is supported iff at least one complete collections of
                supporting evidence (CCoSE) for L exists and may consist of a
                combination of clauses and supporting rules from its KB.
                A CCoSE for L is a set of clauses and supporting rules that
                contains either:
                    - A clause in the KB that supports L.
                    - A supported rule R in the KB that supports L, with the
                        addition of the contents of a CCoSE for R.
            SUPPORTING CLAUSES AND RULES OF A LITERAL:
                - A clause C in a KB supports a Literal L if L is one of the
                    literals C asserts.
                - A rule R in a KB supports a literal L if L i its consequent,
                    and R itself is supported.
        
        For a RULE:
            A SUPPORTED RULE:
                A rule R is supported iff its antecedent contains only
                supported Literals.
            A CCoSE FOR A SUPPORTED RULE:
                R is supported iff at least one CCoSE for R exists and may
                consist of a combination of clauses and supporting rules from
                its KB.
                A CCoSE for R is a set of clauses and supporting rules that
                contain:
                    - Any union of exactly one CCoSE per antecedent literal of
                        R.
            SUPPORTING LITERALS OF A RULE:
                - A literal L may contribute to the support of a rule R if L is
                    in R's antecedent, and L itself is supported.
                - A combination of literals {L} support R if every literal in
                    R's antecedent is in {L}, and each such literal is itself
                    supported.
                    - Further, {L} minimally supports R if there are no
                        literals in {L} that are not in the antecedent of R.
'''

class Case():
    
    def __init__(self, literal, knowledgebase):
        self._claim = literal
        self._kb = knowledgebase
        self._asserting_clauses = frozenset(self.kb._asserting_clauses[str(self.claim)])
        self._asserting_rules = frozenset(self.kb._asserting_rules[str(self.claim)])
    
    @property  # no setter for claim
    def claim(self):
        return self._claim
    
    @property  # no setter for kb
    def kb(self):
        return self._kb
    
    @property  # no setter for asserting_clauses
    def asserting_clauses(self):  
        return self._asserting_clauses
    
    @property  # no setter for asserting_rules
    def asserting_rules(self):
        return self._asserting_rules
    
    # Initiates is_entailed for this case (which in turn value for self.supporting_rules)
    
    @property  # no setter for supporting_rules
    def supporting_rules(self):
        if not hasattr(self, "_supporting_rules"):
            self.is_entailed  # This function will calculate self._supporting_rules
        return self._supporting_rules
    
    @property
    def is_contained(self):
        if not hasattr(self, "_contained"):  # If we haven't done this check before, calculate its value     
            self._contained = False  # First assume self.claim is not contained in self.kb  
            self._asserting_clauses = frozenset(self.kb._asserting_clauses[str(self.claim)])  # Get all supporting clauses in the self.kb for self.claim
            if len(self._asserting_clauses) != 0:  # If there exists any clauses in self.kb that assert self.claim
                self._contained = True  # Then self.claim is contained in self.kb
        return self._contained
    
    # Generates self.supporting_rules
    @property
    def is_entailed(self):
        if not hasattr(self, "_entailed"):  # If we haven't done this check before, calculate its value     
            entailed = False  # Assume self.claim is not entailed by self.kb   
            # Check for supporting Rules in the KB (i.e supported Rules that assert self.claim)
            self._supporting_rules = set()
            for r in self.asserting_rules:
                if r.is_supported:
                    entailed = True  # If any such rules exist, self.claim is supported
                    self._supporting_rules.add(r)
                    # Keep checking through all asserting_rules so all _supporting_rules can be found
            self._supporting_rules = frozenset(self._supporting_rules)  # for hashability
            self._entailed = entailed
        return self._entailed
    
    def __str__(self): ###### TEMPORARY
        return "({" + " ".join([str(c) for c in self._asserting_clauses] + [str(r) for r in self._asserting_rules]) + "}, " + str(self.claim) + ")" 
    
    def __repl__(self):
        return str(self)
    
    def __hash__(self):
        return hash((self.claim, self.kb))
    
    def __eq__(self, other):
        if isinstance(other, Case):
            return (self.claim == other.claim) and (self.kb == other.kb)
        return False