from time import perf_counter  # High precision execution time measurement
from sys import exit, argv, stdout  # Termination of the script upon encountering an exception
from tkinter import messagebox  # GUI Error windows
from typing import IO  # Type hints for file stream type, purely cosmetic
from platform import system  # To check if we need to add .txt to the end of the filename

P_PROGRESS_SHOW = 10000


def lucas_lehmer(p: int) -> bool:
    """
    Function computes whether for given integer p > 0
    Mersenne number m = 2^p - 1 is prime or composite
    Returns true if prime, false if composite
    :param p: int
    :return: bool
    """
    # Special cases for which the loop won't execute
    if p == 0 or p == 1:
        return False
    if p == 2:
        return True
    # Define sequence initial variable and Mersenne number of modulus op
    s = 4
    m = pow(2, p) - 1

    progress = 0  # Variable for extra formatting
    if p > P_PROGRESS_SHOW:  # Some extra formatting if we want to see % progress of the algorithm execution
        print("Progress for p = {}: ".format(p), end="")
    # Main loop
    for i in range(p-2):
        if p > P_PROGRESS_SHOW and (i % int(((p-2) / 10)) == 0):  # Show % of execution every 10%
            print("{}% ".format(progress), end="")
            progress += 10
            stdout.flush()  # This flushes the buffer. Otherwise, the progress would not be displayed due to no newline
        # s = ((s * s) - 2) % m is unoptimised
        s = pow(s, 2, m) - 2  # Pow(s,2,m) is s^2 % m computed more efficiently using pow method

    if p > 10000:
        print()
    return s == 0


def handle_error(*args) -> None:
    """
    Function handles different types of errors.
    It generally exists to shorten the code if an exception is caught inside a function
    An error window is shown with a message indicating what went wrong.
    Then the script exits, except for error 4 where the script will continue
    args[0] is the error code, args[1] is file_name, args[2] is used only for error 3 and indicates algorithm result
    :param args: str
    :return: None
    """
    # In python 3.10 there exists "match", but for backwards compatibility it is not used
    if args[0] == 1:  # argv[1] is file name
        messagebox.showerror(title="Error!",
                             message="File {} not found! Change the filename or ensure the file is in the dir".
                             format(args[1]))
    elif args[0] == 2:
        messagebox.showerror(title="Error!",
                             message="Invalid characters found in the file {}!"
                             .format(args[1]))
    elif args[0] == 3:  # argv[1] is the exponent for which incorrect result was returned, argv[2] is the result
        messagebox.showerror(title="Assertion failed!",
                             message="Method returned invalid result for exponent {}. Should be {}".
                             format(args[1], not bool(args[2])))
    elif args[0] == 4:
        messagebox.showwarning(title="Warning!",
                               message="Can't write output to file {}. Permission denied!\
                               Output will be written to console only".format(args[1]))
        return  # For error 4 we do not want to terminate the program
    elif args[0] == 5:
        messagebox.showerror(title="Error!",
                             message="Invalid number of arguments. Provide at least input file name")

    exit(args[0])


def read_file(file_name: str) -> list[int]:
    """
    Function reads numbers from a file
    Each line is considered a different number
    Encountering a non-digit will raise an exception during int() casting
    :param file_name: str
    :return: list[int]
    """
    result = []
    try:
        with open(file_name) as file:
            for num in file.readlines():
                if int(num) < 0:
                    raise ValueError
                result.append(int(num))
            return result
            # Can also be realised with less readable:
            # return [int(num) if int(num) > 0 else handle_error(2, file_name) for num in file.readlines()]
    except FileNotFoundError:
        handle_error(1, file_name)
    except ValueError:  # Is raised in case int cast was done on a string with invalid characters e.g. a letter
        handle_error(2, file_name)


