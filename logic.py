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

This system also uses the notion of Cases, Arguments and "support" used by
    argumentation.py (see preamble of argumentation.py).
"""
# TODO: Should CCoSE's be minimal sets?

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
        is_supported (bool):
            True if this Literal is supported by its KB, False if not.
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
        """Read-only accessor for this Literal's atom."""
        return self._atom
    
    @property  # no setter for is_positive; this value should not change.
    def is_positive(self):
        """
        Read-only accessor for this Literal's sign; True if positive, False if
            negative.
        """
        return self._is_positive

    @property  # Raises AttributeError if called before self.case has been set.
    def case(self):
        """Accessor for self.case."""
        return self._case
    # TODOD: Where this function is called, deal with AttributeError if raised.

    @case.setter  # The value of case can only be set once.
    def case(self, case):
        """
        One-time setter for self.case (to a Case obj); its value does not
            change thereafter.
        """
        if hasattr(self, "_case"):  # If not first time setting self.case
            raise AttributeError("attribute value can only be set once, and already has value: {}".format(self.case))
        # TODO: Create check to ensure case is Case object.
        #     Currently this property is assumed
        self._case = case
    
    @property  # no setter for is_supported
    def is_supported(self):
        """
        True if this Literal is supported by the KB, and False if not.
        This value is calculated only once on the first call, and relies on the
            association of a Case object with self.case.
        """
        if not hasattr(self, "_supported"):  # If first call to this method
            # This Literal is supported iff self.case is supported
            self._supported = self.case.is_supported  # May return AttributeError if self.case is not set.
        return self._supported
    
    def is_negation_of(self, other):
        """
        Returns True if other is a Literal that asserts the logical complement
            of this Literal. Returns False otherwise.    
        """
        if isinstance(other, Literal):
            return (self.atom == other.atom) and (self.is_positive != other.is_positive())
        return False
        
    def __str__(self):
        """
        Returns a string representation of this Literal in prolog syntax (w/o a 
            trailing fullstop)
        """
        if not self.is_positive:
            return "~" + self.atom
        return self.atom
    
    def __repr__(self):
        return str(self)
        
    def __eq__(self, other):  # Needed for hashability of Literals
        """
        Equality is based on the equality of the atom (str) and is_positive
            (bool).
        """
        if isinstance(other, Literal):
            return (self.atom == other.atom) and (self.is_positive == other.is_positive)
        return False
    
    def __hash__(self):  # Needed for hashability of Literals
        """Hash is based on self.atom and self.is_positive"""
        return hash((self.atom, self.is_positive))
    
class Clause():
    """
    An object that represents a simple logic clause that asserts a set of
        literals in conjunction.
    
    Properties:
        literals (set):
            A set of the Literal instances this Clause asserts.
    
    :param literals: The literals asserted in logical conjunction by this Clause.
    :type literals: A variable number of Literals.     
    """
    #TODO Implement checks to ensure literals is a nonempty iterable of Literals       
    def __init__(self, *literals):
        """
        Parameters:
            literals (Variable number of Literals):
                The Literal instances this Clause asserts.
        Return type: None
        """
        self._literals = frozenset(literals)
    
    @property  # no setter for literals
    def literals(self):
        """Read-only accessor for self.literals"""
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
        """Hash is based on self.literals"""
        return hash(self.literals)

    def __repr__(self):
        return str(self)    

class Rule():
    """
    An object that represents a simple logic rule that asserts that its head
        or "consequent" (Literal) logically follows (modus ponens) from the
        conjunction of the literals in its body or "antecedent" (set of
        Literals).
    
    Properties:
        head (Literal):
            The Literal that represents this Rule's consequent.
        body (set of Literals):
            The Literals which in conjunction represent this Rule's antecedent.
        is_supported (bool):
            True if this Rule is (equivalently, the Literals in its body are)
            supported by its KB, False if not.
    """
    
    def __init__(self, head, *body):
        """
        Parameters:
            head (Literal):
                The Literal that represents this simple logic Rule's consequent.
            body (set of Literals):
                The Literals which in conjunction represent this somple logic
                Rule's antecedent.
        Return type: None
        """
        # TODO: Implement check to ensure head is Literal.
        #     Currently this property is assumed.
        self._head = head
        # TODO: Implement check to body is a nonempty iterable of Literals.
        #     Currently this property is assumed.
        self._body = frozenset(body)
    
    @property  # no setter for head; this value should not change.
    def head(self):
        """Read-only accessor for self.head"""
        return self._head

    @property  # no setter for body; this value should not change.
    def body(self):
        """Read-only accessor for self.body"""
        return self._body
    
    @property  # no setter for is_supported
    def is_supported(self):
        """
        True if this Rule is (or more, all the Literals in its body are)
            supported by the KB, and False if not.
        This value is calculated only once on the first call.
        """
        if not hasattr(self, "_supported"):  # If first call to this method
            supported = True  # Assume this Rule is supported
            for l in self.body:
                if not l.is_supported:
                    supported = False  # If any l is unsupported, so is R.
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
        """Hash is based on self.head and self.body"""
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