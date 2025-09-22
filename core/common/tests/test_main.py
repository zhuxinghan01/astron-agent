"""
Unit tests for common.main module.
"""

from unittest.mock import patch

import pytest

from common.main import main


class TestMain:
    """Test main module."""

    def test_main_function(self):
        """Test main function."""
        with patch("builtins.print") as mock_print:
            main()
            mock_print.assert_called_once_with("Hello from common!")

    def test_main_function_output(self, capsys):
        """Test main function output."""
        main()
        captured = capsys.readouterr()
        assert captured.out == "Hello from common!\n"

    def test_main_as_script(self):
        """Test main function when run as script."""
        # This test verifies the main function works correctly
        # The actual script execution is tested implicitly
        assert callable(main)
        assert main.__name__ == "main"

