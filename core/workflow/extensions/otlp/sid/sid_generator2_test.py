"""
Test module for SID Generator 2.0.

This module contains test functions to verify the functionality
of the SID generator for the 2.0 architecture.
"""

import workflow.extensions.otlp.sid.sid_generator2 as gen


def test_gen() -> None:
    """
    Test function to generate and display a sample SID.

    Initializes the SID generator with test parameters and generates
    a sample session identifier to verify the functionality.
    """
    # Initialize SID generator with test configuration
    gen.init_sid("spf", "hf", "127.0.164.187", "20000")

    # Generate and display a sample SID if generator is available
    if gen.sid_generator2 is not None:
        id = gen.sid_generator2.gen()
        print(id)
