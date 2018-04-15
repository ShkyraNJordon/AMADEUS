"""
amadeus.logic - A Simple Logic
@author: Sh'kyra Jordon
------------------------------

This system assumes the following base logic:

    Atoms:
        * Atoms are facts asserted to be true
    
    Negation:
        * Negated atoms are facts asserted to be false
        * Negation can only be applied to atoms (and Literals, where the
            negation of a negated atom is the original atom.
        * The notation for a negated atom "a" is "~a".
    
    Literals:
        * Atoms and negated atoms are literals
        * An atom is distinct from its negated atom.
        * Similarly, literals are distinct from one another.
    
    Clauses:
        Clauses are in the form:
            a_1, ..., a_n
        where all a_i are literals.
        
        * , is logical conjunction.
        * There is no logical disjunction in this base logic.
        * Thus, all Clauses are in conjunctive negation normal form, with the
            absence of logical disjunction as a binary operator. 
        
        Note that conjunctions of clauses equate to a single clause, and can be
            reduced as such.
        Similarly, a single Literal can equate to a single Clause and can be
            extended as such.
    
    Rules:
        Rules are in the form:
            b :- c
        where c is a (antecedent) Clause and b is a (consequent) Literal.
        
        * :- is mons ponens, the only proof rule.
    
    Propositions:
        Literals, Clauses and Rules will be referred to as "propositions".

"""
   #TODO: Make Literal, Clause and Rules initialisable from PrologStrings         
class Literal():
    """Creates a Literal that is either a positive or negative atom.
    
    :param atom: An atomic fact
    :type atom: str (case-sensitive)
    :param positivity: T/F if atom should be asserted to be T/F. If None, the value assumed is T.
    :type positivity: bool | None
    """
    
    def __init__(self, atom, positivity=None):
        if positivity is None:  # Only one argument was passed
            positivity = True
        self._atom = str(atom)
        self._positivity = positivity
    
    @property
    def atom(self):
        return self._atom
    
    @property
    def is_negated(self):
        """Checks whether the Literal represents a negated atom."""
        return self._positivity == False
    
    def invert(self):
        return Literal(self._atom, not self._positivity)
    
    def __str__(self):
        """Prints the Literal instance in prolog syntax"""
        prefix = ""
        if self.is_negated:
            prefix = "~"
        return prefix + self._atom

    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        """Equality is based on the equality of the atom (str) and sign (boolean)."""
        if isinstance(other, Literal):
            return (self.atom == other.atom) and (self.is_negated == other.is_negated)
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

    
class Clause():
    """A simple clause -- a set of literals (that are assumed to be in
        logical conjunction).
    
    :param literals: The literals assumed to be in logical conjunction for this Clause.
    :type literals: A tuple of Literals.
    """
       
    def __init__(self, *literals):
        self._literals = set(literals)
    
    @property
    def literals(self):
        return self._literals
    
    #TODO make __iadd__
    
    def __str__(self):
        """Prints the Clause instance in prolog syntax"""
        # For the sake of hashability, Clause Literals print in alphabetical order.
        #     However, internally they are stored without order. 
        return ", ".join([str(l) for l in sorted(list(self.literals), key=lambda x: str(x))])
    
    def __iter__(self):
        return iter(self._literals)
        
    def __eq__(self, other):
        """Equality is based on the equality of the literals (Set)"""
        if isinstance(other, Clause):
            return self.literals == other.literals
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(str(self))
    
    
class Rule():
    """A simple rule -- a Literal and Clause | Literal pair, where the former
        is the consequent of the rule, and the latter the antecedent. This order
        is to remain consistent with ProLog syntax.
    
    :param head: The consequent of the simple logic Rule.
    :type head: Literal
    :param body: The antecedent of the simple logic Rule.
    :type body: Clause | Literal
    """
    
    # TODO: Add __hash__ - requires Clause be hashable?
    
    def __init__(self, head, body):
        if isinstance(body, Literal):
            body = Clause(body)
        self._head = head
        self._body = body
    
    @property
    def head(self):
        return self._head

    @property
    def body(self):
        return self._body
    
    def __str__(self):
        """Prints the Rule instance in prolog syntax"""
        return str(self.head) + " :- " + str(self.body) 
    
    def __eq__(self, other):
        """Equality is based on the equality of the head (Literal) and body (Clause)"""
        if isinstance(other, Rule):
            return (self.head == other.head) and (self.body == other.body)
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(str(self))
        
        
if __name__ == "__main__":
    # Making literals example
    alpha, beta, gamma = Literal("alpha"), Literal("beta"), Literal("gamma")
    
    # A clause represents a conjunction of literals.
    clause = Clause(alpha, beta)
    print("My first clause prints as", clause)
    
    # Literals are distinguished by their "atom" name, and their sign.
    print("All positive literals called 'alpha' are considered equivalent:"
          , alpha == Literal("alpha"))
    #TODO Should we make these point to the same space in memory? By use of a DB? 
    
    # Atom names are case sensitive
    print("alpha =/= ALPHA:", alpha != Literal("ALPHA"))
    
    # Rules have a body consisting of a Clause, and a head consisting of a literal.
    rule = Rule(gamma.invert(), clause)
    print("My first rule prints as", rule)
    
    print(Literal("a") == Literal("a"))
    c1 = Clause(Literal("a"), Literal("b"))
    c2 = Clause(Literal("a"), Literal("b"))
    print(c1.literals == c2.literals)
    print(c1 == c2)
    r1 = Rule(gamma, c1)
    r2 = Rule(gamma, c2)
    print(r1==r2)