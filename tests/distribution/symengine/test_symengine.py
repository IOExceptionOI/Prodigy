from prodigy.distribution.symengine_distribution import *
import pytest
import symengine as se
import random
from probably.pgcl import NatLitExpr


def create_random_gf(number_of_variables: int = 1, terms: int = 1):
    # This does most likely does not create a PGF!
    symbols = ["x" + str(i) for i in range(number_of_variables)]
    values = [
        se.S(random.randint(0, 100)) for _ in range(len(symbols) * terms)
    ]
    coeffs = [
        se.S(str(random.uniform(0, 1))) for _ in range(terms)
    ]

    result = se.S(0)
    for i in range(terms):
        monomial = se.S(1)
        for var in symbols:
            monomial *= se.S(var) ** values[i]
        result += monomial * coeffs[i]
    return SymengineDist(str(result), *symbols)


class TestDistributionInterface:
    def test_addition(self):
        g = SymengineDist("x", "x").set_parameters('p')
        h = SymengineDist("y", "y")
        gf_prod = g * h
        assert gf_prod.get_parameters() == {'p'}
        assert gf_prod == SymengineDist("x * y", "x", "y").set_parameters("p")

    def test_product(self):
        g = SymengineDist("x", "x").set_parameters('p')
        h = SymengineDist("y", "y")
        gf_sum = g + h
        assert gf_sum.get_parameters() == {'p'}
        assert gf_sum == SymengineDist("x + y", "x", "y").set_parameters("p")

    def test_conflict_parameter_variable(self):
        g = SymengineDist("x", "x")
        h = SymengineDist("y", "y").set_parameters("x")
        with pytest.raises(SyntaxError):
            g + h

    def test_finite_sleq(self):
        gf1 = SymengineDist("x**2*y**3")
        gf2 = SymengineDist("1/2*x**2*y**3")
        assert gf2 <= gf1

    def test_infinite_leq(self):
        gf1 = SymengineDist("(1-sqrt(1-x**2))/x")
        gf2 = SymengineDist("2/(2-x)-1")
        with pytest.raises(RuntimeError):
            assert gf1 <= gf2

    def test_finite_le(self):
        gf1 = SymengineDist("x**2*y**3")
        gf2 = SymengineDist("1/2*x**2*y**3")
        assert gf2 < gf1

        gf1 = SymengineDist("(1/2) * x**2*y**3 + (1/2) * x**3*y**2")
        gf2 = SymengineDist("(1/3) * x**2*y**3 + (2/3) * x**3*y**2")
        # FIXME sometimes the pygin.get_terms method returns different order leading to different results
        assert not gf1 < gf2

    def test_infinite_le(self):
        gf1 = SymengineDist("(1-sqrt(1-x**2))/x")
        gf2 = SymengineDist("2/(2-x) - 1")
        with pytest.raises(RuntimeError):
            assert gf1 < gf2

    def test_equality_param_fail(self):
        gf1 = SymengineDist("y*x", "x")
        gf2 = SymengineDist("x*y", "y", "x")
        assert gf1 != gf2

    def test_equality_variable_fail(self):
        gf1 = SymengineDist("y*x", "x")
        gf2 = SymengineDist("x*y", "y")
        assert gf1 != gf2

    def test_variable_parameter_clash(self):
        gf = SymengineDist("y*x")
        with pytest.raises(ValueError) as e:
            gf.set_variables("x")
            assert "There are unknown symbols which are neither variables nor parameters" in str(e)

        with pytest.raises(ValueError) as e:
            gf.set_parameters("x")
            assert "At least one parameter is already known as a variable" in str(e)

    def test_iteration(self):
        gf = SymengineDist("(1-sqrt(1-x**2))/x")
        expected_terms = [
            ("1/2", State({"x": 1})),
            ("1/8", State({"x": 3})),
            ("1/16", State({"x": 5})),
            ("5/128", State({"x": 7})),
            ("7/256", State({"x": 9})),
            ("21/1024", State({"x": 11})),
            ("33/2048", State({"x": 13})),
            ("429/32768", State({"x": 15})),
            ("715/65536", State({"x": 17})),
            ("2431/262144", State({"x": 19}))
        ]
        i = 0
        for prob, state in gf:
            if i >= 4:
                break
            if prob == "0":
                continue
            else:
                assert (prob, state) == expected_terms[i]
                i += 1

    def test_iter_with(self):
        pass # TODO

    def test_get_prob_by_diff(self):
        gf = SymenginePGF.geometric("x", "1/2")
        for i in range(10):
            assert gf.get_prob_by_diff(State({"x": i})) == se.S(f"(1/2)**({i}+1)")

    def test_get_prob_by_series(self):
        gf = SymenginePGF.geometric("x", "1/2")
        for i in range(10):
            assert gf.get_prob_by_series(State({"x": i})) == se.S(f"(1/2)**({i}+1)")

    def test_copy(self):
        gf = create_random_gf(3, 5)
        assert gf.copy() == gf

    def test_get_probability_of(self):
        gf = SymengineDist("(1-sqrt(1-x**2))/x")
        assert gf.get_probability_of(parse_expr("x <= 3")) == "5/8"

        gf = SymenginePGF.undefined("z", "y")
        assert gf.get_probability_of(parse_expr("not (z*y < 12)")) == "0"

    def test_get_probability_mass(self):
        gf = SymengineDist("(1-sqrt(1-x**2))/x")
        assert gf.get_probability_mass() == "1"

        gf = SymenginePGF.undefined("x")
        assert gf.get_probability_mass() == "0"

        gf = SymenginePGF.uniform("x", "3", "10")
        assert gf.get_probability_mass() == "1"

    def test_expected_value_of(self):
        gf = SymengineDist("(1-sqrt(1-x**2))/x")
        assert gf.get_expected_value_of("x") == "Infinity"

        gf = SymenginePGF.undefined("x")
        assert gf.get_expected_value_of("x") == "0"

        gf = SymenginePGF.uniform("x", "3", "10")
        with pytest.raises(Exception) as e:
            gf.get_expected_value_of("x**2+y")
        assert "Cannot compute expected value" in str(e)

        gf = SymengineDist("(1-p) + p*x", 'x')
        assert gf.get_expected_value_of('x') == "p"
        assert gf.get_expected_value_of('p*x') == "p**2"

        gf = SymenginePGF.poisson("x", "p")
        assert gf.get_expected_value_of("x") == "p"
        assert se.S(gf.get_expected_value_of("p*x")) == se.S("p^2")
        assert gf.get_expected_value_of("p") == "p"

        gf = SymengineDist("n^5")
        # Linearity breaks if intermediate results are negative.
        with pytest.raises(ValueError):
            gf.get_expected_value_of("n - 7 + 1")
        pytest.xfail(
            'this is simplified to "n" by se, meaning we cannot detect that the intermediate results are negative'
        )
        with pytest.raises(ValueError):
            gf.get_expected_value_of("n - 7 + 7")

    def test_normalize(self):
        assert create_random_gf().normalize().coefficient_sum() == 1

    def test_get_variables(self):
        variable_count = random.randint(1, 10)
        gf = create_random_gf(variable_count, 5)
        assert len(gf.get_variables()) == variable_count, \
            f"Amount of variables does not match. Should be {variable_count}, is {len(gf.get_variables())}."

        assert all(map(lambda x: x in ["x" + str(i) for i in range(variable_count)], gf.get_variables())), \
            f"The variables do not coincide with the actual names." \
            f"Should be {['x' + str(i) for i in range(variable_count)]}, is {gf.get_variables()}."

        gf = SymengineDist("a*x + (1-a)", "x")
        assert len(gf.get_variables()) == 1
        assert gf.get_variables() == {"x"}

    def test_get_parameters(self):
        variable_count = random.randint(1, 10)
        gf = create_random_gf(variable_count, 5)
        gf *= SymengineDist("p", "")
        assert len(gf.get_parameters()) == 1, \
            f"Amount of parameters does not match. Should be {1}, is {len(gf.get_parameters())}."

        assert all(map(lambda x: x in {"p"}, gf.get_parameters())), \
            f"The parameters do not coincide with the actual names." \
            f"Should be {{'a', 'b'}}, is {gf.get_parameters()}."

    def test_filter(self):
        gf = SymenginePGF.undefined("x", "y")
        assert gf.filter(parse_expr("x*3 < 25*y")) == gf

        # check filter on infinite GF
        gf = SymengineDist("(1-sqrt(1-c**2))/c")
        assert gf.filter(parse_expr("c <= 5")) == SymengineDist(
            "c/2 + c**3/8 + c**5/16")

        # check filter on finite GF
        gf = SymengineDist("1/2*x*c + 1/4 * x**2 + 1/4")
        assert gf.filter(parse_expr("x*c < 123")) == gf

        gf = SymengineDist("(1-sqrt(1-c**2))/c", "c", "x", "z")
        assert gf.filter(parse_expr("x*z <= 10")) == gf

        gf = SymengineDist("(c/2 + c^3/2) * (1-sqrt(1-x**2))/x")
        assert gf.filter(parse_expr("c*c <= 5")) == SymengineDist(
            "c/2 * (1-sqrt(1-x**2))/x")

    def test_is_zero_dist(self):
        gf = create_random_gf(4, 10)
        # Sometimes Symengine is not sure whether it's a zero dist
        assert (gf == SymenginePGF.undefined(*gf.get_variables())) == gf.is_zero_dist() or gf.is_zero_dist() is None

        gf = SymenginePGF.undefined("x")
        assert (gf == SymenginePGF.undefined(*gf.get_variables())) == gf.is_zero_dist()

        gf = SymenginePGF.from_expr("x - x", "x")
        assert (gf == SymenginePGF.undefined(*gf.get_variables())) == gf.is_zero_dist()

        gf = SymenginePGF.one("")
        assert not gf.is_zero_dist()

    def test_is_finite(self):
        gf = create_random_gf(10, 10)
        assert gf.is_finite()

        gf = SymengineDist("(1-sqrt(1-c**2))/c")
        assert not gf.is_finite()

        gf = SymenginePGF.one("")
        assert gf.is_finite()

        gf = SymengineDist("(1/6)*(-1 + x_1**6)/(-1 + x_1)")
        assert gf.is_finite()

    def test_get_fresh_variables(self):
        gf = SymengineDist("x_0 * x_1")
        assert "x_2" == gf.get_fresh_variable()
        assert "x_3" == gf.get_fresh_variable(exclude={"x_2"})

    def test_update_sum(self):
        gf = SymengineDist("x")
        assert gf._update_sum("x", 1, 1) == SymengineDist("x ** 2")

        # TODO continue with other branches

    def test_update_var(self):
        # Parameter assignment is not allowed
        gf = SymengineDist("x").set_parameters("y")
        with pytest.raises(ValueError) as e:
            gf._update_var("x", "y")
            assert "Assignment to parameters is not allowed" in str(e)

        # Variables should all be known
        gf = SymengineDist("x")
        with pytest.raises(ValueError) as e:
            gf._update_var("x", "y")
            assert "Unknown symbol: y" in str(e)

        # _update_var with assign_var is integer
        gf = SymengineDist("x")
        assert gf._update_var("x", 5) == SymengineDist("x ** 5")

        # _update_var with updated_var == assign_var
        assert gf._update_var("x", "x") == gf

        # _update_var with updated_var != assign_var, assign_var is symbol
        gf = SymengineDist("x * y")
        assert gf._update_var("x", "y") == SymengineDist("x*y")

    # TODO add tests for other _update_<> methods

    def test_safe_subs(self):
        gf = SymengineDist("x*y")

        # Illegal number of arguments
        with pytest.raises(ValueError) as e:
            gf.safe_subs("x", 1, "y")
            assert "There has to be an equal amount of variables and values" in str(e)

        # safe_subs should behave exactly the same as subs
        assert (gf.safe_subs("x", 1, "y", "x") == gf.safe_subs(("x", 1), ("y", "x"))
                == gf._s_func.subs("x", 1).subs("y", "x"))

        # Direct substitution leads to nan, safe_subs should not
        gf = SymengineDist("(1/11)*(1/2 + (1/2)*y)**10*(-1 + x**11)/(-1 + x)")
        assert gf._s_func.subs("x", 1).simplify() == se.nan
        assert gf.safe_subs("x", 1) == se.S("(1/1024)*(1 + y)**10")
        # TODO add test for limit

    def test_update(self):
        gf = SymengineDist("(1-sqrt(1-c**2))/c")
        # c -> c + 1
        updated_gf = gf.update(BinopExpr(Binop.EQ, VarExpr('c'), BinopExpr(Binop.PLUS, VarExpr('c'), NatLitExpr(1))))
        assert updated_gf == SymengineDist("c*(1-sqrt(1-c**2))/c")

        gf = SymenginePGF.undefined("x")
        expr = BinopExpr(
            Binop.EQ, VarExpr('x'),
            BinopExpr(Binop.PLUS,
                      BinopExpr(Binop.TIMES, VarExpr('x'), NatLitExpr(5)),
                      NatLitExpr(1)))
        assert gf.update(expr) == SymenginePGF.undefined("x")

        gf = SymenginePGF.uniform("x", "0", "5")
        expr = BinopExpr(Binop.EQ, VarExpr('x'),
                         BinopExpr(Binop.TIMES, VarExpr('x'), VarExpr('x')))
        updated_gf = gf.update(expr)
        # TODO how to check for equality with symengine?
        #   cf. https://github.com/symengine/symengine.py/issues/496
        assert sp.S(updated_gf._s_func).equals(sp.S("1/6 * (1 + x + x**4 + x**9 + x**16 + x**25)"))

    def test_marginal(self):
        gf = SymenginePGF.uniform("x", '0', '10') * SymenginePGF.binomial(
            'y', n='10', p='1/2')
        assert gf.marginal('x') == SymenginePGF.uniform("x", '0', '10')
        # TODO how to check for equality with symengine?
        #   cf. https://github.com/symengine/symengine.py/issues/496
        assert sp.S(gf.marginal(
            'x', method=MarginalType.EXCLUDE)._s_func).equals(sp.S(SymenginePGF.binomial('y', n='10', p='1/2')._s_func))
        assert sp.S(gf.marginal('x', 'y')._s_func).equals(sp.S(gf._s_func))

        gf = SymengineDist("(1-sqrt(1-c**2))/c")
        with pytest.raises(ValueError) as e:
            gf.marginal('x', method=MarginalType.INCLUDE)
            assert "Unknown variable(s):" in str(e)

        with pytest.raises(ValueError) as e:
            gf.marginal()
            assert "No variables where provided" in str(e)

    def test_set_variables(self):
        gf = create_random_gf(3, 5)

        gf = gf.set_variables("a", "b", "c", *gf.get_variables())
        assert all([x in gf.get_variables() for x in {'a', 'b', 'c'}])

    def test_approximate(self):
        gf = SymengineDist("2/(2-x) - 1")
        assert list(gf.approximate("0.99"))[-1] == SymengineDist(
            "1/2*x + 1/4*x**2 + 1/8 * x**3 + 1/16 * x**4"
            "+ 1/32 * x**5 + 1/64 * x**6 + 1/128 * x**7")

        gf = SymenginePGF.undefined("x", 'y')
        for dist in gf.approximate(10):
            assert dist.is_zero_dist()
