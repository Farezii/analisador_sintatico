#verificar quinta com que seria uma linha soh

#reserved operators
operator = ['+', '-', '*', '/']
separator = [' ', ':=', ';', ',', '\n', '(', '{', '}', ')', ':']
cmd = ['read', 'write', 'if', 'then', 'else', 'while', 'do', 'begin', 'end', 'procedure', 'program', 'real', 'integer', 'var']
comparison = ['=', '>', '>=', '<', '<=', '<>']

#components of the alphabet/identifiers
number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
char = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

#creation of the reserved and alphabet groups
ocs = operator + comparison + separator
reserved = operator + comparison + cmd + separator
alphabet = number + char

#setup for starting the reading
#i = how many characters have been read
i = 0
#mudar qual arquivo voce deseja usar, txt1, txt2, txt3 ou txt4
file = open('txt4.txt')
txt = file.read()
txt = txt + '\n'
file.close()
token = '' 
line = 1
#log de erros, cada item do vetor eh <linha>: <erro>
error = []
error_syn = []

#funcao analisador lexico
def lex(i):
    #para tornar possivel manipular variaveis fora da funcao
    global txt, token, line, error, operator, ocs, reserved, alphabet

    #booleana para verificar se ele conseguiu identificar um token
    isFound = False
    while not isFound:
        #se final da linha
        if txt[i] == '\n':
            line = line + 1
        #se comentario
        elif txt[i] == '{':
            while txt[i] != '}':
                i = i + 1
        #verifica se certo caracter do token eh invalido
        elif txt[i] != ' ':
            if (not txt[i] in alphabet) and (not txt[i] in reserved):
                       error.append('Line {}: Lexical error: {} is an invalid character.'.format(line,txt[i]))
                       print('{} - {}'.format(txt[i], 'error'))
                       token = ''
                       tokenType = 'error'
                       
            else:
                #constroe o token
                token = token + txt[i]
                if (txt[i + 1] in ocs) or (txt[i] in ocs) or (txt[1 + 1] + txt[i + 2] in ocs) or (not txt[i + 1] in alphabet) and (not txt[i + 1] in reserved):
                    #Token eh reservado
                    if token in reserved:
                        token1 = token + txt[i+1]
                        if token1 in reserved:
                            print('{} - {}'.format(token1, token1))
                            isFound = True
                            tokenType = token1
                            token = '' 
                            token1 = ''
                            i = i + 1
                        else:
                            print('{} - {}'.format(token, token))
                            isFound = True
                            tokenType = token
                            token = ''

                        
                    #final de programa
                    elif i == len(txt) - 2 and token == 'end.':
                        print('{} - {}'.format('end', 'end'))
                        print('{} - {}'.format('.', '.'))
                        isFound = True
                        tokenType = token
                        token = ''
                        
                    #Numeros
                    elif list(filter(token.startswith, number)) != []:
                        if not any(l in [ch for ch in token] for l in char):
                            #verifica se eh real
                            if ('.' in token):
                                #verifica se ultimo ou se tem mais de um ponto nele
                                if not token.endswith('.') and token.count('.') == 1:
                                    print('{} - {}'.format(token, 'real'))
                                    isFound = True
                                    token = ''
                                    tokenType = 'real'
                                else:
                                    error.append('Line {}: {} is an malformed real number.'.format(line, token))
                                    print('{} - {}'.format(token, 'error'))
                                    token = ''
                                    tokenType = 'error'
                                    
                            #nao eh real, eh inteiro, pois nao ha ponto
                            else:
                                print('{} - {}'.format(token, 'integer'))
                                isFound = True
                                token = ''
                                tokenType = 'integer'
                        else:
                            error.append('Line {}: Lexical error: {} is a malformed number.'.format(line, token))
                            print('{} - {}'.format(token, 'error'))
                            token = ''
                            tokenType = 'error'
                            
                    #nao eh numero
                    else:
                        if not '.' in token:
                            print('{} - {}'.format(token, 'identifier'))
                            isFound = True
                            token = ''
                            tokenType = 'identifier'
                        else:
                            error.append('Line (): Lexical error: {} is a malformed identifier.'.format(line, token))
                            print('{} - {}'.format(token, 'error'))
                            token = ''
                            tokenType = 'error'
        i = i + 1
    return i, tokenType

