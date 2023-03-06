*** Settings ***
Documentation   Very simple test suite for lucas_lehmer primality test
Resource    keywords.resource
Suite Setup  Read Prime Exponents  # To obtain known Mersenne prime exponents from the external file
Default Tags    positive

*** Test Cases ***
Check Single Primality Test
    Verify Algorithm Corectness    5

Check Multiple Primality Test
    Verify Algorithm Corectness    2    5    7    13    302    303

Check Multiple With Data From File
    ${exponent_array}=    Fetch File Data
#    FOR  ${line}  IN  @{test_array}
#        Log To Console    ${line}
#    END
   FOR  ${exponent}  IN  @{exponent_array}
       Verify Algorithm Corectness  ${exponent}
   END