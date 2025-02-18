from __future__ import annotations

_PGCL_GRAMMAR = """
    start: instructions
    
    declarations: declaration* -> declarations
    declaration: "bool" var                 -> bool
            | "nat" var                     -> nat
            | "real" var                    -> real
            | "const" var ":=" expression   -> const
            | "rparam" var                  -> rparam
            | "nparam" var                  -> nparam
            
    instructions: instruction* -> instructions

    instruction: "skip"                                      -> skip
               | "if" "(" expression ")" block "else"? block -> if
               | var ":=" rvalue                             -> assign
               | block "[" expression "]" block              -> choice
               
    block: "{" instruction* "}"

    rvalue: "unif_d" "(" expression "," expression ")" -> duniform
          | "unif" "(" expression "," expression ")" -> duniform
          | "unif_c" "(" expression "," expression ")" -> cuniform
          | "geometric" "(" expression ")" -> geometric
          | "poisson" "(" expression ")" -> poisson
          | "logdist" "(" expression ")" -> logdist
          | "binomial" "(" expression "," expression ")" -> binomial
          | "bernoulli" "(" expression ")" -> bernoulli
          | "iid" "(" rvalue "," var ")" -> iid
          | expression
          
    expression: expression "||" expression  -> or
          | expression "&" expression       -> and
          | expression "<=" expression      -> leq
          | expression "<" expression       -> le
          | expression ">=" expression      -> geq
          | expression ">" expression       -> ge
          | expression "=" expression       -> eq
          | expression "+" expression       -> add
          | expression "-" expression       -> sub
          | expression "*" expression       -> mul
          | expression "/" expression       -> div
          | expression "%" expression       -> mod
          | expression "^" expression       -> power
          | "not" expression                -> neg
          | "(" expression ")"              -> parens
          | "[" expression "]"              -> iverson
          | literal
          | var


    literal: "true"  -> true
           | "false" -> false
           | INT     -> nat
           | FLOAT   -> real
          

    var: CNAME


"""

#TODO: implement the corresponding semantics and rules for decalaration, instruction, expression, etc.
from probably.pgcl.ast import declarations, instructions, expressions, program
from probably.pgcl.ast import Node
from probably.pgcl.ast.expressions import ExprClass, VarExpr

from prodigy.synthesis.program import Program, ProgramList, ProgramStorage
from prodigy.synthesis.semantics import Semantics, EqExprSemantics, LeqExprSemantics, LtExprSemantics, GeqExprSemantics, GtExprSemantics
from prodigy.synthesis.semantics import AndExprSemantics, OrExprSemantics, IfInstrSemantics
from prodigy.synthesis.semantics import AssignInstrSemantics, ChoiceInstrSemantics, InstructionSequanceSemantics
from prodigy.synthesis.semantics import AddExprSemantics, SubExprSemantics
from prodigy.synthesis.semantics import UniformDistributionSemantics, BernoulliDistributionSemantics, GeometricDistributionSemantics, PoissonDistributionSemantics, BinomialDistributionSemantics, LogDistributionSemantics, IidSampleSemantics
from prodigy.synthesis.semantics import VarDeclSemantics, ParamDeclSemantics
from prodigy.synthesis.semantics import VarSemantics, VarExprSemantics, ParamSemantics
from prodigy.synthesis.semantics import NatLitExprSemantics
from prodigy.synthesis.semantics import RealLitExprSemantics
from decimal import Decimal
from fractions import Fraction

from typing import List, Optional
from abc import ABC, abstractmethod


class NonTerminal():
    def __init__(self, _type: Node, _name: str):
        self.type = _type
        self.name = _name
        self.rule_list: List[Rule] = []
        self.id = 0
    
    def __str__(self) -> str:
        return self.name
    
NTList = List[NonTerminal]


"""
    instructions: instruction* -> instructions

    instruction: "skip"                                      -> skip
               | "if" "(" expression ")" block "else"? block -> if
               | var ":=" rvalue                             -> assign
               | block "[" expression "]" block              -> choice
               
    block: "{" instruction* "}" -> instruction
"""

from probably.pgcl.ast.instructions import InstrClass
#from .semantics import IfInstrSemantics, AssignInstrSemantics, ChoiceInstrSemantics, InstructionSequanceSemantics
class Instruction(NonTerminal):
    def __init__(self):
        super().__init__(InstrClass, 'Instruction')
        self.rule_list = None
        
from probably.pgcl.ast.declarations import VarDecl
#from .semantics import VarSemantics  
class Var(NonTerminal):
    def __init__(self):
        super().__init__(VarDecl, 'Var')
        self.rule_list = None
    #TODO: add the rule for the parameter list

