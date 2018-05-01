"""
amadeus.logic - A Simple Logic
@author: Sh'kyra Jordon
------------------------------

This system assumes the following (simple logic) base logic (Besnard & Hunter
2014) and is consistent with the prolog syntax:

    Atoms:
        An atom is an atomic formula (as in mathematical logic), aka the
        assertion of an atomic logical statement.
        
        - Atoms are denoted by some alpha-numerical string that accepts 
            underscores, and contains at least one non-numerical character).
        
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
        
        - Negation may only be performed on literals.
        
    Clauses:
        Clauses are in the form, where all a_i are literals the clause asserts
        in conjunction:
            a_1, a_2, ..., a_n.    (for positive integer n)
        
        - x, y denotes logical conjunction between literals x and y.
        - . denotes the end of a clause.
        - There is no logical disjunction in this definition of simple logic.
        - Thus, all clauses are in conjunctive negation normal form, with the
            absence of logical disjunction as a binary operator. 
        
        Note that conjunctions of clauses are equivalent to a single clause,
        and can be reduced as such.
        For example, since brackets are included in the syntax for simple
        logic:
            (a_1, a_2), (b_1, b_2).
        would be written as its equivalent
            a_1, a_2, b_1, b_2.
        Note also that a clause may consist of only a single literal.
    
    Rules:
        Rules are in the form:
            b :- a_1, a_2, ..., a_n.    (for positive integer n)
        where b is a (consequent) literal and a_i are a (antecedent) literals.
        
        - :- denotes modus ponens, the only proof rule in this definition of
            simple logic.
        - . denotes the end of a rule.
        
        Thus a rule asserts that its consequent logically follows (by the modus
        ponens rule of inference) from its antecedent.
    
    Statements:
        Clauses and rules are considered whole logical statements.
        
        - . denotes the end of a logical statement.
    
    Knowledge base (KB):
        A knowledge base is a collection of logical statements.
        
        Note: A KB's "content" refers to the clauses and rules it asserts.

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
"""
# TODO: Should CCoSE's be minimal sets?
from _ast import Attribute
class Literal():
    """
    An object representing a simple logic literal that asserts either an atom,
        or its logical complement.
    
    Properties:
        atom (str):
            The string representation of this Literal's atom. This is
            case-sensitive and should be non-empty, containing only chars
            "a-zA-Z0-9_", with at least 1 non-numerical char.
            This is read-only after initialisation.
        is_positive (bool):
            The sign of this Literal; True if positive, False if negative.
            This is read-only after initialisation.
        case (Case):
            The Case instance associated with this Literal. Needs to be set
            first time. Thereafter, it is read-only.
    """
    
    def __init__(self, atom, is_positive=None):
        """
        Parameters:
            atom (str):
                The string representation of this Literal's atom. This is
                case-sensitive and should be non-empty, containing only chars
                "a-zA-Z0-9_", with at least 1 non-numerical char.
            is_positive (bool | None): 
                The sign of this Literal; True if positive, False if negative.
        Return type: None
        """
        # TODO: Implement checks to ensure atom is a nonempty str in the right format (a-zA-Z0-9_ with at least one non-numerical char).
        #     Currently this property is assumed.
        self._atom = atom
        if is_positive is None:  # If is_positive is not passed, assume is True
            is_positive = True
        # TODO: Implement check to ensure is_positive is bool, if not None.
        #     Currently this property is assumed.
        self._is_positive = is_positive
        
    @property  # no setter for atom; this value should not change.
    def atom(self):
        """
        Return type: str
        
        Read-only accessor for this Literal's atom.
        """
        return self._atom
    
    @property  # no setter for is_positive; this value should not change.
    def is_positive(self):
        """
        Return type: bool
        
        Read-only accessor for this Literal's sign; True if positive, False if
            negative.
        """
        return self._is_positive
      
    def is_negation_of(self, other):
        """
        Parameters:
            other (Literal): The Literal instance to compare this Literal to.
        Return type: bool
        
        Returns True if other is a Literal asserts the logical complement of
            this Literal. Returns False otherwise.    
        """
        if isinstance(other, Literal):
            return (self.atom == other.atom) and (self.is_positive != other.is_positive())
        return False

    @property  # Raises AttributeError if called before self.case has been set.
    def case(self):
        """
        Return type: Case
        
        Accessor for self.case.
        """
        return self._case
    # TODOD: Where this function is called, deal with AttributeError if raised.

    @case.setter  # The value of case can only be set once.
    def case(self, case):
        """
        Parameters:
            case (Case): The Case instance associated with this Literal.
        Return type: None
        
        One-time setter for attribute self.case; its value does not change
            thereafter.
        """
        if not hasattr(self, "_case"):  # If first time setting self.case
            self._case = case
        else:
            raise AttributeError("attribute value can only be set once, and already has value: {}".format(self.case))
    
    @property
    def is_supported(self):
        """
        Return type: bool
        
        Returns True if this Literal is supported by the KB, and False if not.
            This value is calculated only once on the first call.
        Relies on the association of a Case object with self.case.
        """
        if hasattr(self, "_supported"):  # If not first call to this method
            return self._supported
        self._supported = self.case.is_supported  # May return AttributeError if self.case is not set.
        return self._supported
    
    def __str__(self):
        """Returns a string of the Literal instance in prolog syntax (w/o trailing fullstop)"""
        if not self.is_positive:
            return "~" + self.atom
        return self.atom
    
    def __repr__(self):
        return str(self)
        
    # Literal must be an immutable hashable type so Clause and KnowledgeBase 
    #     (knowledgebase.py) classes0 can store Literal objects in a set.
    def __eq__(self, other):  # Needed for hashability of Literals
        """Equality is based on the equality of the atom (str) and sign (boolean)."""
        if isinstance(other, Literal):
            return (self.atom == other.atom) and (self.is_positive == other.is_positive)
        return False
    
    def __hash__(self):  # Needed for hashability of Literals
        return hash((self.atom, self.is_positive))
    
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
    
    @property
    def is_supported(self):
        if hasattr(self, "_supported"):  # If this method has been called before
            return self._supported
        supported = True
        for l in self.body:
            if not l.is_supported:
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