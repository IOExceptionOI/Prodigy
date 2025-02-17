from prodigy.synthesis.synthesize_pgcl_invariant import synthesize_pgcl_invariant


from probably.pgcl.compiler import compile_pgcl


target_pgcl_program = compile_pgcl(
    """
    nat x;
    nat y;
    nparam a;
    
    x := 0;
    y := 0;
    while (x < 10) {
        x := x + 1;
        y := y + x;
    }""")

invariant_pgcl_programs = synthesize_pgcl_invariant(target_pgcl_program)

# delete the file if it exists
import os
if os.path.exists("invariant_pgcl_program.txt"):
    os.remove("invariant_pgcl_program.txt")

with open("invariant_pgcl_program.txt", "a") as f:

    for invariant_pgcl_program in invariant_pgcl_programs:
    # print("--------------------------------")
    # print(f"invariant_pgcl_program: \n{invariant_pgcl_program}")
    # print("--------------------------------")
    
        # append to the file
        f.write("--------------------------------\n")
        f.write(str(invariant_pgcl_program) + "\n")
        