class VarExpression(NonTerminal):
    def __init__(self):
        super().__init__(VarExpr, 'VarExpression')
        self.rule_list = None
    
from probably.pgcl.ast.declarations import ParameterDecl


class Param(NonTerminal):
    def __init__(self):
        super().__init__(ParameterDecl, 'Param')    
        self.rule_list = None
    #TODO: add the rule for the parameter list
   
    
        
"""
    expression: expression "||" expression  -> or
          | expression "&" expression       -> and
          | expression "<=" expression      -> leq
          | expression "<" expression       -> le
          | expression ">=" expression      -> geq
          | expression ">" expression       -> ge
          | expression "=" expression       -> eq
          | expression "+" expression       -> add
          | expression "-" expression       -> sub
          | expression "*" expression       -> mul
          | expression "/" expression       -> div
          | expression "%" expression       -> mod
          | expression "^" expression       -> power
          | "not" expression                -> neg
          | "(" expression ")"              -> parens
          | "[" expression "]"              -> iverson
          | literal -> Param(Param)
          | var -> (Var)
"""

from probably.pgcl.ast.expressions import ExprClass
#from .semantics import OrExprSemantics, AndExprSemantics, AddExprSemantics, VarSemantics, ParamSemantics
class Expression(NonTerminal):
    def __init__(self):
        super().__init__(ExprClass, 'Expression')
        self.rule_list = None
                
class BoolExpression(NonTerminal):
    def __init__(self):
        super().__init__(ExprClass, 'BoolExpression')
        self.rule_list = None
        
class DistExpression(NonTerminal):
    def __init__(self):
        super().__init__(ExprClass, 'DistExpression')
        self.rule_list = None
        
class IidExpression(NonTerminal):
    def __init__(self):
        super().__init__(ExprClass, 'IidExpression')
        self.rule_list = None
        
class ArithExpression(NonTerminal):
    def __init__(self):
        super().__init__(ExprClass, 'ArithExpression')
        self.rule_list = None
        
class Probe(NonTerminal):
    def __init__(self):
        super().__init__(ExprClass, 'Probe')
        self.rule_list = None
    
class Number(NonTerminal):
    def __init__(self):
        super().__init__(ExprClass, 'Number')
        self.rule_list = None   
        
        
        
# Rule Definition
class Rule(ABC):
    def __init__(self, _para_list:NTList):
        self.para_list: NTList = _para_list
        
    @abstractmethod 
    def buildProgram(self, sub_list:ProgramList) -> Program:
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
class ConcreteRule(Rule):
    def __init__(self, _para_list:NTList, _semantics: Semantics):
        super().__init__(_para_list)
        self.semantics: Semantics = _semantics
    
    def __str__(self) -> str:
        res: str = str(self.semantics)
        if len(self.para_list) > 0:
            res += '('
            for para in self.para_list:
                res += str(para) + ','
            res = res[:-1] + ')'
            
        return res
        
    def buildProgram(self, sub_list:ProgramList) -> Program:
        return Program(self.semantics, sub_list)
    
    

        

 
class Grammar():
    def __init__(self, _start: NonTerminal, _symbolist: List[NonTerminal]):
        self.start: NonTerminal = _start
        self.symbolist: List[NonTerminal] = _symbolist
        self.pos = 0
        for i, symbol in enumerate(self.symbolist):
            if(symbol.name == self.start.name):
                self.pos = i
                break
        # swap the start symbol to the first position
        self.symbolist[0], self.symbolist[self.pos] = self.symbolist[self.pos], self.symbolist[0]
        
        
    def indexSymbol(self) -> None:
        for i, symbol in enumerate(self.symbolist):
            symbol.id = i
            
    def print(self) -> None:
        print(f'start: {self.start}')
        for symbol in self.symbolist:
            print("================================================")
            print(f'NonTerminal: {symbol}')
            index = 0
            for rule in symbol.rule_list:
                print(f'Rule {index}: {rule}')
                index += 1
                
