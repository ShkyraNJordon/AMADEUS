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
        self.support_clauses, self.support_rules = set(), set()
    
    @property  # no setter for claim
    def claim(self):
        return self._claim
    
    @property  # no setter for kb
    def kb(self):
        return self._kb
    
    @property
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
            if r.is_supported:
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