def write_out(message: str, file_handle: IO[str], close: bool) -> None:
    """
    This is a helper function that writes a message to console and file if the file exists
    If close flag is set, the function will try closing the file.
    It is assumed file handle is correct, but ValueError will occur if I/O operation is performed on a closed file
    :param message: str
    :param file_handle: IO[str]
    :param close: bool
    :return: None
    """
    print(message)
    # file_handle.closed is a failsafe. the file_handle passed here shouldn't be closed
    if file_handle and not file_handle.closed:
        file_handle.write(message + "\n")  # For files, lines need to end with "\n"
        if close:  # It needs to be nested, because otherwise we could call close() on an empty object
            file_handle.close()


def is_prime_odd(num: int) -> bool:
    """
    Performs trial division on a number to determine if it's an odd prime
    For our case, this primality determination of a number is fast
    Because the exponent of the Mersenne's numbers are not *big*
    :param num: int
    :return: bool
    """
    if num == 2 or num % 2 == 0:  # Odd primes, 2 is a prime, but not an odd prime
        return False
    sqrt_num = num**0.5  # Square root

    for i in range(3, int(sqrt_num)+1, 2):
        if num % i == 0:
            return False

    return True


def test_algorithm(known_primes: list[int], test_data: list[int], file_name: str) -> None:
    """
    Function takes known Mersenne prime exponents and exponents we want to check
    It runs the algorithm for every integer in test_data and checks if the output is correct
    If file_name argument is given, the output is also written to the file with specified name
    If file doesn't exist, it will be created (if possible)
    :param known_primes: list[int]
    :param test_data: list[int]
    :param file_name: str
    :return: None
    """
    f = None
    try:
        f = open(file_name, "w")  # Try creating the file. "w" clears the file if it exists
    except PermissionError:  # The system didn't allow to create and/or modify the file
        handle_error(4, file_name)
    except FileNotFoundError:  # If the file_name is not specified, file handle should stay as None
        pass

    write_out("Number; Is prime?; Time elapsed [s]", f, False)
    for exponent in test_data:
        if not is_prime_odd(exponent):
            write_out("Exponent {} is not prime, skipping...".format(exponent), f, False)
            continue
        # These variables need to be declared due to handling of a risky KeyboardInterrupt exception:
        is_prime = None
        t = perf_counter()  # High precision time
        try:
            is_prime = lucas_lehmer(exponent)
            t_delta = perf_counter() - t
        except KeyboardInterrupt:  # To handle manual execution abort during lucas_lehmer algorithm long computation
            t_delta = perf_counter() - t
            print()  # We only want newline in the console, but not in file
            write_out("Interrupted by user after {:.1f} s when checking 2^{} - 1".format(t_delta, exponent), f, True)
            exit(6)

        s = "2^{} - 1; {}; {:.7f}".format(exponent, is_prime, t_delta)
        try:
            if is_prime:
                assert exponent in known_primes
            else:
                assert exponent not in known_primes
        except AssertionError:  # In case algorithm returns incorrect result
            s += "\nExecution aborted due to invalid result for p = {}".format(exponent)
            write_out(s, f, True)
            handle_error(3, exponent, is_prime)  # This will exit the script after writing proper error messages
        else:
            write_out(s, f, False)

    write_out("End of tests", f, True)


def main():
    # 1st arg should be test_data filename, 2nd (optional) is output file name

    if len(argv) >= 4:
        handle_error(5)
    if len(argv) <= 1 or argv[1] == "-h" or argv[1] == "--help":
        print("Usage: python3 lucas_lehmer [test_data_file] [output_file]\n"
              "For every exponent p in test_data_file, determines if its mersenne number 2^p - 1 is prime\n\n"
              "test_data_file - should contain Mersenne exponents to be tested\n"
              "output file (optional) - file to which results are written")
        exit(0)

    primes_filename = "p_primes"  # Should be official Mersenne prime exponents .e.g from https://mersenne.org
    if system() == "Windows":  # We need to add .txt if the script is run on Windows, since the file_name is hardcoded
        primes_filename += ".txt"

    gimps_p = read_file(primes_filename)
    test_data = read_file(argv[1])  # Read test data

    if len(argv) == 3:  # If output file name was specified
        test_algorithm(gimps_p, test_data, argv[2])
    else:
        test_algorithm(gimps_p, test_data, "")


if __name__ == "__main__":
    main()
