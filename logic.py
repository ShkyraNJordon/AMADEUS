"""
amadeus.logic - A Simple Logic
@author: Sh'kyra Jordon
------------------------------

This system assumes the following (simple logic) base logic (Besnard & Hunter
    2014) and is consistent with the prolog syntax:

    Atoms:
        An atom is an atomic formula (as in mathematical logic), aka the
            assertion of an atomic logical statement.
        
        * Atoms are denoted by some raining-numerical string that accepts 
            underscores (with at least one non-numerical character).
        
        Example atoms include:
            - a
            - FranceIsCold
            - James_passed_module_CM1234
            
    Literals:
        Literals are positive or negative:
            - Positive literals assert some atom, denoted "a" for atom "a"
            - Negative literals assert the logical complement (as in
                mathematical logic) of some atom, denoted "~a" for atom "a"
            and thus literals are either atoms, or their logical complements.
        
        Example literals include:
            - a
            - ~a
            - FranceIsCold
            - ~FranceIsCold
            - James_passed_module_CM1234
            - ~James_passed_module_CM1234
    
    Negation:
        The negation of a literal with atom "a" is a literal that asserts the
            logical complement of "a" (as describe above), and is denoted "~a". 
        
        * Negation may only be performed on literals.
        
    Clauses:
        Clauses are in the form, where all a_i are literals the clause asserts:
            a_1, a_2, ..., a_n.    (for positive integer n)
        
        * , represents logical conjunction.
        * . represents the end of a clause (and in fact any [logical] statement)
        * There is no logical disjunction in this base logic.
        * Thus, all Clauses are in conjunctive negation normal form, with the
            absence of logical disjunction as a binary operator. 
        
        Note that conjunctions of clauses equate to a single clause, and can be
            reduced as such. For example, since brackets are not in our syntax:
                (a_1, a_2), (b_1, b_2).
            would be written as its equivalent
                a_1, a_2, b_1, b_2.
        Note also that a clause may consist only of a single literal.
    
    Rules:
        Rules are in the form:
            b :- c.
        where c is a (antecedent) Clause and b is a (consequent) Literal.
        
        * :- is modus ponens, the only proof rule in this logic.
        
        Thus a rule asserts that its consequent logically follows (by the modus
            ponens rule of inference) from its antecedent.
    
    Statements:
        Clauses and Rules will be referred to as "statements".
        
        * The end of a logical statement is denoted with a .


This system also uses a notion of Arguments, Cases and "support" built on this
    (simple logic) base logic:
    Argument:
        An Argument is in the form:
            (support, claim)
        where support is a complete collection of supporting evidence
            (CCoSE) for the Argument's claim (where the CCoSE contains Clauses
            and supporting Rules), and claim is the Literal the Argument's
            support attempts to provide evidence for.
    
    Case:
        A Case is in the form:
            (supports, claim)
        where supports is a set of all CCoSEs for claim, as described above,
            and claim is the Literal supports' elements provide evidence for.
        All Arguments for a claim can be produced from a claim's Case. 
        
    The notion of SUPPORTING a Literal or Rule, and what a COMPLETE
        collection of supporting EVIDENCE (CCoSE) for these items is:
    
        For a LITERAL:
            A Literal L is supported if there is a Clause C or a supported
                Rule R in KB's contents that supports it. In which case,
                complete collections of supporting evidence (CCoSE) for L's
                may be:
                - A Clause C that supports L
                - A supported Rule R that supports L with the addition of a
                    CCoSE for R.
            A Clause C supports a Literal L if L is one of the literals C asserts.
            A Rule R supports its consequent Literal L if it is supported.
        
        For a RULE:
            A Rule R is supported if its antecedent contains only supported
                Literals. In which case, CCoSE for R may be:
                - Suppose R has antecedent Literals L_i (for i = 1,2,...n),
                    where each L_i is supported.
                    Then for each L_i there exists at least one CCoSE for
                        L_i.
                    Consider a (set) union where for every L_i, exactly one
                        CCoSE for L_i has been included in this union.
                    Any such union can be considered a CCoSE for R.
"""
from unittest import case
class Literal():
    """!
    An object representing a simple logic literal that asserts either an atom,
        or its logical complement.
    
    @param _atom: The atom associated with this literal.
    @type _atom: str. Case-sensitive, should be: non-empty; consisting of only alphanumerical chars and underscores and at least one non-numerical char.
    @param is_positive: True if literal asserts an atom. False if literal asserts its logical complement. If intialised as None, it's assumed to be True.
    @type is_positive: bool | None
    
    Note: Literal must be an immutable hashable type so Clause and KnowledgeBase 
        (knowledgebase.py) classes can store Literal objects in a set. 
    """
    #TODO Implement checks to ensure atom is a nonempty str in the right format
    #    (a-zA-Z0-9_ with at least one non-numerical char) and is_positive is bool or None   
    def __init__(self, atom, is_positive=None):
        if is_positive is None:  # If only one param was passed/None passed for 2nd,
            is_positive = True  # then positivity takes on default value True.
        self._atom = str(atom)  # Assumption: atom is in the right format
        self._positivity = is_positive  # Assumption: positivity is of type bool
        
    @property  # no setter for atom
    def atom(self):
        return self._atom
    
    @property  # no setter for is_positive
    def is_positive(self):
        """Checks whether this Literal asserts its atom."""
        return self._positivity
      
    def is_negation_of(self, other):
        if isinstance(other, Literal):
            return (self.atom == other.atom) and (self.is_positive != other.is_positive())
        return False

    @property  # Raises error if self.case has not been set yet
    def case(self):
        return self._case

    @case.setter  # The value of case can only be set once
    def case(self, case):
        if not hasattr(self, "_case"):  # If this is the first time setting self.case
            self._case = case
        else:
            raise AttributeError("can't set attribute")
    
    def is_supported(self):
        if hasattr(self, "_supported"):  # If this method has been called before:
            return self._supported
        self._supported = self.case.is_supported()
        return self._supported
    
    def __str__(self):
        """Returns a string of the Literal instance in prolog syntax (w/o trailing fullstop)"""
        if not self.is_positive:
            return "~" + self.atom
        return self.atom
    
    def __eq__(self, other):  # Needed for hashability
        """Equality is based on the equality of the atom (str) and sign (boolean)."""
        if isinstance(other, Literal):
            return (self.atom == other.atom) and (self.is_positive == other.is_positive)
        return False
    
    def __hash__(self):  # Needed for hashability
        return hash((self.atom, self.is_positive))

    def __repr__(self):
        return str(self)
    
