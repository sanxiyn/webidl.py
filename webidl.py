# Web IDL parser

# Lexer

import ply.lex as lex

tokens = [
    'ellipsis',
    'array',
    'hexinteger',
    'decimalinteger',
    'string',
    'identifier',
]

literals = '(),:;<=>?[]{}'

def t_newline(t):
    r'\n'
    t.lexer.lineno += 1

t_ignore = r' '
t_ignore_line_comment = r'//.*'
t_ignore_block_comment = r'/\*.*?\*/'

def t_error(t):
    print "Illegal character '%s'" % (t.value[0],)
    t.lexer.skip(1)

t_ellipsis = r'\.\.\.'
t_array = r'\[\]'

def t_hexinteger(t):
    r'0[xX][0-9a-fA-F]+'
    t.value = int(t.value, 16)
    return t

def t_decimalinteger(t):
    r'[1-9][0-9]*|0'
    t.value = int(t.value)
    return t

def t_string(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t

reserved = {
    'DOMString',
    'any',
    'attribute',
    'boolean',
    'const',
    'creator',
    'deleter',
    'dictionary',
    'double',
    'exception',
    'float',
    'getraises',
    'getter',
    'implements',
    'in',
    'interface',
    'long',
    'optional',
    'partial',
    'raises',
    'readonly',
    'sequence',
    'setter',
    'short',
    'static',
    'stringifier',
    'typedef',
    'unsigned',
    'void',
}

tokens.extend(sorted(reserved))

def t_identifier(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = t.value
    return t

# Parser

import ply.yacc as yacc

def p_Definitions(p):
    'Definitions : ExtendedAttributeList Definition Definitions'
    p[0] = [p[2]] + p[3]

def p_Definitions_empty(p):
    'Definitions :'
    p[0] = []

def p_Definition(p):
    '''
    Definition : Interface
               | PartialInterface
               | Dictionary
               | Exception
               | Typedef
               | ImplementsStatement
    '''
    p[0] = p[1]

def p_Interface(p):
    'Interface : interface identifier Inheritance "{" InterfaceMembers "}" ";"'
    p[0] = ['interface', p[2], p[5]]

def p_PartialInterface(p):
    'PartialInterface : partial interface identifier "{" InterfaceMembers "}" ";"'
    p[0] = ['partial interface', p[3], p[5]]

def p_Inheritance(p):
    'Inheritance : ":" ScopedName'
    p[0] = p[2]

def p_Inheritance_empty(p):
    'Inheritance :'
    p[0] = None

def p_InterfaceMembers(p):
    'InterfaceMembers : ExtendedAttributeList InterfaceMember InterfaceMembers'
    p[0] = [p[2]] + p[3]

def p_InterfaceMembers_empty(p):
    'InterfaceMembers :'
    p[0] = []

def p_InterfaceMember(p):
    '''
    InterfaceMember : Const
                    | AttributeOrOperation
    '''
    p[0] = p[1]

def p_Dictionary(p):
    'Dictionary : dictionary identifier Inheritance "{" DictionaryMembers "}" ";"'
    p[0] = ['dictionary', p[2], p[5]]

def p_DictionaryMembers(p):
    'DictionaryMembers : ExtendedAttributeList DictionaryMember DictionaryMembers'
    p[0] = [p[2]] + p[3]

def p_DictionaryMembers_empty(p):
    'DictionaryMembers :'
    p[0] = []

def p_DictionaryMember(p):
    'DictionaryMember : Type identifier DefaultValue ";"'
    p[0] = ['attribute', p[2]]

def p_DefaultValue(p):
    'DefaultValue : "=" ConstValue'
    p[0] = p[2]

def p_DefaultValue_empty(p):
    'DefaultValue :'
    p[0] = None

def p_Exception(p):
    'Exception : exception identifier Inheritance "{" ExceptionMembers "}" ";"'
    p[0] = ['exception', p[2], p[5]]

def p_ExceptionMembers(p):
    'ExceptionMembers : ExtendedAttributeList ExceptionMember ExceptionMembers'
    p[0] = [p[2]] + p[3]

def p_ExceptionMembers_empty(p):
    'ExceptionMembers :'
    p[0] = []

def p_Typedef(p):
    'Typedef : typedef Type identifier ";"'
    p[0] = ['typedef', p[3], p[2]]

def p_ImplementsStatement(p):
    'ImplementsStatement : ScopedName implements ScopedName ";"'
    p[0] = ['implements', p[1], p[3]]

def p_Const(p):
    'Const : const ConstType identifier "=" ConstValue ";"'
    p[0] = ['const', p[3]]

def p_ConstValue(p):
    '''
    ConstValue : integer
               | string
    '''
    p[0] = p[1]

def p_AttributeOrOperation_stringifier(p):
    'AttributeOrOperation : stringifier StringifierAttributeOrOperation'
    p[0] = p[2]

def p_AttributeOrOperation(p):
    '''
    AttributeOrOperation : Attribute
                         | Operation
    '''
    p[0] = p[1]

def p_StringifierAttributeOrOperation(p):
    'StringifierAttributeOrOperation : Attribute'
    p[0] = p[1]

def p_Attribute(p):
    'Attribute : ReadOnly attribute AttributeType identifier Get ";"'
    p[0] = ['attribute', p[4]]

def p_ReadOnly(p):
    'ReadOnly : readonly'
    p[0] = True

def p_ReadOnly_empty(p):
    'ReadOnly :'
    p[0] = False

# From 20110712 draft
def p_Get(p):
    '''
    Get : GetRaises
        |
    '''

# From 20110712 draft
def p_GetRaises(p):
    'GetRaises : getraises ExceptionList'
    p[0] = p[2]

def p_Operation(p):
    'Operation : Qualifiers OperationRest'
    p[0] = ['method'] + p[2]

def p_Qualifiers(p):
    '''
    Qualifiers : static
               | Specials
    '''
    p[0] = p[1]

def p_Specials(p):
    'Specials : Special Specials'
    p[0] = [p[1]] + p[2]

def p_Specials_empty(p):
    'Specials :'
    p[0] = []

def p_Special(p):
    '''
    Special : getter
            | setter
            | creator
            | deleter
    '''
    p[0] = p[1]

def p_OperationRest(p):
    'OperationRest : ReturnType OptionalIdentifier "(" ArgumentList ")" Raises ";"'
    p[0] = [p[2]]

def p_OptionalIdentifier(p):
    'OptionalIdentifier : identifier'
    p[0] = p[1]

def p_OptionalIdentifier_empty(p):
    'OptionalIdentifier :'
    p[0] = None

# From 20110712 draft
def p_Raises(p):
    'Raises : raises ExceptionList'
    p[0] = p[2]

# From 20110712 draft
def p_Raises_empty(p):
    'Raises :'
    p[0] = []

# From 20110712 draft
def p_ExceptionList(p):
    'ExceptionList : "(" ScopedNameList ")"'
    p[0] = p[2]

def p_ArgumentList(p):
    'ArgumentList : Argument Arguments'
    p[0] = [p[1]] + p[2]

def p_ArgumentList_empty(p):
    'ArgumentList :'
    p[0] = []

def p_Arguments(p):
    'Arguments : "," Argument Arguments'
    p[0] = [p[2]] + p[3]

def p_Arguments_empty(p):
    'Arguments :'
    p[0] = []

def p_Argument(p):
    'Argument : ExtendedAttributeList In Optional Type Ellipsis identifier'
    p[0] = p[6]

# From 20110712 draft
def p_In(p):
    'In : in'
    p[0] = True

# From 20110712 draft
def p_In_empty(p):
    'In :'
    p[0] = False

def p_Optional(p):
    'Optional : optional'
    p[0] = True

def p_Optional_empty(p):
    'Optional :'
    p[0] = False

def p_Ellipsis(p):
    'Ellipsis : ellipsis'
    p[0] = True

def p_Ellipsis_empty(p):
    'Ellipsis :'
    p[0] = False

def p_ExceptionMember(p):
    '''
    ExceptionMember : Const
                    | ExceptionField
    '''
    p[0] = p[1]

def p_ExceptionField(p):
    'ExceptionField : AttributeType identifier ";"'
    p[0] = ['attribute', p[2]]

def p_ExtendedAttributeList(p):
    'ExtendedAttributeList : "[" ExtendedAttribute ExtendedAttributes "]"'
    p[0] = [p[2]] + p[3]

def p_ExtendedAttributeList_empty(p):
    'ExtendedAttributeList :'
    p[0] = []

def p_ExtendedAttributes(p):
    'ExtendedAttributes : "," ExtendedAttribute ExtendedAttributes'
    p[0] = [p[2]] + p[3]

def p_ExtendedAttributes_empty(p):
    'ExtendedAttributes :'
    p[0] = []

def p_ExtendedAttribute(p):
    '''
    ExtendedAttribute : "(" ExtendedAttributeInner ")" ExtendedAttributeRest
                      | Other ExtendedAttributeRest
    '''

def p_ExtendedAttributeRest(p):
    '''
    ExtendedAttributeRest : ExtendedAttribute
                          |
    '''

def p_ExtendedAttributeInner(p):
    '''
    ExtendedAttributeInner : "(" ExtendedAttributeInner ")" ExtendedAttributeInner
                           | OtherOrComma ExtendedAttributeInner
                           |
    '''

def p_Other(p):
    '''
    Other : identifier
          | array
          | "="
          | DOMString
          | in
          | optional
    '''

def p_OhterOrComma(p):
    '''
    OtherOrComma : Other
                 | ","
    '''

def p_Type(p):
    '''
    Type : AttributeType
         | SequenceType
    '''
    p[0] = p[1]

def p_SequenceType(p):
    'SequenceType : sequence "<" Type ">" Null'
    p[0] = 'sequence<' + p[3] + '>' + p[5]

def p_AttributeType(p):
    '''
    AttributeType : PrimitiveOrStringType TypeSuffix
                  | ScopedName TypeSuffix
                  | any TypeSuffixStartingWithArray
    '''
    p[0] = p[1] + p[2]

def p_ConstType(p):
    'ConstType : PrimitiveOrStringType Null'
    p[0] = p[1]

def p_PrimitiveOrStringType(p):
    '''
    PrimitiveOrStringType : UnsignedIntegerType
                          | boolean
                          | float
                          | double
                          | DOMString
    '''
    p[0] = p[1]

def p_UnsignedIntegerType_unsigned(p):
    'UnsignedIntegerType : unsigned IntegerType'
    p[0] = 'unsigned ' + p[2]

def p_UnsignedIntegerType(p):
    'UnsignedIntegerType : IntegerType'
    p[0] = p[1]

def p_IntegerType_short(p):
    'IntegerType : short'
    p[0] = p[1]

def p_IntegerType_long(p):
    'IntegerType : long OptionalLong'
    p[0] = p[1] + p[2]

def p_OptionalLong(p):
    'OptionalLong : long'
    p[0] = ' long'

def p_OptionalLong_empty(p):
    'OptionalLong :'
    p[0] = ''

def p_TypeSuffix_array(p):
    'TypeSuffix : array TypeSuffix'
    p[0] = '[]' + p[2]

def p_TypeSuffix_optional(p):
    'TypeSuffix : "?" TypeSuffixStartingWithArray'
    p[0] = '?' + p[2]

def p_TypeSuffix_empty(p):
    'TypeSuffix :'
    p[0] = ''

def p_TypeSuffixStartingWithArray_array(p):
    'TypeSuffixStartingWithArray : array TypeSuffix'
    p[0] = '[]' + p[2]

def p_TypeSuffixStartingWithArray_empty(p):
    'TypeSuffixStartingWithArray :'
    p[0] = ''

def p_Null(p):
    'Null : "?"'
    p[0] = '?'

def p_Null_empty(p):
    'Null :'
    p[0] = ''

def p_ReturnType(p):
    '''
    ReturnType : Type
               | void
    '''
    p[0] = p[1]

# From 20110712 draft
def p_ScopedNameList(p):
    'ScopedNameList : ScopedName ScopedNames'
    p[0] = [p[1]] + p[2]

# From 20110712 draft
def p_ScopedNames(p):
    'ScopedNames : "," ScopedName ScopedNames'
    p[0] = [p[2]] + p[3]

# From 20110712 draft
def p_ScopedNames_empty(p):
    'ScopedNames :'
    p[0] = []

def p_ScopedName(p):
    'ScopedName : RelativeScopedName'
    p[0] = p[1]

def p_RelativeScopedName(p):
    'RelativeScopedName : identifier'
    p[0] = p[1]

def p_integer(p):
    '''
    integer : decimalinteger
            | hexinteger
    '''
    p[0] = p[1]

lexer = lex.lex()
parser = yacc.yacc()
parse = parser.parse

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if len(args) != 1:
        print 'Usage: webidl.py IDL'
        sys.exit()
    idlfile = args[0]
    f = open(idlfile)
    idl = f.read()
    f.close()
    import pprint
    tree = parse(idl)
    pprint.pprint(tree)