class NonTerminalFactory:
    _instruction = None
    #_expression = None
    _bool_expression = None
    _dist_expression = None
    _iid_expression = None
    _arith_expression = None
    _probe = None
    _var = None
    _var_expression = None
    _param = None
    _number = None
    @classmethod
    def instruction(cls):
        if cls._instruction is None:
            cls._instruction = Instruction()
        return cls._instruction

    @classmethod
    def bool_expression(cls):
        if cls._bool_expression is None:
            cls._bool_expression = BoolExpression()
        return cls._bool_expression
    
    @classmethod
    def dist_expression(cls):
        if cls._dist_expression is None:
            cls._dist_expression = DistExpression()
        return cls._dist_expression
    
    @classmethod
    def iid_expression(cls):
        if cls._iid_expression is None:
            cls._iid_expression = IidExpression()
        return cls._iid_expression
    
    @classmethod
    def arith_expression(cls):
        if cls._arith_expression is None:
            cls._arith_expression = ArithExpression()
        return cls._arith_expression
    
    @classmethod
    def probe(cls):
        if cls._probe is None:
            cls._probe = Probe()
        return cls._probe
    
    @classmethod
    def number(cls):
        if cls._number is None:
            cls._number = Number()
        return cls._number
    
    @classmethod
    def var(cls):
        if cls._var is None:
            cls._var = Var()
        return cls._var

    @classmethod
    def var_expression(cls):
        if cls._var_expression is None:
            cls._var_expression = VarExpression()
        return cls._var_expression

    @classmethod
    def param(cls):
        if cls._param is None:
            cls._param = Param()
        return cls._param