#funcoes do sintatico
def insert_error(error_message):
    global line
    error_syn.append('Line {}: Syntax error: {} was expected, but not found.'.format(line, error_message))

def program():
    current_index = 0
    current_index, token_type = lex(current_index)
    if token_type != 'program':
        insert_error('program')
    current_index, token_type = lex(current_index)
    if token_type != 'identifier':
        insert_error('identifier')
    current_index, token_type = lex(current_index)
    if token_type != ';':
        insert_error(';')
    current_index, token_type = lex(current_index)
    current_index, token_type = body(current_index, token_type)
    current_index, token_type = lex(current_index)
    if token_type != '.':
        insert_error('.')
    #return "proccess finalized"

def body(current_index, token_type):
    current_index, token_type = dc(current_index, token_type)
    current_index, token_type = lex(current_index)
    if token_type != 'begin':
        insert_error('begin')
        return current_index, token_type
    current_index, token_type = lex(current_index)
    current_index, token_type = commands(current_index, token_type)
    current_index, token_type = lex(current_index)
    if token_type != 'end':
        insert_error('end')
        return current_index, token_type
    return current_index, token_type

def dc(current_index, token_type):
    if token_type == 'var' or token_type == 'procedure':
        current_index, token_type = dc_v(current_index, token_type)
        current_index, token_type = dc_p(current_index, token_type)
        return current_index, token_type
    else:
        insert_error('var or procedure')
        return current_index, token_type

def dc_v(current_index, token_type): #lambda
    if token_type == 'var':
        current_index, token_type = lex(current_index)
        current_index, token_type = variables(current_index, token_type)
        #current_index, token_type = lex(current_index) #tirar do comentario depois pra testar
        if token_type != ':':
            insert_error('var')
            return current_index, token_type
        current_index, token_type = lex(current_index)
        current_index, token_type = var_type(current_index, token_type)
        current_index, token_type = lex(current_index)
        if token_type != ';':
            insert_error(';')
            return current_index, token_type
        current_index, token_type = lex(current_index)
        current_index, token_type = dc_v(current_index, token_type)
        return current_index, token_type
    else:
        return current_index, token_type

def var_type(current_index, token_type):
    if not (token_type == 'real' or token_type == 'integer'):
        insert_error('real or integer')
        return current_index, token_type
    return current_index, token_type

def variables(current_index, token_type):
    if token_type != 'identifier':
        insert_error('identifier')
        return current_index, token_type
    current_index, token_type = lex(current_index)
    current_index, token_type = more_var(current_index, token_type)
    return current_index, token_type

def more_var(current_index, token_type): #lambda
    if token_type == ',':
        current_index, token_type = lex(current_index)
        current_index, token_type = variables(current_index, token_type)
        return current_index, token_type
    else:
        return current_index, token_type

def dc_p(current_index, token_type): #lambda
    if token_type == 'procedure':
        current_index, token_type = lex(current_index)
        if token_type != 'identifier':
            insert_error('identifier')
            return current_index, token_type
        current_index, token_type = lex(current_index)
        current_index, token_type = parameters(current_index, token_type)
        current_index, token_type = lex(current_index)
        if token_type != ';':
            insert_error(';')
            return current_index, token_type
        current_index, token_type = lex(current_index)
        current_index, token_type = body_p(current_index, token_type)
        current_index, token_type = lex(current_index)
        current_index, token_type = dc_p(current_index, token_type)
        return current_index, token_type
    else:
        return current_index, token_type

def parameters(current_index, token_type):#lambda
    if token_type == '(':
        current_index, token_type = lex(current_index)
        current_index, token_type = par_list(current_index, token_type)
        #current_index, token_type = lex(current_index) #tirar depois pra ver
        if token_type != ')':
            insert_error(')')
            return current_index, token_type
        return current_index, token_type
    else:
        return current_index, token_type

