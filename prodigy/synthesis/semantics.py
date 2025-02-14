from __future__ import annotations
from typing import List


class Semantics:
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
    
# Instruction_Semantics:
class IfInstrSemantics(Semantics):
    def __init__(self):
        super().__init__('IfInstr')
        
class AssignInstrSemantics(Semantics):
    def __init__(self):
        super().__init__('AssignInstr')
        
class ChoiceInstrSemantics(Semantics):
    def __init__(self):
        super().__init__('ChoiceInstr')
        
class SkipInstrSemantics(Semantics):
    def __init__(self):
        super().__init__('SkipInstr')

# Expression_Semantics:
class OrExprSemantics(Semantics):
    def __init__(self):
        super().__init__('OrExpr')
        
class AndExprSemantics(Semantics):
    def __init__(self):
        super().__init__('AndExpr')
        
class AddExprSemantics(Semantics):
    def __init__(self):
        super().__init__("AddExpr")

# Var_Semantics:
class VarSemantics(Semantics):
    def __init__(self, _para_name=None):
        super().__init__('Var')
        self.para_name = _para_name 
        
    def __str__(self):
        if self.para_name is None:
            return self.semantic_name
        return self.para_name
        
# Param_Semantics:
class RParamSemantics(Semantics):
    def __init__(self, _para_name=None):
        super().__init__('RParam')
        self.para_name = _para_name 
    def __str__(self):
        if self.para_name is None:
            return self.semantic_name
        return self.para_name
        
