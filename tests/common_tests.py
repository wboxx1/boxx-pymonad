# --------------------------------------------------------
# (c) Copyright 2014, 2020 by Jason DeLaat.
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------
import pymonad.tools
import pymonad.operators.reader

id = pymonad.tools.identity
curry = pymonad.tools.curry
k_compose = pymonad.tools.kleisli_compose


@curry(2)
def add(x, y):
    return x + y


@curry(2)
def mul(x, y):
    return x * y


@curry(2)
def sub(x, y):
    return x - y


@curry(2)
def k_inc(cls, x):
    return cls.insert(x + 1)


@curry(2)
def k_dec(cls, x):
    return cls.insert(x - 1)


@curry(2)
def k_dbl(cls, x):
    return cls.insert(2 * x)


class ApplicativeTests:
    def setUp(self):
        raise NotImplementedError(
            "ApplicativeTests: You need to set self._class to the monad class being tested."
        )

    def test_application_is_homomorphic(self):
        f = add(1)
        self.assertEqual(
            self._class.insert(f(2)),
            self._class.apply(f).to_arguments(self._class.insert(2)),
        )

    def test_application_is_same_as_mapping(self):
        f = add(1)
        self.assertEqual(
            self._class.apply(f).to_arguments(self._class.insert(2)),
            self._class.insert(2).map(f),
        )

    def test_application_is_associative(self):
        self.assertEqual(
            self._class.apply(add).to_arguments(
                self._class.insert(1), self._class.insert(2)
            ),
            self._class.apply(lambda args: add(*args)).to_arguments(
                self._class.apply(lambda b: (1, b)).to_arguments(self._class.insert(2))
            ),
        )


class MonadTests:
    def setUp(self):
        raise NotImplementedError(
            "MonadTests: You need to set self._class to the monad class being tested."
        )

    def test_left_identity(self):
        inc = k_inc(self._class)
        self.assertEqual(k_compose(self._class.insert, inc)(0), inc(0))

    def test_right_identity(self):
        inc = k_inc(self._class)
        self.assertEqual(k_compose(inc, self._class.insert)(0), inc(0))

    def test_associativity(self):
        inc = k_inc(self._class)
        dec = k_dec(self._class)
        dbl = k_dbl(self._class)
        self.assertEqual(
            k_compose(k_compose(inc, dec), dbl)(0),
            k_compose(inc, k_compose(dec, dbl))(0),
        )


class FunctorTests:
    def setUp(self):
        raise NotImplementedError(
            "FunctorTests: You need to set self._class to the monad class being tested."
        )

    def test_left_identity(self):
        self.assertEqual(self._class.insert(id(1)), self._class.insert(1))

    def test_rightidentity(self):
        self.assertEqual(id(self._class.insert(1)), self._class.insert(1))

    def test_apply_then_insert(self):
        self.assertEqual(
            self._class.insert(1).map(add(1)), self._class.insert(add(1, 1))
        )

    def test_composition(self):
        self.assertEqual(
            self._class.insert(1).map(lambda x: sub(2, add(1, x))),
            self._class.insert(1).map(add(1)).map(sub(2)),
        )


class ThenTests:
    def setUp(self):
        raise NotImplementedError(
            "FunctorTests: You need to set self._class to the monad class being tested."
        )

    def test_then_with_normal_function(self):
        self.assertEqual(self._class.insert(0).then(add(1)), self._class.insert(1))

    def test_then_with_kleisli_function(self):
        self.assertEqual(
            self._class.insert(0).then(k_inc(self._class)), k_inc(self._class, 0)
        )


class FunctorOperatorTests:
    def setUp(self):
        raise NotImplementedError(
            "FunctorTests: You need to set self._class to the monad class being tested."
        )

    def test_left_identity(self):
        self.assertEqual(self._class.insert(id(1)), self._class.insert(1))

    def test_rightidentity(self):
        self.assertEqual(id(self._class.insert(1)), self._class.insert(1))

    def test_apply_then_insert(self):
        self.assertEqual(add(1) << self._class.insert(1), self._class.insert(add(1, 1)))

    def test_composition(self):
        # To compose functions with operators we need to explicitly
        # wrap them in the pymonad.operators.reader.Reader
        # constructor. Here we do that directly, in actual code using
        # @Reader as a decorator would be cleaner.
        self.assertEqual(
            sub(2) << (add(1) << self._class.insert(1)),
            sub(2) << pymonad.operators.reader.Reader(add(1)) << self._class.insert(1),
        )


class ApplicativeOperatorTests:
    def setUp(self):
        raise NotImplementedError(
            "ApplicativeTests: You need to set self._class to the monad class being tested."
        )

    def test_application_is_homomorphic(self):
        f = add(1)
        self.assertEqual(
            self._class.insert(f(2)), self._class.insert(f) & self._class.insert(2)
        )

    def test_application_is_same_as_mapping(self):
        f = add(1)
        self.assertEqual(
            self._class.apply(f).to_arguments(self._class.insert(2)),
            f << self._class.insert(2),
        )

    def test_application_is_associative(self):
        self.assertEqual(
            add << self._class.insert(1) & self._class.insert(2),
            self._class.insert(lambda args: add(*args))
            & (self._class.insert(lambda b: (1, b)) & self._class.insert(2)),
        )


class MonadOperatorTests:
    def setUp(self):
        raise NotImplementedError(
            "MonadTests: You need to set self._class to the monad class being tested."
        )

    def test_left_identity(self):
        inc = k_inc(self._class)
        self.assertEqual(self._class.insert(0) >> inc, inc(0))

    def test_right_identity(self):
        inc = k_inc(self._class)
        self.assertEqual(inc(0) >> self._class.insert, inc(0))

    def test_associativity(self):
        inc = k_inc(self._class)
        dec = k_dec(self._class)
        dbl = k_dbl(self._class)
        self.assertEqual((inc(0) >> dec) >> dbl, inc(0) >> (lambda x: dec(x) >> dbl))