def par_list(current_index, token_type):
    current_index, token_type = variables(current_index, token_type)
    #current_index, token_type = lex(current_index) #tirar depois rpa ver
    if token_type != ':':
        insert_error(':')
        return current_index, token_type
    current_index, token_type = lex(current_index)
    current_index, token_type = var_type(current_index, token_type)
    current_index, token_type = lex(current_index)
    current_index, token_type = more_par(current_index, token_type)
    return current_index, token_type

def more_par(current_index, token_type):
    if token_type == ';':
        current_index, token_type = lex(current_index)
        current_index, token_type = par_list(current_index, token_type)
        return current_index, token_type
    else:
        return current_index, token_type

def body_p(current_index, token_type):
    current_index, token_type = dc_v(current_index, token_type) #dc_loc
    #current_index, token_type = lex(current_index) #tirar depois pra ver
    if token_type != 'begin':
        insert_error('begin')
        return current_index, token_type
    current_index, token_type = lex(current_index)
    current_index, token_type = commands(current_index, token_type)
    current_index, token_type = lex(current_index)
    if token_type != 'end':
        insert_error('end')
        return current_index, token_type
    current_index, token_type = lex(current_index)
    if token_type != ';':
        insert_error(';')
        return current_index, token_type
    return current_index, token_type

#def dc_loc(current_index, token_type): basicamente dc_v

def arg_list(current_index, token_type):
    if token_type == '(':
        current_index, token_type = lex(current_index)
        current_index, token_type = arguments(current_index, token_type)
        current_index, token_type = lex(current_index)
        if token_type != ')':
            insert_error(')')
            return current_index, token_type
        return current_index, token_type
    else:
        return current_index, token_type

def arguments(current_index, token_type):
    if token_type != 'identifier':
        insert_error('identifier')
        return current_index, token_type
    current_index, token_type = lex(current_index)
    current_index, token_type = more_ident(current_index, token_type)
    return current_index, token_type

def more_ident(current_index, token_type):
    if token_type == ';':
        current_index, token_type = lex(current_index)
        current_index, token_type = arguments(current_index, token_type)
        return current_index, token_type
    else:
        return current_index, token_type

def pfalse(current_index, token_type): #olhar a aprtir daqui. Erro atual: a:=x+c; proximo token eh pra ser ; mas ele ja ta como ;
    if token_type == 'else':
        current_index, token_type = lex(current_index)
        current_index, token_type = cmd(current_index, token_type) #originalmente commands, mudei pra cmd
        return current_index, token_type
    else:
        return current_index, token_type

def commands(current_index, token_type):
    if token_type in cmd or token_type == 'identifier':
        current_index, token_type = CMD(current_index, token_type)
        current_index, token_type = lex(current_index)
        if token_type != ';':
            insert_error(';')
            return current_index, token_type
        current_index, token_type = lex(current_index)
        current_index, token_type = commands(current_index, token_type)
        return current_index, token_type
    else:
        return current_index, token_type

def CMD(current_index, token_type):
    if token_type == 'read':
        current_index, token_type = lex(current_index)
        if token_type != '(':
            insert_error('(')
            return current_index, token_type
        current_index, token_type = lex(current_index)
        current_index, token_type = variables(current_index, token_type)
        #current_index, token_type = lex(current_index)
        if token_type != ')':
            insert_error(')')
            return current_index, token_type
        return current_index, token_type

    if token_type == 'write':
        current_index, token_type = lex(current_index)
        if token_type != '(':
            insert_error('(')
            return current_index, token_type
        current_index, token_type = lex(current_index)
        current_index, token_type = variables(current_index, token_type)
        current_index, token_type = lex(current_index)
        if token_type != ')':
            insert_error(')')
            return current_index, token_type
        return current_index, token_type

    if token_type == 'while':
        current_index, token_type = lex(current_index)
        current_index, token_type = condition(current_index, token_type)
        current_index, token_type = lex(current_index)
        if token_type != 'do':
            insert_error('do')
            return current_index, token_type
        current_index, token_type = lex(current_index)
        current_index, token_type = CMD(current_index, token_type)
        return current_index, token_type

    if token_type == 'if':
        current_index, token_type = lex(current_index)
        current_index, token_type = condition(current_index, token_type)
        #current_index, token_type = lex(current_index)
        if token_type != 'then':
            insert_error('then')
            return current_index, token_type
        current_index, token_type = lex(current_index)
        current_index, token_type = CMD(current_index, token_type)
        current_index, token_type = lex(current_index)
        current_index, token_type = pfalse(current_index, token_type)
        return current_index, token_type

    if token_type == 'identifier':
        current_index, token_type = lex(current_index)
        if token_type == ':=':
            current_index, token_type = lex(current_index)
            current_index, token_type = expression(current_index, token_type)
            return current_index, token_type
        elif token_type == '(':
            current_index, token_type = arg_list(current_index, token_type)
            return current_index, token_type
        else:
            insert_error(':= or (')
            return current_index, token_type

    if token_type == 'begin':
        current_index, token_type = lex(current_index)
        current_index, token_type = commands(current_index, token_type)
        current_index, token_type = lex(current_index)
        if token_type != 'end':
            insert_error('end')
            return current_index, token_type
        return current_index, token_type

