from __future__ import annotations

from typing import List
from .semantics import Semantics

from probably.pgcl.ast import program as pgcl_program
from probably.pgcl.ast import Node, VarDecl, ParameterDecl

class Program:
    def __init__(self, _semantics: Semantics, _sub_list: ProgramList):  
        self.semantics = _semantics
        self.sub_list = _sub_list
    
    def __str__(self):
        sub_expr_list: List[str] = []
        for sub_expr in self.sub_list:
            sub_expr_list.append(str(sub_expr))
        return self.semantics.buildProgramString(sub_expr_list)
    
    def size(self) -> int:
        res = 1
        for sub_expr in self.sub_list:
            res += sub_expr.size()
        return res

    def to_pgcl(self) -> List[Node]:
        sub_pgcl_list: List[List[Node]] = []
        for sub_program in self.sub_list:
            sub_pgcl_list.append(sub_program.to_pgcl())
            
        return self.semantics.buildPGCLProgram(sub_pgcl_list)
    
    
    
ProgramList = List[Program]
ProgramStorage = List[ProgramList]