from __future__ import annotations

import itertools
import logging
from typing import Dict, List, Literal, Tuple, Callable, Sequence, Union

import sympy
from probably.pgcl import (BoolType, Program, VarExpr, Instr)
from prodigy.analysis.config import ForwardAnalysisConfig
from prodigy.analysis.instructionhandler.program_info import ProgramInfo
from prodigy.analysis.solver.solver_type import SolverType
from prodigy.distribution.distribution import Distribution, State
from prodigy.pgcl.pgcl_operations import cav_phi
from prodigy.util.logger import log_setup

logger = log_setup("Test", logging.DEBUG)

def format_instructions(instructions: List[Instr], indent: str = "") -> str:
    """格式化指令列表，使其更易读"""
    result = []
    result.append("")
    for instr in instructions:
        instr_str = str(instr)
        # 保留关键字，但移除类名
        if "WhileInstr" in instr_str:
            cond = instr_str.split('cond=')[1].split(',')[0]
            body = format_instructions(instr.body, indent + "    ")
            result.append(f"{indent}while ({cond}) {{")
            result.append(body)
            result.append(f"{indent}}}")
        elif "IfInstr" in instr_str:
            cond = instr_str.split('cond=')[1].split(',')[0]
            true_body = format_instructions(instr.true, indent + "    ")
            false_body = format_instructions(instr.false, indent + "    ")
            result.append(f"{indent}if ({cond}) {{")
            result.append(true_body)
            result.append(f"{indent}}} else {{")
            result.append(false_body)
            result.append(f"{indent}}}")
        elif "ChoiceInstr" in instr_str:
            prob = instr_str.split('prob=')[1].split(',')[0]
            lhs = format_instructions(instr.lhs, "").strip()
            rhs = format_instructions(instr.rhs, "").strip()
            result.append(f"{indent}{{{lhs}}} [{prob}] {{{rhs}}}")
        elif "AsgnInstr" in instr_str:
            lhs = instr_str.split('lhs=')[1].split(',')[0].strip("'")
            rhs = instr_str.split('rhs=')[1].split(')')[0]
            result.append(f"{indent}{lhs} := {rhs}")
        elif "SkipInstr" in instr_str:
            result.append(f"{indent}skip")
        else:
            # 对于其他类型的指令，保持原样
            result.append(f"{indent}{instr_str}")
    return '\n'.join(result)

def log_program_info(program: Program, prefix: str = "") -> None:
    """记录程序的详细信息"""
    logger.info(f"\n{prefix} 程序详细信息:")
    logger.info(f"变量定义:")
    for var, type_ in program.variables.items():
        logger.info(f"  {var}: {type_}")
    
    if program.parameters:
        logger.info(f"参数定义:")
        for param, type_ in program.parameters.items():
            logger.info(f"  {param}: {type_}")
    
    logger.info(f"程序指令:")
    logger.info(format_instructions(program.instructions, ""))

def log_distribution_info(dist: Distribution, prefix: str = "") -> None:
    """记录分布的详细信息"""
    logger.info(f"\n{prefix} 分布详细信息:")
    logger.info(f"表达式: {dist}")
    # 使用 _variables 和 _parameters 替代 variables 和 parameters
    try:
        logger.info(f"变量: {dist._variables}")
        logger.info(f"参数: {dist._parameters}")
    except AttributeError:
        logger.info("注意: 无法访问分布的变量和参数信息")

def check_equivalence_with_debug(
        program: Program,
        invariant: Program,
        config: ForwardAnalysisConfig,
        analyzer: Callable) -> Tuple[bool, Union[List[Dict[str, str]], State, Distribution]]:
    """带详细调试信息的等价性检查函数"""
    logger.info("\n" + "="*50)
    logger.info("开始等价性检查")
    logger.info("="*50)

    # 1. 记录输入程序
    logger.info("\n=== 输入程序 ===")
    logger.info("原始程序:")
    logger.info(format_instructions(program.instructions, ""))
    logger.info("\n不变式程序:")
    logger.info(format_instructions(invariant.instructions, ""))

    # 2. 生成修改后的不变式
    logger.info("\n=== 修改后的不变式 ===")
    modified_inv = cav_phi(program, invariant)
    logger.info(format_instructions(modified_inv.instructions, ""))

    # 3. 生成测试分布
    logger.info("\n=== 生成测试分布 ===")
    dist = config.factory.one()
    so_vars: Dict[str, str] = {}  # second order variables
    
    for variable in program.variables:
        new_var = dist.get_fresh_variable()
        if isinstance(program.variables[variable], BoolType):
            expr = f"(1+{new_var} * {variable})"
            dist *= config.factory.from_expr(expr,
                                           VarExpr(var=new_var),
                                           VarExpr(var=variable))
        else:
            expr = f"1/(1-{new_var}*{variable})"
            dist *= config.factory.from_expr(expr,
                                           VarExpr(var=new_var),
                                           VarExpr(var=variable))
        so_vars[new_var] = variable
    
    test_dist = dist.set_variables(*program.variables.keys(), *so_vars.keys()).set_parameters()
    logger.info(f"测试分布: {test_dist}")
    logger.info(f"变量映射: {so_vars}")

    # 4. 计算结果
    logger.info("\n=== 计算程序结果 ===")
    modified_inv_result, modified_inv_error = analyzer(
        modified_inv.instructions,
        ProgramInfo(modified_inv, so_vars=frozenset(so_vars.keys())),
        test_dist,
        config.factory.from_expr("0", *(modified_inv.variables | so_vars.keys())),
        config
    )
    
    inv_result, inv_error = analyzer(
        invariant.instructions,
        ProgramInfo(invariant, so_vars=frozenset(so_vars.keys())),
        test_dist,
        config.factory.one(*(modified_inv.variables | so_vars.keys())) * 0,
        config
    )

    # 5. 求解等价性
    logger.info("\n=== 求解等价性 ===")
    diff = inv_result - modified_inv_result
    logger.info(f"分布差异: {diff}")

    params = program.parameters.keys() | invariant.parameters.keys()
    solver = SolverType.make(config.solver_type)

    dist_is_solution, dist_candidates = solver.solve(
        inv_result.set_parameters(*params),
        modified_inv_result.set_parameters(*params)
    )
    err_is_solution, err_candidates = solver.solve(
        inv_error.set_parameters(*params),
        modified_inv_error.set_parameters(*params)
    )

    # 6. 返回结果
    logger.info("\n=== 最终结果 ===")
    if (dist_is_solution and err_is_solution) is False:
        logger.info("验证失败 - 无解")
        state, _ = diff.get_state()
        return False, State({var: state[sym] for sym, var in so_vars.items()})

    if (dist_is_solution and err_is_solution) is True:
        if not dist_candidates:
            logger.info("验证成功 - 使用误差候选解")
            return True, err_candidates
        if not err_candidates:
            logger.info("验证成功 - 使用分布候选解")
            return True, dist_candidates

        res_both = []
        for i, (dist_sol, err_sol) in enumerate(itertools.product(dist_candidates, err_candidates)):
            to_be_solved = []
            for var, constr in dist_sol.items() | err_sol.items():
                equation = sympy.S(f'({var}) - ({constr})')
                to_be_solved.append(equation)
            
            solution = (sympy.solve(to_be_solved, dict=True) if len(to_be_solved) > 1 
                       else sympy.solve(to_be_solved[0], dict=True))
            res_both += solution

        if len(res_both) == 0:
            logger.info("验证失败 - 无匹配解")
            return False, State()
            
        logger.info(f"验证成功 - 最终解空间: {res_both}")
        return True, res_both

    logger.info("结果不确定")
    return None, diff 