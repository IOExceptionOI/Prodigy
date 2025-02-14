from __future__ import annotations
from typing import List, Union
from abc import ABC, abstractmethod
from probably.pgcl.ast import Node, Var
from probably.pgcl.ast.expressions import Expr
from probably.pgcl.ast.instructions import Instr


class Semantics(ABC):
    def __init__(self, _semantic_name: str):
        self.semantic_name = _semantic_name
    def __str__(self):
        return self.semantic_name
    def buildProgramString(self, sub_list: List[str]) -> str:
        res: str = str(self)
        if len(sub_list) > 0:
            res += "("
            for sub in sub_list:
                res += sub + ","
            res = res[:-1] + ")"
        return res

    @abstractmethod
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> Union[List[Node], List[Instr], Expr, VarDecl, ParameterDecl]:
        pass

class InstructionSemantics(Semantics):
    @abstractmethod
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        pass

class ExpressionSemantics(Semantics):
    @abstractmethod
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> Expr:
        pass
    
# Instruction_Semantics:
class InstructionSequanceSemantics(InstructionSemantics):
    def __init__(self):
        super().__init__('InstructionSequance')
    
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        res: List[Instr] = []
        for sub_pgcl in sub_pgcl_list:
            res.extend(sub_pgcl)
        return res
    
from probably.pgcl.ast.instructions import IfInstr
class IfInstrSemantics(InstructionSemantics):
    def __init__(self):
        super().__init__('IfInstr')
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        res: List[Instr] = []
        cond: Expr = sub_pgcl_list[0]
        true: List[Instr] = sub_pgcl_list[1]
        false: List[Instr] = sub_pgcl_list[2]
        res.append(IfInstr(cond, true, false))
        return res
        
from probably.pgcl.ast.instructions import AsgnInstr
class AssignInstrSemantics(InstructionSemantics):
    def __init__(self):
        super().__init__('AssignInstr')
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        res: List[Instr] = []
        lhs: Var = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        res.append(AsgnInstr(lhs, rhs))
        return res
        
from probably.pgcl.ast.instructions import ChoiceInstr
class ChoiceInstrSemantics(InstructionSemantics):
    def __init__(self):
        super().__init__('ChoiceInstr')
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        res: List[Instr] = []
        cond = sub_pgcl_list[0]
        true = sub_pgcl_list[1]
        false = sub_pgcl_list[2]
        res.append(ChoiceInstr(cond, true, false))
        return res
    
from probably.pgcl.ast.instructions import SkipInstr
class SkipInstrSemantics(InstructionSemantics):
    def __init__(self):
        super().__init__('SkipInstr')
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        res: List[Instr] = []
        res.append(SkipInstr())
        return res
# Expression_Semantics:
from probably.pgcl.ast.expressions import BinopExpr, Binop
class OrExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('OrExpr')
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.OR
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
        
class AndExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('AndExpr')
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.AND
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
    

class AddExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__("AddExpr")
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.PLUS
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
    
class SubExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__("SubExpr")
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.MINUS
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
# Var_Semantics:
from probably.pgcl.ast.declarations import VarDecl
from probably.pgcl.ast.types import Type
class VarSemantics(ExpressionSemantics):
    def __init__(self, _para_name=None, _type=None):
        super().__init__('Var')
        self.para_name: Var = _para_name 
        self.type: Type = _type
    def __str__(self):
        if self.para_name is None:
            return self.semantic_name
        return self.para_name
    
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> VarDecl:
        return VarDecl(self.para_name, self.type)
# Param_Semantics:
from probably.pgcl.ast.declarations import ParameterDecl
class RParamSemantics(ExpressionSemantics):
    def __init__(self, _para_name=None, _type=None):
        super().__init__('RParam')
        self.para_name: Var = _para_name 
        self.type: Type = _type
    def __str__(self):
        if self.para_name is None:
            return self.semantic_name
        return self.para_name
    
    def to_pgcl(self, sub_pgcl_list: List[List[Node]]) -> ParameterDecl:
        return ParameterDecl(self.para_name, self.type) 
