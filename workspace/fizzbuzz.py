"""FizzBuzz script for numbers 1 to 20."""


def fizzbuzz(n: int) -> str:
    """Return FizzBuzz string for a given number.

    Args:
        n: The number to evaluate.

    Returns:
        "FizzBuzz" if divisible by 15,
        "Fizz" if divisible by 3,
        "Buzz" if divisible by 5,
        otherwise the number as string.
    """
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)


def main() -> None:
    """Print FizzBuzz for numbers 1 to 20."""
    for i in range(1, 21):
        print(fizzbuzz(i))


if __name__ == "__main__":
    main()