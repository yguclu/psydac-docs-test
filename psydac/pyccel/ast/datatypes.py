# coding: utf-8

from .singleton import Singleton
from .basic import Basic

from sympy.core.compatibility import with_metaclass

import numpy

# TODO [YG, 12.03.2020] verify why we need all these types
# NOTE: symbols not used in pyccel are commented out
__all__ = (
#
# --------- CLASSES -----------
#
    'CustomDataType',
    'DataType',
    'FunctionType',
    'NativeBool',
    'NativeComplex',
    'NativeGeneric',
    'NativeInteger',
    'NativeTuple',
#    'NativeNil',
#    'NativeParallelRange',
    'NativeRange',
    'NativeReal',
    'NativeString',
    'NativeSymbol',
    'NativeTensor',
    'NativeVoid',
    'UnionType',
    'VariableType',
    'DataTypeFactory',
#
# --------- FUNCTIONS -----------
#
    'datatype',
#    'get_default_value',
    'is_iterable_datatype',
    'is_pyccel_datatype',
    'is_with_construct_datatype',
#
# --------- VARIABLES -----------
#
    'Bool',
    'Cmplx',
    'Generic',
    'Int',
    'Nil',
    'Real',
    'String',
    'Void',
#    '_Symbol',
    'default_precision',
    'dtype_and_precision_registry',
    'dtype_registry'
)

#==============================================================================

default_precision = {'real': 8, 'int': numpy.dtype(int).alignment, 'integer': numpy.dtype(int).alignment, 'complex': 8, 'bool':4, 'float':8}
dtype_and_precision_registry = { 'real':('real',default_precision['float']),
                                 'double':('real',default_precision['float']),
                                 'float':('real',default_precision['float']),       # sympy.Float
                                 'pythonfloat':('real',default_precision['float']), # built-in float
                                 'float32':('real',4),
                                 'float64':('real',8),
                                 'pythoncomplex':('complex',default_precision['complex']),
                                 'complex':('complex',default_precision['complex']),  # to create numpy array with dtype='complex'
                                 'complex64':('complex',4),
                                 'complex128':('complex',8),
                                 'int8' :('int',1),
                                 'int16':('int',2),
                                 'int32':('int',4),
                                 'int64':('int',8),
                                 'int'  :('int', default_precision['int']),
                                 'int_'  :('int', default_precision['int']), # numba only accepts int_ as datatype instead of int
                                 'pythonint'  :('int', default_precision['int']),
                                 'integer':('int',default_precision['int']),
                                 'bool' :('bool',default_precision['bool']),
                                 'bool_' :('bool',default_precision['bool']), # numba only accepts bool_ as datatype instead of bool
                                 'pythonbool' :('bool',default_precision['bool'])}


class DataType(metaclass=Singleton):
    """Base class representing native datatypes"""
    _name = '__UNDEFINED__'

    @property
    def name(self):
        return self._name

    def __str__(self):
        return str(self.name).lower()

class NativeBool(DataType):
    _name = 'Bool_'

class NativeInteger(DataType):
    _name = 'Int64'

class NativeReal(DataType):
    _name = 'Float64'

class NativeComplex(DataType):
    _name = 'Complex'

class NativeString(DataType):
    _name = 'String'

class NativeVoid(DataType):
    _name = 'Void'

class NativeNil(DataType):
    _name = 'Nil'

class NativeTuple(DataType):
    """Base class representing native datatypes"""
    _name = 'Tuple'

class NativeRange(DataType):
    _name = 'Range'

class NativeTensor(DataType):
    _name = 'Tensor'

class NativeParallelRange(NativeRange):
    _name = 'ParallelRange'

class NativeSymbol(DataType):
    _name = 'Symbol'


# TODO to be removed
class CustomDataType(DataType):
    _name = '__UNDEFINED__'

    def __init__(self, name='__UNDEFINED__'):
        self._name = name

class NativeGeneric(DataType):
    _name = 'Generic'
    pass


