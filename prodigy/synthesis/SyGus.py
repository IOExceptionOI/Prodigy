from typing import List

from prodigy.synthesis.grammar import SynthesisGrammar, Rule, Grammar
from prodigy.synthesis.program import ProgramList, ProgramStorage

from prodigy.analysis.analyzer import compute_semantics
from prodigy.analysis.config import ForwardAnalysisConfig
from prodigy.analysis.equivalence.equivalence_check import check_equivalence

import logging
from prodigy.util.logger import log_setup

from probably.pgcl.parser import parse_pgcl
from probably.pgcl.compiler import compile_pgcl
from probably.pgcl.ast.instructions import Instr
from probably.pgcl.ast.expressions import Expr
from probably.pgcl.ast.declarations import Decl
logger = log_setup(str(__name__).rsplit(".", maxsplit=1)[-1], logging.DEBUG)

def SyGus(grammar: Grammar) -> None:
    grammar.indexSymbol()
    for symbol in grammar.symbolist:
        print(f"NonTerminal: {symbol}, id: {symbol.id}")
    grammar.print()
    
    #TODO: implement the SyGus algorithm
    MAX_SIZE = 11
    
    program_storage: ProgramStorage = [[[] for _ in range(MAX_SIZE)] for _ in range(len(grammar.symbolist))]
    #program_storage: ProgramStorage = [[] for _ in range(len(grammar.symbolist))]
    
    #print(f"program_storage: {program_storage}")
    for size in range(1, MAX_SIZE):
        logger.debug(f"Synthesizing programs of size {size}...")
        print(f"Synthesizing programs of size {size}...")
    
    # traverse the NonTernimal List in Grammar
        for non_terminal in grammar.symbolist:
            logger.debug(f"CurrentNoneTerminal: {non_terminal}")
            print(f"Current NonTerminal: {non_terminal}")
            #program_storage[non_terminal.id][size].append(None)
            #print(f"program_storage: {program_storage}")
            
            # traverse the rule list in NonTerminal
            for rule in non_terminal.rule_list:
                logger.debug(f"Current Rule: {rule}")
                print(f"Current Rule: {rule}")
                #using the rule to generate the program
                for candidate_program in constructPrograms(rule, size, program_storage):
                    print("--------------------------------")
                    print(f"candidate_program: {candidate_program}")
                    print("--------------------------------")
                    program_storage[non_terminal.id][size].append(candidate_program)
                    pgcl_program = candidate_program.to_pgcl()
                    
                    if (not isinstance(pgcl_program, Expr)) and (not isinstance(pgcl_program, Decl)):
                        instrs = "\n".join(map(str, pgcl_program))
                        print(f"pgcl_program: \n{instrs}\n")
                       
                    else:
                        
                        print(f"pgcl_program: {pgcl_program}")
                    
                    # if isinstance(candidate_program, Instr):
                    #     pgcl_program = candidate_program.to_pgcl()
                    #     print(f"pgcl_program: {pgcl_program}")
                    
                    #parsed_pgcl_program = parse_pgcl(pgcl_program)
                    #print(parsed_pgcl_program)
                    # if Instruction:
                    if non_terminal.id == 0:
                        pass

            
            
            
def constructPrograms(rule: Rule, size: int, program_storage: ProgramStorage) -> ProgramList:
    logger.info(f"Constructing program from rule: {rule}, size: {size}")
    print(f"Constructing program from rule: {rule}, size: {size}")
    #TODO: implement the constructProgram function
    
    size_pool: List[List[int]] = []
    
    index = 0
    
    # count the size of the programes in each para
    for para in rule.para_list:
        #print(f"para: {para}")
        size_list: List[int] = []
        # count the size of the programes in each para
        for i in range(size):
            #print(f"para.id: {para.id}, i: {i}")
            if(program_storage[para.id][i]):
                size_list.append(i)
        
        logger.debug(f"para: {para}, size_list: {size_list}")
        print(f"para: {para}, size_list: {size_list}")
        size_pool.append(size_list)
    
    res: ProgramList = []
    
    # access all the possible size combination  
    for scheme in getAllSizeScheme(size - 1, size_pool):
        
        sub_programs: ProgramStorage = []
        for i in range(len(scheme)):
            sub_programs.append(program_storage[rule.para_list[i].id][scheme[i]])
    
        sub_list: ProgramList = [] 

        #build all combinations of programs
        buildAllCombinations(0, sub_programs, rule, sub_list, res)
    
    return res
        

def getAllSizeScheme(size: int, size_pool: List[List[int]]) -> List[List[int]]:
    tmp: List[int] = []
    res: List[List[int]] = []
    _getAllSizeScheme(0, size, size_pool, tmp, res)
    return res

def _getAllSizeScheme(pos: int, rem: int, size_pool: List[List[int]], tmp: List[int], res: List[List[int]]):
    # if the size_pool is exhausted, and the remaining size is 0, add the tmp to the res
    # len(size_pool) is the size of the para_list in the rule
    if pos == len(size_pool):
        if rem == 0:
            res.append(tmp.copy())
            return
            
    #! MAYBE WRONG HERE
    if pos < len(size_pool):
        for size in size_pool[pos]:
            # if the size is greater than the remaining size, skip
            if size > rem:
                continue
            tmp.append(size)
            _getAllSizeScheme(pos + 1, rem - size, size_pool, tmp, res)
            tmp.pop()
    
        
def buildAllCombinations(pos: int, sub_programs: ProgramStorage, rule: Rule, sub_list:ProgramList, res: ProgramList):
    # if the sub_program is exhausted, add the sub_list to the res
    if pos == len(sub_programs):
        res.append(rule.buildProgram(sub_list.copy()))
        return
    
    # traverse the sub_program list of each para
    for sub_program in sub_programs[pos]:
        sub_list.append(sub_program)
        buildAllCombinations(pos + 1, sub_programs, rule, sub_list, res)
        sub_list.pop()
    
    
    
if __name__ == "__main__":
    grammar = SynthesisGrammar()
    SyGus(grammar)
