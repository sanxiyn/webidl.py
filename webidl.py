# Web IDL parser

import sys

# Lexer

import ply.lex as lex

tokens = [
    'ellipsis',
    'array',
    'scope',
    'hexinteger',
    'decimalinteger',
    'string',
    'identifier',
]

literals = '(),:;<=>?[]{}'

# Used in WebKitIDL Conditional attribute
literals += '&|'
# Used in WebKitIDL InterfaceUUID/ImplementationUUID attribute
literals += '-'

def t_newline(t):
    r'\n'
    t.lexer.lineno += 1

def t_block_comment(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')

t_ignore = ' \t'
t_ignore_line_comment = r'//.*'

def t_error(t):
    print >>sys.stderr, "Illegal character '%s'" % (t.value[0],)
    t.lexer.skip(1)

t_ellipsis = r'\.\.\.'
t_array = r'\[\]'
t_scope = r'::'

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
    'callback',
    'caller',
    'const',
    'creator',
    'deleter',
    'dictionary',
    'double',
    'enum',
    'exception',
    'float',
    'getraises',
    'getter',
    'implements',
    'in',
    'interface',
    'legacycaller',
    'long',
    'module',
    'null',
    'optional',
    'or',
    'partial',
    'raises',
    'readonly',
    'sequence',
    'setraises',
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
    if p[2][0] == 'module':
        p[0] = p[2][2] + p[3]
    else:
        p[0] = [p[2]] + p[3]

def p_Definitions_empty(p):
    'Definitions :'
    p[0] = []

def p_Definition(p):
    '''
    Definition : Module
               | CallbackOrInterface
               | PartialInterface
               | Dictionary
               | Exception
               | Enum
               | Typedef
               | ImplementsStatement
    '''
    p[0] = p[1]

# From 20110927 draft
# Optional semicolon from WebKitIDL
def p_Module(p):
    'Module : module identifier "{" Definitions "}" optional_semicolon'
    p[0] = ['module', p[2], p[4]]

def p_CallbackOrInterface_callback(p):
    'CallbackOrInterface : callback CallbackRestOrInterface'
    p[0] = p[2]

def p_CallbackOrInterface(p):
    'CallbackOrInterface : Interface'
    p[0] = p[1]

def p_CallbackRestOrInterface(p):
    'CallbackRestOrInterface : CallbackRest'
    p[0] = ['callback'] + p[1]

def p_CallbackRestOrInterface_interface(p):
    'CallbackRestOrInterface : Interface'
    p[1][0] = 'callback interface'
    p[0] = p[1]

# ExtendedAttributeList from WebKitIDL
# Optional semicolon from WebKitIDL
def p_Interface(p):
    'Interface : interface ExtendedAttributeList identifier Inheritance "{" InterfaceMembers "}" optional_semicolon'
    p[0] = ['interface', p[3], p[6]]

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
    'DictionaryMember : Type identifier Default ";"'
    p[0] = ['attribute', p[2]]

def p_Default(p):
    'Default : "=" DefaultValue'
    p[0] = p[2]

def p_Default_empty(p):
    'Default :'
    p[0] = None

def p_DefaultValue(p):
    '''
    DefaultValue : ConstValue
                 | string
    '''
    p[0] = p[1]

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

def p_Enum(p):
    'Enum : enum identifier "{" EnumValueList "}" ";"'
    p[0] = ['enum', p[2], p[4]]

def p_EnumValueList(p):
    'EnumValueList : string EnumValues'
    p[0] = [p[1]] + p[2]

def p_EnumValues(p):
    'EnumValues : "," string EnumValues'
    p[0] = [p[2]] + p[3]

def p_EnumValues_empty(p):
    'EnumValues :'
    p[0] = []

def p_CallbackRest(p):
    'CallbackRest : identifier "=" ReturnType "(" ArgumentList ")" ";"'
    p[0] = [p[1], '']

def p_Typedef(p):
    'Typedef : typedef Type identifier ";"'
    p[0] = ['typedef', p[3], p[2]]

def p_ImplementsStatement(p):
    'ImplementsStatement : ScopedName implements ScopedName ";"'
    p[0] = ['implements', p[1], p[3]]

# ExtendedAttributeList from WebKitIDL
def p_Const(p):
    'Const : const ExtendedAttributeList ConstType identifier "=" ConstValue ";"'
    p[0] = ['const', p[4]]

def p_ConstValue(p):
    '''
    ConstValue : integer
               | null
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

# ExtendedAttributeList from WebKitIDL
def p_Attribute(p):
    'Attribute : ReadOnly attribute ExtendedAttributeList Type identifier AttributeRaises ";"'
    p[0] = ['attribute', p[5]]

def p_ReadOnly(p):
    'ReadOnly : readonly'
    p[0] = True

def p_ReadOnly_empty(p):
    'ReadOnly :'
    p[0] = False

def p_AttributeRaises(p):
    '''
    AttributeRaises : GetRaises SetRaises
                    | GetterRaises
                    | SetterRaises
                    | GetterRaises "," SetterRaises
                    | SetterRaises "," GetterRaises
    '''

# From 20110712 draft
def p_GetRaises(p):
    'GetRaises : getraises ExceptionList'
    p[0] = p[2]

# From 20110712 draft
def p_GetRaises_empty(p):
    'GetRaises :'
    p[0] = []

# From WebKitIDL
def p_GetterRaises(p):
    'GetterRaises : getter raises ExceptionList'
    p[0] = p[3]

# From 20110712 draft
def p_SetRaises(p):
    'SetRaises : setraises ExceptionList'
    p[0] = p[2]

# From 20110712 draft
def p_SetRaises_empty(p):
    'SetRaises :'
    p[0] = []

# From WebKitIDL
def p_SetterRaises(p):
    'SetterRaises : setter raises ExceptionList'
    p[0] = p[3]

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

# caller from 20110712 draft
def p_Special(p):
    '''
    Special : getter
            | setter
            | creator
            | deleter
            | legacycaller
            | caller
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

# Second ExtendedAttributeList from WebKitIDL
def p_Argument(p):
    'Argument : ExtendedAttributeList In Optional ExtendedAttributeList Type Ellipsis identifier'
    p[0] = p[7]

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
    'ExceptionField : Type identifier ";"'
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
    'Type : SingleType'
    p[0] = p[1]

def p_Type_union(p):
    'Type : UnionType TypeSuffix'
    p[0] = p[1] + p[2]

def p_SingleType(p):
    'SingleType : NonAnyType'
    p[0] = p[1]

def p_SingleType_any(p):
    'SingleType : any TypeSuffixStartingWithArray'
    p[0] = p[1] + p[2]

def p_UnionType(p):
    'UnionType : "(" UnionMemberType or UnionMemberType UnionMemberTypes ")"'
    p[0] = '(' + p[2] + ' or ' + p[4] + p[5] + ')'

def p_UnionMemberType(p):
    'UnionMemberType : NonAnyType'
    p[0] = p[1]

def p_UnionMemberType_union(p):
    'UnionMemberType : UnionType TypeSuffix'
    p[0] = p[1] + p[2]

def p_UnionMemberType_any(p):
    'UnionMemberType : any array TypeSuffix'
    p[0] = p[1] + p[2] + p[3]

def p_UnionMemberTypes(p):
    'UnionMemberTypes : or UnionMemberType UnionMemberTypes'
    p[0] = ' or ' + p[2] + p[3]

def p_UnionMemberTypes_empty(p):
    'UnionMemberTypes :'
    p[0] = ''

def p_NonAnyType(p):
    '''
    NonAnyType : PrimitiveOrStringType TypeSuffix
               | ScopedName TypeSuffix
    '''
    p[0] = p[1] + p[2]

def p_NonAnyType_sequence(p):
    'NonAnyType : sequence "<" Type ">" Null'
    p[0] = 'sequence<' + p[3] + '>' + p[5]

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

# From 20110927 draft
def p_ScopedName(p):
    'ScopedName : RelativeScopedName'
    p[0] = '::'.join(p[1])

# From 20110927 draft
def p_RelativeScopedName(p):
    'RelativeScopedName : identifier ScopedNameParts'
    p[0] = [p[1]] + p[2]

# From 20110927 draft
def p_ScopedNameParts(p):
    'ScopedNameParts : scope identifier ScopedNameParts'
    p[0] = [p[2]] + p[3]

# From 20110927 draft
def p_ScopedNameParts_empty(p):
    'ScopedNameParts :'
    p[0] = []

def p_integer(p):
    '''
    integer : decimalinteger
            | hexinteger
    '''
    p[0] = p[1]

def p_optional_semicolon(p):
    '''
    optional_semicolon : ";"
                       |
    '''

# API

lexer = lex.lex()
parser = yacc.yacc()

def parse(input):
    local_lexer = lexer.clone()
    return parser.parse(input, lexer=local_lexer)

if __name__ == '__main__':
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