class Clause():
    """An object that represents a simple logic clause that asserts a set of
        literals in conjunction.
    
    :param literals: The literals asserted in logical conjunction by this Clause.
    :type literals: A variable number of Literals.
    
    Note: Clause must be an immutable hashable type so KnowledgeBase
        (knowledgebase.py) can store Clause objects in a set.     
    """
    #TODO Implement checks to ensure literals is a nonempty iterable of Literals       
    def __init__(self, *literals):
        self._literals = frozenset(literals)
    
    @property  # no setter for literals
    def literals(self):
        return self._literals
    
    def __str__(self):
        """Returns a string of the Clause instance in prolog syntax"""
        return ", ".join([str(l) for l in sorted(list(self.literals), key=lambda x: str(x))]) + "."
    
    def __iter__(self):  # Iterating over a Clause iterates over its Literal(s)
        return iter(self._literals)
        
    def __eq__(self, other):  # Needed for hashability
        """Equality consistent with the equality of the Literals in literals (Frozenset)"""
        if isinstance(other, Clause):
            return self.literals == other.literals
        return False
    
    def __hash__(self):  # Needed for hashability
        return hash(self.literals)

    def __repr__(self):
        return str(self)    

class Rule():
    """!
    An object that represents a sinple logic rule that asserts that its head
        (Literal) logically follows (modus ponens) from its body (Clause).
        
    :param head: The head (consequent) of the simple logic Rule.
    :type head: Literal
    :param body: The body (antecedent) of the simple logic Rule.
    :type body: A variable number of Literals
    
    Note: Rule must be an immutable hashable type so KnowledgeBase
        (knowledgebase.py) can store Rule objects in a set.
    """
    
    #TODO Implement checks to ensure head is a Literal and body is a nonempty
    #     iterable of Literals.
    def __init__(self, head, *body):
        self._head = head  # should be a Literal
        self._body = frozenset(body)  # should be a nonempty iterable of Literals
    
    @property  # no setter for head
    def head(self):
        return self._head

    @property  # no setter for body
    def body(self):
        return self._body
    
    def is_supported(self):
        if hasattr(self, "_supported"):  # If this method has been called before
            return self._supported
        supported = True
        for l in self.body:
            if not l.is_supported():
                supported = False
        self._supported = supported
        return self._supported
    
    def __str__(self):
        """Returns a strong of the Rule instance in prolog syntax"""
        return str(self.head) + ":- " + ", ".join([str(l) for l in self.body]) + "."
    
    def __eq__(self, other):  # Needed for hashability
        """Equality is based on the equality of the head (Literal) and body (Clause)"""
        if isinstance(other, Rule):
            return (self.head == other.head) and (self.body == other.body)
        return False
       
    def __hash__(self):  # Needed for hashability
        return hash((self.head, self.body))
        
    def __repr__(self):
        return str(self)        
        
if __name__ == "__main__":
    
    # Demonstrating the use of Literals
    print("Let's directly create literals: ~raining. happy. goodday.")
    notraining, happy, goodday = Literal("raining", False), Literal("happy"), Literal("goodday")
    print("\tprinting them as Literals:", notraining, happy, goodday)
    
    print("Note that these do not print with trailing '.' because they are not considered whole logcial statements unless enclosed in a Clause.")
    print("\tprinting them as Clauses:", Clause(notraining), Clause(happy), Clause(goodday))
    
    print("We can test the equality of Literals...")
    print("\tnotraining == Literal('raining', False):", notraining == Literal("raining", False))
    
    print("\n")
    
    # Demonstrating the use of Clauses
    print("From this, let's make two clauses: ~raining, happy. happy, goodday.")
    c1, c2 = Clause(notraining, happy), Clause(happy, goodday)
    print("\tprinting these Clauses as c1:", c1, "and c2:", c2)
    
    print("We can test the equality of Clauses")
    print("\tc1 == c2:", c1 == c2)
    print("\tc1 == Clause(notraining, happy):", c1 == Clause(notraining, happy))

    print("\n")

    # Demonstrating the use of Rules
    print("And we can create rules of inference from Literals: happy:- ~raining. goodday:- happy.")
    rain_is_sad, happy_is_good = Rule(happy, notraining), Rule(goodday, happy)
    print("\tprinting them as Rules:", rain_is_sad, happy_is_good)