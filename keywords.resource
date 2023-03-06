*** Settings ***
Documentation   Resource file for a simple test suite
Library    lucas_lehmer.py
Library    OperatingSystem
Library    String

*** Variables ***
@{PRIME_EXP}  ${EMPTY}

*** Keywords ***
Verify Algorithm Corectness
    [Arguments]    ${exponent}
    ${alg_result}=    Lucas Lehmer    ${exponent}
    IF    $exponent in $PRIME_EXP
        Should Be True    ${alg_result}
    ELSE
        Should Not Be True   ${alg_result}
    END

Fetch File Data
    ${File_content}=    Get File    .//test_vector2.txt
    @{File_lines}=    Split to Lines    ${File_Content}
    [Return]   ${File_lines}

Read Prime Exponents
    Log To Console    Read Prime Exponents w
    ${File_content}=    Get File    .//p_primes.txt
    @{File_lines}=    Split to Lines    ${File_Content}
    Set Suite Variable  ${PRIME_EXP}  ${File_lines}