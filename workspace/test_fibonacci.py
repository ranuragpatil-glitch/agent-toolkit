# test_fibonacci.py
"""Tests for Fibonacci sequence implementation."""
import pytest
from fibonacci import fibonacci


def test_fibonacci_base_cases():
    """Test base cases: fib(0) = 0, fib(1) = 1."""
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1


def test_fibonacci_known_values():
    """Test known Fibonacci values."""
    assert fibonacci(2) == 1
    assert fibonacci(3) == 2
    assert fibonacci(4) == 3
    assert fibonacci(5) == 5
    assert fibonacci(6) == 8
    assert fibonacci(7) == 13
    assert fibonacci(8) == 21
    assert fibonacci(9) == 34
    assert fibonacci(10) == 55


def test_fibonacci_larger_values():
    """Test larger Fibonacci values."""
    assert fibonacci(20) == 6765
    assert fibonacci(30) == 832040


def test_fibonacci_negative_raises():
    """Test that negative input raises ValueError."""
    with pytest.raises(ValueError, match="n must be non-negative"):
        fibonacci(-1)
    with pytest.raises(ValueError, match="n must be non-negative"):
        fibonacci(-10)


def test_fibonacci_non_integer_raises():
    """Test that non-integer input raises TypeError."""
    with pytest.raises(TypeError, match="Expected integer"):
        fibonacci(3.14)
    with pytest.raises(TypeError, match="Expected integer"):
        fibonacci("5")
    with pytest.raises(TypeError, match="Expected integer"):
        fibonacci(None)
    with pytest.raises(TypeError, match="Expected integer"):
        fibonacci([5])


def test_fibonacci_sequence_property():
    """Test that fib(n) = fib(n-1) + fib(n-2) for n >= 2."""
    for n in range(2, 20):
        assert fibonacci(n) == fibonacci(n - 1) + fibonacci(n - 2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])




"""Simple greeting module for Qwen2.5-Coder interactions."""

from typing import Optional


def greet_user(user_input: str) -> str:
    """Generate appropriate response based on user input.
    
    Args:
        user_input: The user's message.
        
    Returns:
        A greeting or clarification request.
    """
    user_input = user_input.strip().lower()
    
    if user_input in {"hi", "hello", "hey", "namaste"}:
        return (
            "Namaste! Main Qwen2.5-Coder hoon — aapka Python development expert.\n"
            "Kya aap koi specific coding task ka plan chahte hain? "
            "Please details share karein (requirements, constraints, examples, etc.)."
        )
    
    return "Main aapki Python coding tasks mein madad kar sakta hoon. Kya task hai?"


def main() -> None:
    """Run interactive greeting (for CLI usage)."""
    import sys
    
    if len(sys.argv) > 1:
        user_msg = " ".join(sys.argv[1:])
    else:
        user_msg = input("Aap: ")
    
    response = greet_user(user_msg)
    print(f"Qwen: {response}")


if __name__ == "__main__":
    main()
