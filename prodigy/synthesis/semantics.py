from __future__ import annotations
from typing import List, Union
from decimal import Decimal
from fractions import Fraction
from abc import ABC, abstractmethod
from probably.pgcl.ast import Node, Var
from probably.pgcl.ast.expressions import Expr, VarExpr, NatLitExpr, RealLitExpr    
from probably.pgcl.ast.instructions import Instr
from probably.pgcl.ast.expressions import CUniformExpr, BernoulliExpr, GeometricExpr, PoissonExpr, BinomialExpr, LogDistExpr, IidSampleExpr

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
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> Union[List[Node], List[Instr], Expr, VarDecl, ParameterDecl]:
        pass

class InstructionSemantics(Semantics):
    @abstractmethod
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        pass

class ExpressionSemantics(Semantics):
    @abstractmethod
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> Expr:
        pass
    
# Instruction_Semantics:
class InstructionSequanceSemantics(InstructionSemantics):
    def __init__(self):
        super().__init__('InstructionSequance')
    
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        res: List[Instr] = []
        for sub_pgcl in sub_pgcl_list:
            res.extend(sub_pgcl)
        return res
    
from probably.pgcl.ast.instructions import IfInstr
class IfInstrSemantics(InstructionSemantics):
    def __init__(self):
        super().__init__('IfInstr')
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        res: List[Instr] = []
        cond: Expr = sub_pgcl_list[0]
        true: List[Instr] = sub_pgcl_list[1]
        false: List[Instr] = sub_pgcl_list[2]
        res.append(IfInstr(cond=cond, true=true, false=false))
        return res
        
from probably.pgcl.ast.instructions import AsgnInstr
class AssignInstrSemantics(InstructionSemantics):
    def __init__(self):
        super().__init__('AssignInstr')
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        res: List[Instr] = []
        lhs: Var = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        res.append(AsgnInstr(lhs=lhs, rhs=rhs))
        return res
        
from probably.pgcl.ast.instructions import ChoiceInstr
class ChoiceInstrSemantics(InstructionSemantics):
    def __init__(self):
        super().__init__('ChoiceInstr')
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        res: List[Instr] = []
        lhs = sub_pgcl_list[0]
        prob = sub_pgcl_list[1]
        rhs = sub_pgcl_list[2]
        res.append(ChoiceInstr(prob=prob, lhs=lhs, rhs=rhs))
        return res
    
from probably.pgcl.ast.instructions import SkipInstr
class SkipInstrSemantics(InstructionSemantics):
    def __init__(self):
        super().__init__('SkipInstr')
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> List[Instr]:
        res: List[Instr] = []
        res.append(SkipInstr())
        return res
# Expression_Semantics:
from probably.pgcl.ast.expressions import BinopExpr, Binop
class OrExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('OrExpr')
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.OR
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
        
class AndExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('AndExpr')
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.AND
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
class EqExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('EqExpr')
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.EQ
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
    
class LeqExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('LeqExpr')
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.LEQ
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
    
class LtExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('LtExpr')
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.LT
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
    
class GeqExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('GeqExpr')
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.GEQ
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
    
class GtExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('GtExpr')
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.GT
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
    
    
class AddExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__("AddExpr")
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.PLUS
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)

class SubExprSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__("SubExpr")
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> BinopExpr:
        operator: Binop = Binop.MINUS
        lhs: Expr = sub_pgcl_list[0]
        rhs: Expr = sub_pgcl_list[1]
        return BinopExpr(operator=operator, lhs=lhs, rhs=rhs)
    
# Distribution_Semantics:
class UniformDistributionSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('UniformDistribution')
   
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> CUniformExpr:
        start: Expr = sub_pgcl_list[0]
        end: Expr = sub_pgcl_list[1]
        return CUniformExpr(start=start, end=end)
    
class BernoulliDistributionSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('BernoulliDistribution')
    
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> BernoulliExpr:
        param: Expr = sub_pgcl_list[0]
        return BernoulliExpr(param=param)
    
class GeometricDistributionSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('GeometricDistribution')
    
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> GeometricExpr:
        param: Expr = sub_pgcl_list[0]
        return GeometricExpr(param=param)
    
class PoissonDistributionSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('PoissonDistribution')
    
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> PoissonExpr:
        param: Expr = sub_pgcl_list[0]
        return PoissonExpr(param=param)
    
class BinomialDistributionSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('BinomialDistribution')
    
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> BinomialExpr:
        n: Expr = sub_pgcl_list[0]
        p: Expr = sub_pgcl_list[1]
        return BinomialExpr(n=n, p=p)
    
class LogDistributionSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('LogDistribution')
   
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> LogDistExpr:
        param: Expr = sub_pgcl_list[0]
        return LogDistExpr(param=param)
    
class IidSampleSemantics(ExpressionSemantics):
    def __init__(self):
        super().__init__('IidSample')
    
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> IidSampleExpr:
        sampling_dist: Expr = sub_pgcl_list[0]
        variable: Var = sub_pgcl_list[1]
        return IidSampleExpr(sampling_dist=sampling_dist, variable=variable)
    
        
# Var_Semantics:
class VarSemantics(ExpressionSemantics):
    def __init__(self, _para_name=None):
        super().__init__('Var')
        self.para_name: Var = _para_name
    def __str__(self):
        if self.para_name is None:
            return self.semantic_name
        return self.para_name
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> Var:
        return self.para_name
class VarExprSemantics(ExpressionSemantics):
    def __init__(self, _para_name=None):
        super().__init__('VarExpr')
        self.para_name: Var = _para_name
    def __str__(self):
        if self.para_name is None:
            return self.semantic_name
        return f"VarExpr('{self.para_name}')"
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> VarExpr:
        return VarExpr(var=self.para_name)
# Param_Semantics:
class ParamSemantics(ExpressionSemantics):
    def __init__(self, _para_name=None):
        super().__init__('Param')
        self.para_name: Var = _para_name
    def __str__(self):
        if self.para_name is None:
            return self.semantic_name
        return f"VarExpr('{self.para_name}')"
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> Var:
        return VarExpr(var=self.para_name)
# VarDecl_Semantics:
from probably.pgcl.ast.declarations import VarDecl
from probably.pgcl.ast.types import Type
class VarDeclSemantics(ExpressionSemantics):
    def __init__(self, _para_name=None, _type=None):
        super().__init__('VarDecl')
        self.para_name: Var = _para_name 
        self.type: Type = _type
    def __str__(self):
        if self.para_name is None:
            return self.semantic_name
        return self.para_name
    
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> VarDecl:
        return VarDecl(self.para_name, self.type)
# ParamDecl_Semantics:
from probably.pgcl.ast.declarations import ParameterDecl
class ParamDeclSemantics(ExpressionSemantics):
    def __init__(self, _para_name=None, _type=None):
        super().__init__('ParamDecl')
        self.para_name: Var = _para_name 
        self.type: Type = _type
    def __str__(self):
        if self.para_name is None:
            return self.semantic_name
        return self.para_name
    
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> ParameterDecl:
        if self.type is None or self.para_name is None:
            raise ValueError("Type or parameter name is None")
        return ParameterDecl(self.para_name, self.type) 
    
class NatLitExprSemantics(ExpressionSemantics):
    def __init__(self, _value: int):
        super().__init__('NatLitExpr')
        self.value: int = _value
    def __str__(self):
        if self.value is None:
            return self.semantic_name
        return str(self.value)
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> NatLitExpr:
        if self.value is None:
            raise ValueError("Value is None")
        return NatLitExpr(value=self.value)
    
class RealLitExprSemantics(ExpressionSemantics):
    def __init__(self, _value: Union[Decimal, Fraction]):
        super().__init__('RealLitExpr')
        self.value: Union[Decimal, Fraction] = _value
    def __str__(self):
        if self.value is None:
            return self.semantic_name
        return str(self.value)
    def buildPGCLProgram(self, sub_pgcl_list: List[List[Node]]) -> RealLitExpr:
        if self.value is None:
            raise ValueError("Value is None")
        return RealLitExpr(value=self.value)
