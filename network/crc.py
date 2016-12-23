def compute(msg,code = '00000000'):
    """Cyclic Redundancy Check
    Generates an error detecting code based on an inputted message
    and divisor in the form of a polynomial representation.
    Arguments:
        msg: The input message of which to generate the output code.
        div: The divisor in polynomial form. For example, if the polynomial
            of x^3 + x + 1 is given, this should be represented as '1011' in
            the div argument.
        code: This is an option argument where a previously generated code may
            be passed in. This can be used to check validity. If the inputted
            code produces an outputted code of all zeros, then the message has
            no errors.
    Returns:
        An error-detecting code generated by the message and the given divisor.
    """
    # Append the code to the message. If no code is given, default to '000'
    msg = msg + code

    # Convert msg and div into list form for easier handling
    msg = list(msg)
    div = list('11010101')

    # Loop over every message bit (minus the appended code)
    for i in range(len(msg)-len(code)):
        # If that messsage bit is 1, perform modulo 2 multiplication
        if msg[i] == '1':
            for j in range(len(div)):
                # Perform modulo 2 multiplication on each index of the divisor
                msg[i+j] = str((int(msg[i+j])+int(div[j]))%2)

    # Output the last error-checking code portion of the message generated
    return ''.join(msg[-len(code):])


def check(msg,code):
    return compute(msg,code) == '00000000'


# # TEST 1 ####################################################################
# print('Test 1 ---------------------------')
# # Use a divisor that simulates: x^3 + x + 1
# div = '11010101'
# msg = '1011001111111111111111111'
#
# print('Input message:', msg)
# print('Divisor:', div)
#
# # Enter the message and divisor to calculate the error-checking code
# code = crc(msg, div)
#
# print('Output code:', code)
#
# # Perform a test to check that the code, when run back through, returns an
# # output code of '000' proving that the function worked correctly
# print('Success:', crc(msg, div, code) == '00000000')
#
#
# # TEST 2 ####################################################################
# print('Test 2 ---------------------------')
# # Use a divisor that simulates: x^2 + 1
# div = '0101'
# msg = '00101111011101'
#
# print('Input message:', msg)
# print('Divisor:', div)
#
# # Enter the message and divisor to calculate the error-checking code
# code = crc(msg, div)
#
# print('Output code:', code)
#
# # Perform a test to check that the code, when run back through, returns an
# # output code of '000' proving that the function worked correctly
# print('Success:', crc(msg, div, code) == '000')