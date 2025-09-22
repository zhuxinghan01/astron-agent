"""
Unit tests for common.initialize module.
"""

from unittest.mock import Mock, patch

import pytest

from common.initialize.initialize import initialize_services


class TestInitialize:
    """Test initialize module."""

    def test_initialize_services_function_exists(self):
        """Test that initialize_services function exists and is callable."""
        assert callable(initialize_services)

    def test_initialize_services_with_none(self):
        """Test initialize_services with None services."""
        with patch(
            "common.initialize.initialize.get_factories_and_deps"
        ) as mock_get_factories:
            with patch(
                "common.initialize.initialize.service_manager"
            ) as mock_service_manager:
                mock_get_factories.return_value = []

                initialize_services(None)

                mock_get_factories.assert_called_once_with(None)
                mock_service_manager.register_factory.assert_not_called()

    def test_initialize_services_with_services(self):
        """Test initialize_services with services list."""
        services = ["service1", "service2"]
        mock_factory = Mock()
        mock_dependencies = ["dep1", "dep2"]

        with patch(
            "common.initialize.initialize.get_factories_and_deps"
        ) as mock_get_factories:
            with patch(
                "common.initialize.initialize.service_manager"
            ) as mock_service_manager:
                mock_get_factories.return_value = [(mock_factory, mock_dependencies)]

                initialize_services(services)

                mock_get_factories.assert_called_once_with(services)
                mock_service_manager.register_factory.assert_called_once_with(
                    mock_factory, dependencies=mock_dependencies
                )

    def test_initialize_services_with_exception(self):
        """Test initialize_services with exception."""
        services = ["service1"]
        mock_factory = Mock()
        mock_dependencies = ["dep1"]

        with patch(
            "common.initialize.initialize.get_factories_and_deps"
        ) as mock_get_factories:
            with patch(
                "common.initialize.initialize.service_manager"
            ) as mock_service_manager:
                with patch("common.initialize.initialize.logger") as mock_logger:
                    mock_get_factories.return_value = [
                        (mock_factory, mock_dependencies)
                    ]
                    mock_service_manager.register_factory.side_effect = Exception(
                        "Registration failed"
                    )

                    with pytest.raises(
                        RuntimeError, match="Could not initialize services"
                    ):
                        initialize_services(services)

                    mock_logger.exception.assert_called_once()

    def test_initialize_services_multiple_services(self):
        """Test initialize_services with multiple services."""
        services = ["service1", "service2", "service3"]
        mock_factory1 = Mock()
        mock_factory2 = Mock()
        mock_factory3 = Mock()

        with patch(
            "common.initialize.initialize.get_factories_and_deps"
        ) as mock_get_factories:
            with patch(
                "common.initialize.initialize.service_manager"
            ) as mock_service_manager:
                mock_get_factories.return_value = [
                    (mock_factory1, ["dep1"]),
                    (mock_factory2, ["dep2"]),
                    (mock_factory3, ["dep3"]),
                ]

                initialize_services(services)

                assert mock_service_manager.register_factory.call_count == 3
                mock_service_manager.register_factory.assert_any_call(
                    mock_factory1, dependencies=["dep1"]
                )
                mock_service_manager.register_factory.assert_any_call(
                    mock_factory2, dependencies=["dep2"]
                )
                mock_service_manager.register_factory.assert_any_call(
                    mock_factory3, dependencies=["dep3"]
                )

    def test_initialize_services_empty_services(self):
        """Test initialize_services with empty services list."""
        services = []

        with patch(
            "common.initialize.initialize.get_factories_and_deps"
        ) as mock_get_factories:
            with patch(
                "common.initialize.initialize.service_manager"
            ) as mock_service_manager:
                mock_get_factories.return_value = []

                initialize_services(services)

                mock_get_factories.assert_called_once_with(services)
                mock_service_manager.register_factory.assert_not_called()

    def test_initialize_services_logging(self):
        """Test initialize_services logging."""
        services = ["service1"]
        mock_factory = Mock()
        mock_dependencies = ["dep1"]

        with patch(
            "common.initialize.initialize.get_factories_and_deps"
        ) as mock_get_factories:
            with patch(
                "common.initialize.initialize.service_manager"
            ) as mock_service_manager:
                with patch("common.initialize.initialize.logger") as mock_logger:
                    mock_get_factories.return_value = [
                        (mock_factory, mock_dependencies)
                    ]
                    mock_service_manager.register_factory.side_effect = Exception(
                        "Test exception"
                    )

                    with pytest.raises(RuntimeError):
                        initialize_services(services)

                    # Should log the exception
                    mock_logger.exception.assert_called_once()
                    # Check that the exception was logged with the original exception
                    logged_exception = mock_logger.exception.call_args[0][0]
                    assert str(logged_exception) == "Test exception"
