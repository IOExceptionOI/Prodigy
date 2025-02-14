from __future__ import annotations

from typing import List
from .semantics import Semantics



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
    
    
ProgramList = List[Program]
ProgramStorage = List[ProgramList]