# ...
class VariableType(DataType):

    def __init__(self, rhs, alias):
        self._alias = alias
        self._rhs = rhs
        self._name = rhs._name

    @property
    def alias(self):
        return self._alias

class FunctionType(DataType):

    def __init__(self, domains):
        self._domain = domains[0]
        self._codomain = domains[1:]
        self._domains = domains
        self._name = ' -> '.join('{}'.format(V) for V in self._domains)

    @property
    def domain(self):
        return self._domain

    @property
    def codomain(self):
        return self._codomain
# ...



Bool           = NativeBool()
Int            = NativeInteger()
Real           = NativeReal()
Cmplx          = NativeComplex()
Void           = NativeVoid()
Nil            = NativeNil()
String         = NativeString()
_Symbol        = NativeSymbol()
Generic        = NativeGeneric()

dtype_registry = {'bool': Bool,
                  'bool_': Bool,
                  'int': Int,
                  'int_': Int,
                  'integer': Int,
                  'real'   : Real,
                  'complex': Cmplx,
                  'void': Void,
                  'nil': Nil,
                  'symbol': _Symbol,
                  '*': Generic,
                  'str': String}


class UnionType(Basic):

    def __new__(cls, args):
        return Basic.__new__(cls, args)

    @property
    def args(self):
        return self._args[0]


def DataTypeFactory(name, argnames=("_name"),
                    BaseClass=CustomDataType,
                    prefix=None,
                    alias=None,
                    is_iterable=False,
                    is_with_construct=False,
                    is_polymorphic=True):
    def __init__(self, **kwargs):
        for key, value in list(kwargs.items()):
            # here, the argnames variable is the one passed to the
            # DataTypeFactory call
            if key not in argnames:
                raise TypeError("Argument %s not valid for %s"
                    % (key, self.__class__.__name__))
            setattr(self, key, value)
        BaseClass.__init__(self, name=name[:-len("Class")])

    if prefix is None:
        prefix = 'Pyccel'
    else:
        prefix = 'Pyccel{0}'.format(prefix)

    newclass = type(prefix + name, (BaseClass,),
                    {"__init__":          __init__,
                     "_name":             name,
                     "prefix":            prefix,
                     "alias":             alias,
                     "is_iterable":       is_iterable,
                     "is_with_construct": is_with_construct,
                     "is_polymorphic":    is_polymorphic})
    return newclass

def is_pyccel_datatype(expr):
    return isinstance(expr, CustomDataType)

def is_iterable_datatype(dtype):
    """Returns True if dtype is an iterable class."""
    if is_pyccel_datatype(dtype):
        return dtype.is_iterable
    elif isinstance(dtype, (NativeRange, NativeTensor)):
        return True
    else:
        return False


def get_default_value(dtype):
    """Returns the default value of a native datatype."""
    if isinstance(dtype, NativeInteger):
        value = 0
    elif isinstance(dtype, NativeReal):
        value = 0.0
    elif isinstance(dtype, NativeComplex):
        value = 0.0
    elif isinstance(dtype, NativeBool):
        value = BooleanFalse()
    else:
        raise TypeError('Unknown type')
    return value


# TODO improve
def is_with_construct_datatype(dtype):
    """Returns True if dtype is an with_construct class."""
    if is_pyccel_datatype(dtype):
        return dtype.is_with_construct
    else:
        return False

# TODO check the use of Reals
def datatype(arg):
    """Returns the datatype singleton for the given dtype.

    arg : str or sympy expression
        If a str ('bool', 'int', 'real','complex', or 'void'), return the
        singleton for the corresponding dtype. If a sympy expression, return
        the datatype that best fits the expression. This is determined from the
        assumption system. For more control, use the `DataType` class directly.

    Returns:
        DataType

    """


    if isinstance(arg, str):
        if arg.lower() not in dtype_registry:
            raise ValueError("Unrecognized datatype " + arg)
        return dtype_registry[arg]
    if isinstance(arg, DataType):
        return dtype_registry[arg.name.lower()]
    else:
        raise TypeError('Expecting a DataType')


