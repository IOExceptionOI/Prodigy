from prodigy.synthesis.synthesize_pgcl_invariant import synthesize_pgcl_invariant
from prodigy.analysis.equivalence import equivalence_check
from probably.pgcl.compiler import compile_pgcl
from probably.pgcl.check import CheckFail, check_program
import os
from prodigy.util.color import Style
from typing import Tuple, List, Dict, Literal
from prodigy.distribution.distribution import Distribution, State

target_pgcl_program = compile_pgcl(
    """
    nat x;
    nat c;
    nat tmp;

    while(x > 0) {
    { x := x-1 } [1/2] { c := c+1 }
    tmp := 0;
    }
""")

invariant_pgcl_programs = synthesize_pgcl_invariant(target_pgcl_program)

# delete the file if it exists
if os.path.exists("invariant_pgcl_program.txt"):
    os.remove("invariant_pgcl_program.txt")

for invariant_pgcl_program in invariant_pgcl_programs:
    # check whether the invariant can be compiled
    print(f'invariant_pgcl_program:\n{invariant_pgcl_program}')
    print(invariant_pgcl_program.__repr__())
    res = check_program(invariant_pgcl_program)
    if isinstance(res, CheckFail):
        # write to the file
        with open("invariant_pgcl_program.txt", "a") as f:
            f.write("--------------------------------\n")
            f.write("compile failed\n")
            f.write(str(invariant_pgcl_program) + "\n")
            f.write(str(res) + "\n")
            f.write("--------------------------------\n")
    else:
        # write to the file
        with open("invariant_pgcl_program.txt", "a") as f:
            f.write("--------------------------------\n")
            f.write("compile successfully\n")
            f.write(str(invariant_pgcl_program) + "\n")
            f.write("--------------------------------\n")
            
            # check the equivalence of the invariant and the target program
            # equiv, result = equivalence_check(target_pgcl_program, invariant_pgcl_program, ctx.obj['CONFIG'], compute_semantics)
            
            # if equiv is True:
            #     assert isinstance(result, list)
            #     f.write(f"Program{Style.OKGREEN} is equivalent{Style.RESET} to invariant")
            #     if len(result) == 0:
            #         f.write(".\n")
            #     else:
            #         f.write(f" {Style.OKGREEN}under the following constraints:{Style.RESET} {result}.\n")
            # elif equiv is False:
            #     assert isinstance(result, State)
            #     f.write(
            #         f"Program{Style.OKRED} is not equivalent{Style.RESET} to invariant. "
            #         f"{Style.OKRED}Counterexample:{Style.RESET} {result.valuations}\n"
            #     )
            # else:
            #     assert equiv is None
            #     f.write(
            #         f"Program equivalence{Style.OKYELLOW} cannot be determined{Style.RESET}, "
            #         f"but depends on {result}.\n"
            #     )

# delete the file if it exists
# import os
# if os.path.exists("invariant_pgcl_program.txt"):
#     os.remove("invariant_pgcl_program.txt")

# with open("invariant_pgcl_program.txt", "a") as f:

#     for invariant_pgcl_program in invariant_pgcl_programs:
#     # print("--------------------------------")
#     # print(f"invariant_pgcl_program: \n{invariant_pgcl_program}")
#     # print("--------------------------------")
    
#         # append to the file
#         f.write("--------------------------------\n")
#         f.write(str(invariant_pgcl_program) + "\n")
        
