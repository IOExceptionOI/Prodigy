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

from .program import Program, ProgramList, ProgramStorage
from .semantics import Semantics

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
from .semantics import IfInstrSemantics, AssignInstrSemantics, ChoiceInstrSemantics, InstructionSequanceSemantics
class Instruction(NonTerminal):
    def __init__(self):
        super().__init__(InstrClass, 'Instruction')
        self.rule_list = None
        
from probably.pgcl.ast.declarations import VarDecl
from .semantics import VarSemantics  
class Var(NonTerminal):
    def __init__(self):
        super().__init__(VarDecl, 'Var')
        self.rule_list = None
    #TODO: add the rule for the parameter list
   
    
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
from .semantics import OrExprSemantics, AndExprSemantics, AddExprSemantics, VarSemantics, ParamSemantics
class Expression(NonTerminal):
    def __init__(self):
        super().__init__(ExprClass, 'Expression')
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
    _expression = None
    _var = None
    _param = None

    @classmethod
    def instruction(cls):
        if cls._instruction is None:
            cls._instruction = Instruction()
        return cls._instruction

    @classmethod
    def expression(cls):
        if cls._expression is None:
            cls._expression = Expression()
        return cls._expression

    @classmethod
    def var(cls):
        if cls._var is None:
            cls._var = Var()
        return cls._var

    @classmethod
    def param(cls):
        if cls._param is None:
            cls._param = Param()
        return cls._param

class SynthesisGrammar(Grammar):
    def __init__(self):
        # get the instance of the NonTerminal through the factory
        self.instruction = NonTerminalFactory.instruction()
        self.expression = NonTerminalFactory.expression()
        self.var = NonTerminalFactory.var()
        self.param = NonTerminalFactory.param()

        super().__init__(
            _start=self.var,
            _symbolist=[self.instruction, self.expression, self.var, self.param]
        )
        
        self.instruction.rule_list =[
            #| "if" "(" expression ")" block "else"? block -> if
            ConcreteRule([self.expression, self.instruction, self.instruction],IfInstrSemantics()),
            #| var ":=" rvalue                             -> assign
            ConcreteRule([self.var, self.expression],AssignInstrSemantics()),
            #| block "[" expression "]" block              -> choice
            ConcreteRule([self.instruction, self.expression, self.instruction],ChoiceInstrSemantics()),
            # instruction* -> instructions
            ConcreteRule([self.instruction, self.instruction], InstructionSequanceSemantics())
            ]
        
        self.expression.rule_list = [
            #| expression "||" expression  -> or
            ConcreteRule([self.expression, self.expression],OrExprSemantics()),
            #| expression "&" expression       -> and
            ConcreteRule([self.expression, self.expression],AndExprSemantics()),
            #| expression "+" expression -> add
            ConcreteRule([self.expression, self.expression],AddExprSemantics()),
            #| Var
            #ConcreteRule([self.var], VarSemantics()),
            #| Param
            #ConcreteRule([self.param], RParamSemantics())
        ]
        #from .semantics import VarSemantics
        self.var.rule_list = [
            ConcreteRule([],VarSemantics('Var0')),
            ConcreteRule([],VarSemantics('Var1')),
        ]
        #from .semantics import ParamSemantics
        self.param.rule_list = [
            ConcreteRule([],ParamSemantics('Param0')),
            ConcreteRule([],ParamSemantics('Param1')),
        ]
        
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
        
        self.expression.rule_list.extend(self.var.rule_list)
        self.expression.rule_list.extend(self.param.rule_list)
