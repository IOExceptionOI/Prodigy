import pytest
from probably.pgcl.compiler import compile_pgcl

from prodigy.analysis.analyzer import compute_discrete_distribution
from prodigy.analysis.config import ForwardAnalysisConfig
from prodigy.distribution.fast_generating_function import ProdigyPGF
from prodigy.distribution.generating_function import SympyPGF
from prodigy.distribution.symengine_distribution import SymenginePGF


@pytest.mark.parametrize('engine,factory',
                         [(ForwardAnalysisConfig.Engine.SYMPY, SympyPGF),
                          (ForwardAnalysisConfig.Engine.GINAC, ProdigyPGF),
                          (ForwardAnalysisConfig.Engine.SYMENGINE, SymenginePGF)])
def test_basic_function(engine, factory):
    prog = compile_pgcl("""
        fun f := {
            nat y;
            y := 42;
            return y;
        }
        nat x;
        x := f(y := 5);
    """)
    res, error_prob = compute_discrete_distribution(
        prog, factory.one(), ForwardAnalysisConfig(engine=engine))
    assert res == factory.from_expr("x^42")


@pytest.mark.parametrize('engine,factory',
                         [(ForwardAnalysisConfig.Engine.SYMPY, SympyPGF),
                          (ForwardAnalysisConfig.Engine.GINAC, ProdigyPGF),
                          (ForwardAnalysisConfig.Engine.SYMENGINE, SymenginePGF)])
def test_parameter(engine, factory):
    prog = compile_pgcl("""
        fun f := {
            nat y;
            y := geometric(p);
            return y;
        }
        nat x;
        rparam p;
        x := f();
    """)
    res, error_prob = compute_discrete_distribution(
        prog, factory.one(), ForwardAnalysisConfig(engine=engine))
    assert res == factory.geometric('x', 'p')
