def is_palindrome(s: str) -> bool:
    """
    Check if a string is a palindrome, ignoring case and non-alphanumeric characters.

    Args:
        s: The input string to check.

    Returns:
        True if the string is a palindrome, False otherwise.
    """
    filtered = [ch.lower() for ch in s if ch.isalnum()]
    return filtered == filtered[::-1]


if __name__ == "__main__":
    test_cases = [
        ("A man, a plan, a canal: Panama", True),
        ("race a car", False),
        ("No lemon, no melon", True),
    ]

    all_passed = True
    for input_str, expected in test_cases:
        result = is_palindrome(input_str)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        print(f"{status}: is_palindrome({input_str!r}) = {result} (expected {expected})")

    if all_passed:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")