def condition(current_index, token_type):
    current_index, token_type = expression(current_index, token_type)
    current_index, token_type = relation(current_index, token_type)
    current_index, token_type = expression(current_index, token_type)
    return current_index, token_type

def relation(current_index, token_type):
    if token_type == '=':
        current_index, token_type = lex(current_index)
        return current_index, token_type
    elif token_type == '<>':
        current_index, token_type = lex(current_index)
        return current_index, token_type
    elif token_type == '>=':
        current_index, token_type = lex(current_index)
        return current_index, token_type
    elif token_type == '<=':
        current_index, token_type = lex(current_index)
        return current_index, token_type
    elif token_type == '>':
        current_index, token_type = lex(current_index)
        return current_index, token_type
    elif token_type == '<':
        current_index, token_type = lex(current_index)
        return current_index, token_type

def expression(current_index, token_type):
    current_index, token_type = term(current_index, token_type)
    current_index, token_type = other_term(current_index, token_type)
    return current_index, token_type

def op_un(current_index, token_type):
    if token_type == '+':
        current_index, token_type = lex(current_index)
        return current_index, token_type
    elif token_type == '-':
        current_index, token_type = lex(current_index)
        return current_index, token_type
    else:
        return current_index, token_type

def other_term(current_index, token_type):
    if token_type == '-' or token_type == '+':
        current_index, token_type = op_ad(current_index, token_type)
        current_index, token_type = term(current_index, token_type)
        current_index, token_type = other_term(current_index, token_type)
        return current_index, token_type
    else:
        return current_index, token_type

def op_ad(current_index, token_type):
    if token_type == '+':
        current_index, token_type = lex(current_index)
        return current_index, token_type
    else:
        current_index, token_type = lex(current_index)
        return current_index, token_type

def term(current_index, token_type):
    current_index, token_type = op_un(current_index, token_type)
    current_index, token_type = factor(current_index, token_type)
    current_index, token_type = more_factor(current_index, token_type)
    return current_index, token_type

def more_factor(current_index, token_type):
    if token_type == '*' or token_type == '/':
        current_index, token_type = op_mul(current_index, token_type)
        current_index, token_type = factor(current_index, token_type)
        #current_index, token_type = lex(current_index)
        current_index, token_type = more_factor(current_index, token_type)
    else:
        return current_index, token_type

def op_mul(current_index, token_type):
    if token_type == '*':
        current_index, token_type = lex(current_index)
        return current_index, token_type
    elif token_type == '/':
        current_index, token_type = lex(current_index)
        return current_index, token_type
    else:
        insert_error('* or /')
        return current_index, token_type #error

def factor(current_index, token_type):
    if token_type == 'identifier' or token_type == 'real' or token_type == 'integer':
        current_index, token_type = lex(current_index)
        return current_index, token_type
    elif token_type == '(':
        current_index, token_type = lex(current_index)
        current_index, token_type = expression(current_index, token_type)
        current_index, token_type = lex(current_index)
        if token_type != ')':
            insert_error(')')
            return current_index, token_type
        return current_index, token_type
    else:
        insert_error('identifier or real or integer or (')
        return current_index, token_type #error

#sintatico main

#fin
program()

print('\n')
while error:
    print(error.pop(0))

print('\n')
while error_syn:
    print(error_syn.pop(0))