class SynthesisGrammar(Grammar):
    def __init__(self):
        # get the instance of the NonTerminal through the factory
        self.instruction = NonTerminalFactory.instruction()
        #self.expression = NonTerminalFactory.expression()
        self.bool_expression = NonTerminalFactory.bool_expression()
        self.dist_expression = NonTerminalFactory.dist_expression()
        self.iid_expression = NonTerminalFactory.iid_expression()
        self.arith_expression = NonTerminalFactory.arith_expression()
        self.probe = NonTerminalFactory.probe()
        self.var = NonTerminalFactory.var()
        self.var_expression = NonTerminalFactory.var_expression()
        self.param = NonTerminalFactory.param()
        self.number = NonTerminalFactory.number()
        super().__init__(
            _start=self.instruction,
            _symbolist=[self.instruction, self.bool_expression, self.dist_expression, self.iid_expression, self.arith_expression, self.var, self.var_expression, self.param, self.probe, self.number]
        )
        
        self.instruction.rule_list =[
            # instruction* -> instructions
            ConcreteRule([self.instruction, self.instruction], InstructionSequanceSemantics()),
            #| "if" "(" expression ")" block "else"? block -> if
            ConcreteRule([self.bool_expression, self.instruction, self.instruction],IfInstrSemantics()),
            #| var ":=" rvalue                             -> assign
            ConcreteRule([self.var, self.dist_expression],AssignInstrSemantics()),
            ConcreteRule([self.var, self.iid_expression],AssignInstrSemantics()),
            ConcreteRule([self.var, self.arith_expression],AssignInstrSemantics()),
            ConcreteRule([self.var, self.number],AssignInstrSemantics()),
            ConcreteRule([self.var, self.var_expression],AssignInstrSemantics()),
            #| block "[" expression "]" block              -> choice
            ConcreteRule([self.instruction, self.probe, self.instruction],ChoiceInstrSemantics()),
            
            ]
        
        #self.expression.rule_list = [
            #| expression "||" expression  -> or
            #ConcreteRule([self.expression, self.expression],OrExprSemantics()),
            #| expression "&" expression       -> and
            #ConcreteRule([self.expression, self.expression],AndExprSemantics()),
            #| expression "+" expression -> add
            #ConcreteRule([self.expression, self.expression],AddExprSemantics()),
            #| Var
            #ConcreteRule([self.var], VarSemantics()),
            #| Param
            #ConcreteRule([self.param], RParamSemantics())
        #]
        '''
        bool_expr: var "=" number                          -> var_eq_num
             | var "=" var                                 -> var_eq_var
             | var "<=" number                             -> var_leq_num
             | var "<" number                              -> var_lt_num
             | var ">=" number                             -> var_geq_num
             | var ">" number                              -> var_gt_num
             | bool_expr "&" bool_expr                     -> and
             | bool_expr "|" bool_expr                     -> or
             | "not" bool_expr  no-need  
        '''
        self.bool_expression.rule_list = [
            
            ConcreteRule([self.var_expression, self.number], EqExprSemantics()),
            ConcreteRule([self.var_expression, self.var_expression], EqExprSemantics()),
            ConcreteRule([self.var_expression, self.number], LeqExprSemantics()),
            ConcreteRule([self.var_expression, self.number], LtExprSemantics()),
            ConcreteRule([self.var_expression, self.number], GeqExprSemantics()),
            ConcreteRule([self.var_expression, self.number], GtExprSemantics()),
            ConcreteRule([self.bool_expression, self.bool_expression], AndExprSemantics()),
            ConcreteRule([self.bool_expression, self.bool_expression], OrExprSemantics()),
        ]
        '''
        simple_arith: var "+" var                         -> add_vars
                | var "-" var                             -> sub_vars
                | var "+" number                          -> add_const
                | var "-" number
        '''
        self.arith_expression.rule_list = [
            ConcreteRule([self.var_expression, self.var_expression], AddExprSemantics()),
            ConcreteRule([self.var_expression, self.var_expression], SubExprSemantics()),
            ConcreteRule([self.var_expression, self.number], AddExprSemantics()),
            ConcreteRule([self.var_expression, self.number], SubExprSemantics()),
        ]
        
        self.dist_expression.rule_list = [
            #ConcreteRule([self.number, self.number], UniformDistributionSemantics()),
            ConcreteRule([self.probe], BernoulliDistributionSemantics()),
            ConcreteRule([self.number, self.probe], BinomialDistributionSemantics()),
            ConcreteRule([self.probe], GeometricDistributionSemantics()),
            ConcreteRule([self.number], PoissonDistributionSemantics()),
            ConcreteRule([self.probe], LogDistributionSemantics()),
        ]
        
        self.iid_expression.rule_list = [
            ConcreteRule([self.dist_expression, self.var_expression], IidSampleSemantics()),
        ]
        
        self.probe.rule_list = [
            # ConcreteRule([], RealLitExprSemantics(Fraction(0))),
            # ConcreteRule([], RealLitExprSemantics(Fraction(1, 2))),
            # ConcreteRule([], RealLitExprSemantics(Fraction(1, 3))),
            # ConcreteRule([], RealLitExprSemantics(Fraction(1, 4))),
            # ConcreteRule([], RealLitExprSemantics(Fraction(1, 5))),
            # ConcreteRule([], RealLitExprSemantics(Fraction(1, 6))),
            # ConcreteRule([], RealLitExprSemantics(Fraction(1, 7))),
            # ConcreteRule([], RealLitExprSemantics(Fraction(1, 8))),
            # ConcreteRule([], RealLitExprSemantics(Fraction(1, 9))),
            # ConcreteRule([], RealLitExprSemantics(Fraction(1, 10))),
        ]
        
        self.number.rule_list = [
            # ConcreteRule([], NatLitExprSemantics(0)),
            # ConcreteRule([], NatLitExprSemantics(1)),
            # ConcreteRule([], NatLitExprSemantics(2)),
            # ConcreteRule([], NatLitExprSemantics(3)),
            # ConcreteRule([], NatLitExprSemantics(4)),
            # ConcreteRule([], NatLitExprSemantics(5)),
            # ConcreteRule([], NatLitExprSemantics(6)),
            # ConcreteRule([], NatLitExprSemantics(7)),
            # ConcreteRule([], NatLitExprSemantics(8)),
            # ConcreteRule([], NatLitExprSemantics(9)),
        ]
        
        #from .semantics import VarSemantics
        self.var.rule_list = [
            ConcreteRule([],VarSemantics('Var0')),
            #ConcreteRule([],VarSemantics('Var1')),
        ]
        self.var_expression.rule_list = [
            ConcreteRule([],VarExprSemantics('Var0')),
        ]
        #from .semantics import ParamSemantics
        self.param.rule_list = [
            ConcreteRule([],ParamSemantics('Param3')),
            #ConcreteRule([],ParamSemantics('Param1')),
        ]
        
        # add the param to the rule of probe
        self.probe.rule_list.extend(self.param.rule_list)
        # add the param to the rule of number
        self.number.rule_list.extend(self.param.rule_list)
        
        # TODO: add the rule for the variable and parameter Declaration
        # from probably.pgcl.ast.types import NatType
        # from .semantics import VarDeclSemantics
        # self.var.rule_list = [
        #     ConcreteRule([],VarDeclSemantics('Var0', NatType(bounds=None))),
        #     ConcreteRule([],VarDeclSemantics('Var1', NatType(bounds=None))),
        # ]
        # from .semantics import ParamDeclSemantics
        # self.param.rule_list = [
        #     ConcreteRule([],ParamDeclSemantics('Param0', NatType(bounds=None))),
        #     ConcreteRule([],ParamDeclSemantics('Param1', NatType(bounds=None))),
        # ]
        
        # self.expression.rule_list.extend(self.var.rule_list)
        # self.expression.rule_list.extend(self.param.rule_list)
