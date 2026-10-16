"""Fibonacci module with iterative implementation and input validation."""


def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number iteratively.

    Args:
        n: The index of the Fibonacci number to calculate (0-indexed).

    Returns:
        The nth Fibonacci number.

    Raises:
        TypeError: If n is not an integer.
        ValueError: If n is negative.
    """
    if not isinstance(n, int):
        raise TypeError(f"Expected integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")

    if n == 0:
        return 0
    if n == 1:
        return 1

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


if __name__ == "__main__":
    # Test cases
    assert fibonacci(0) == 0, "fibonacci(0) should be 0"
    assert fibonacci(1) == 1, "fibonacci(1) should be 1"
    assert fibonacci(2) == 1, "fibonacci(2) should be 1"
    assert fibonacci(3) == 2, "fibonacci(3) should be 2"
    assert fibonacci(10) == 55, "fibonacci(10) should be 55"
    assert fibonacci(20) == 6765, "fibonacci(20) should be 6765"

    # Test negative input
    try:
        fibonacci(-1)
        assert False, "Should raise ValueError for negative input"
    except ValueError:
        pass

    # Test non-integer input
    try:
        fibonacci(3.5)
        assert False, "Should raise TypeError for float input"
    except TypeError:
        pass

    try:
        fibonacci("5")
        assert False, "Should raise TypeError for string input"
    except TypeError:
        pass

    print("All tests passed!")