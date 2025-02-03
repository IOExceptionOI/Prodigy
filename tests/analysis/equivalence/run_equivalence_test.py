from probably.pgcl.ast import Program
from probably.pgcl.compiler import compile_pgcl
from prodigy.analysis.analyzer import compute_semantics
from prodigy.analysis.config import ForwardAnalysisConfig
from prodigy.analysis.equivalence.equivalence_check import check_equivalence
from prodigy.analysis.equivalence.equivalence_check_debug import check_equivalence_with_debug
import logging

logging.basicConfig(level=logging.DEBUG)

def run_basic_equivalence_test(engine):
    """运行基本等价性检查测试"""
    print(f"\n{'='*60}")
    print(f"基本等价性测试 - 使用引擎: {engine}")
    print(f"{'='*60}\n")
    
    # 编译第一个程序
    prog = compile_pgcl("""
        nat x;
        nat c;
        nat temp;

        while (x >= 1){
        {x := 0 } [1/2] {c := c+1}
        temp :=0
        }
    """)
    assert isinstance(prog, Program)

    # 编译第二个程序
    inv = compile_pgcl("""
        nat x;
        nat c;
        nat temp;

        if(x >= 1){
            temp := geometric(1/2)
            c := c + temp
            x := 0
            temp := 0
        } else {skip}
    """)
    assert isinstance(inv, Program)
    
    # 使用新的调试版本
    res, subs = check_equivalence_with_debug(prog, inv, ForwardAnalysisConfig(engine=engine), compute_semantics)
    print(f"测试结果: {'通过' if res else '失败'}")
    print(f"替换: {subs}")
    return res, subs

def run_parameter_equivalence_test(engine):
    """运行带参数的等价性检查测试"""
    print(f"\n使用引擎: {engine}")
    
    # 编译第一个程序
    prog = compile_pgcl("""
        nat x;
        nat c;
        nat temp;
        rparam p;

        while (x >= 1){
        {x := 0 } [1.0-p] {c := c+1}
        temp :=0
        }
    """)
    assert isinstance(prog, Program)

    # 编译第二个程序
    inv = compile_pgcl("""
        nat x;
        nat c;
        nat temp;
        rparam p;

        if(x >= 1){
            temp := geometric(p)
            c := c + temp
            x := 0
            temp := 0
        } else {skip}
    """)
    assert isinstance(inv, Program)
    
    # 执行等价性检查
    res, subs = check_equivalence(prog, inv, ForwardAnalysisConfig(engine=engine), compute_semantics)
    print(f"测试结果: {'通过' if res else '失败'}")
    print(f"替换: {subs}")
    return res, subs

def main():
    """主函数：运行所有测试"""
    engines = [
        ForwardAnalysisConfig.Engine.GINAC,
        #ForwardAnalysisConfig.Engine.SYMPY,
        #ForwardAnalysisConfig.Engine.SYMENGINE
    ]
    
    print("开始运行基本等价性测试...")
    for engine in engines:
        run_basic_equivalence_test(engine)
        
    # print("\n开始运行带参数的等价性测试...")
    # for engine in engines:
    #     run_parameter_equivalence_test(engine)

if __name__ == "__main__":
    main() 