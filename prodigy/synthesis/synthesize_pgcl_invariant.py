from __future__ import annotations

from typing import Generator, List, Dict

from probably.pgcl.ast import Program as PgclProgram
from probably.pgcl.ast import Decl, Var, Type, Expr, Instr

from prodigy.synthesis.SyGus import SyGus
from prodigy.synthesis.grammar import SynthesisGrammar, ConcreteRule
from prodigy.synthesis.program import Program
from prodigy.synthesis.semantics import VarSemantics, ParamSemantics, VarExprSemantics

def synthesize_pgcl_invariant(pgcl_program: PgclProgram) -> Generator[PgclProgram, None, None]:
    
    
    # get the declarations, variables, constants, parameters, instructions from the target pgcl program
    declarations: List[Decl] = pgcl_program.declarations.copy()
    variables: Dict[Var, Type] = pgcl_program.variables.copy()
    constants: Dict[Var, Expr] = pgcl_program.constants.copy()
    parameters: Dict[Var, Type] = pgcl_program.parameters.copy()
    #functions = pgcl_program.functions
    instructions: List[Instr] = pgcl_program.instructions.copy()

    # set the synthesis grammar
    grammar = SynthesisGrammar()
    grammar.var.rule_list = []
    grammar.var_expression.rule_list = []
    grammar.param.rule_list = []
    grammar.number.rule_list = []
    grammar.probe.rule_list = []
    
    # get the variables and parameters from the pgcl program
    variables_list: List[Var] = list(variables.keys())
    parameters_list: List[Var] = list(parameters.keys())
    
    for variable in variables_list:
        grammar.var.rule_list.append(ConcreteRule([], VarSemantics(variable)))
        grammar.var_expression.rule_list.append(ConcreteRule([], VarExprSemantics(variable)))
    for parameter in parameters_list:
        grammar.param.rule_list.append(ConcreteRule([], ParamSemantics(parameter)))
        
    from probably.pgcl.ast import ParameterDecl
    from probably.pgcl.ast import NatType, RealType
    # self-added parameters
    
    #grammar.param.rule_list.append(ConcreteRule([], ParamSemantics('Param1')))
    
    declarations.append(ParameterDecl(var='Param0', typ=NatType(bounds=None)))
    declarations.append(ParameterDecl(var='Param1', typ=RealType()))
    # upgrade the param to the rule of param (! Not Necessary)
    grammar.param.rule_list.append(ConcreteRule([], ParamSemantics('Param0')))
    grammar.param.rule_list.append(ConcreteRule([], ParamSemantics('Param1')))
    
    # upgrade the param to the rule of number
    grammar.number.rule_list.append(ConcreteRule([], ParamSemantics('Param0')))
    # upgrade the param to the rule of probe
    grammar.probe.rule_list.append(ConcreteRule([], ParamSemantics('Param1')))
    # # update the SyntehsisGrammar according to the change of variables and parameters
    # grammar.expression.rule_list.extend(grammar.var.rule_list)
    # grammar.expression.rule_list.extend(grammar.param.rule_list)
    
    
    # build the invariant program
    invariant_pgcl_programs: Generator[PgclProgram, None, None] = build_invariant_program(grammar, declarations)
    return invariant_pgcl_programs


def build_invariant_program(synthesisgrammar: SynthesisGrammar, declarations: List[Decl]) -> Generator[PgclProgram, None, None]:
    candidate_pgcl_instructions = SyGus(synthesisgrammar)
    for candidate_pgcl_instruction in candidate_pgcl_instructions:
        
        invariant_pgcl_program = PgclProgram.from_parse(declarations=declarations, instructions=candidate_pgcl_instruction)
        yield invariant_pgcl_program
    #test
    #print(f"invariant_pgcl_program: {invariant_pgcl_program}")
    

