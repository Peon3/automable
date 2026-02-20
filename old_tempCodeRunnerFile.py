import unittest
from unittest.mock import Mock

from .new_calcManagers import PostCalcManager
from .new_interfaces import (Analyzer, ChildSpawner, ErrorHandler, Parser,
                              PostValidator)


class TestPostCalcManager(unittest.TestCase):

    def setUp(self):
        """Set up common test resources."""
        self.job_data = {'id': 'test-job-123'}

        # Create mock strategies
        self.mock_parser = Mock(spec=Parser)
        self.mock_parser.__class__.__name__ = "MockParser"

        self.mock_validator = Mock(spec=PostValidator)
        self.mock_validator.__class__.__name__ = "MockValidator"

        self.failing_validator = Mock(spec=PostValidator)
        self.failing_validator.__class__.__name__ = "FailingValidator"

        self.mock_analyzer = Mock(spec=Analyzer)
        self.mock_analyzer.__class__.__name__ = "MockAnalyzer"

        self.mock_spawner = Mock(spec=ChildSpawner)
        self.mock_spawner.__class__.__name__ = "MockSpawner"

        self.mock_handler = Mock(spec=ErrorHandler)
        self.mock_handler.__class__.__name__ = "MockHandler"

    def test_run_success_scenario(self):
        """Test the successful run of PostCalcManager where all components succeed."""
        # Arrange
        self.mock_parser.parse.return_value = True
        self.mock_validator.postValidate.return_value = True
        self.mock_analyzer.analyze.return_value = True
        self.mock_spawner.spawn.return_value = True

        manager = PostCalcManager(
            parsers=[self.mock_parser],
            postValidators=[self.mock_validator],
            analyzers=[self.mock_analyzer],
            errorHandlers={},
            childSpawners=[self.mock_spawner]
        )

        # Act
        result = manager.run(self.job_data)

        # Assert
        self.assertTrue(result)
        self.mock_parser.parse.assert_called_once_with(manager, self.job_data)
        self.mock_validator.postValidate.assert_called_once_with(manager, self.job_data)
        self.mock_analyzer.analyze.assert_called_once_with(manager, self.job_data)
        self.mock_spawner.spawn.assert_called_once_with(manager, self.job_data)

    def test_run_parsing_fails(self):
        """Test that run() returns False if a parser fails."""
        # Arrange
        self.mock_parser.parse.return_value = False

        manager = PostCalcManager(
            parsers=[self.mock_parser],
            postValidators=[self.mock_validator],
            analyzers=[self.mock_analyzer],
            errorHandlers={},
            childSpawners=[self.mock_spawner]
        )

        # Act
        result = manager.run(self.job_data)

        # Assert
        self.assertFalse(result)
        self.mock_parser.parse.assert_called_once_with(manager, self.job_data)
        self.mock_validator.postValidate.assert_not_called()
        self.mock_analyzer.analyze.assert_not_called()
        self.mock_spawner.spawn.assert_not_called()

    def test_run_validation_fails_with_successful_error_handler(self):
        """Test that run() succeeds if validation fails but a corresponding error handler fixes it."""
        # Arrange
        self.mock_parser.parse.return_value = True
        self.failing_validator.postValidate.return_value = False
        self.mock_handler.handle.return_value = True
        self.mock_analyzer.analyze.return_value = True
        self.mock_spawner.spawn.return_value = True

        manager = PostCalcManager(
            parsers=[self.mock_parser],
            postValidators=[self.failing_validator],
            analyzers=[self.mock_analyzer],
            errorHandlers={"FailingValidator": [self.mock_handler]},
            childSpawners=[self.mock_spawner]
        )

        # Act
        result = manager.run(self.job_data)

        # Assert
        self.assertTrue(result)
        self.mock_parser.parse.assert_called_once()
        self.failing_validator.postValidate.assert_called_once()
        self.mock_handler.handle.assert_called_once_with(manager, self.job_data)
        self.mock_analyzer.analyze.assert_called_once()
        self.mock_spawner.spawn.assert_called_once()

    def test_run_validation_fails_with_failing_error_handler(self):
        """Test that run() fails if validation fails and the error handler also fails."""
        # Arrange
        self.mock_parser.parse.return_value = True
        self.failing_validator.postValidate.return_value = False
        self.mock_handler.handle.return_value = False

        manager = PostCalcManager(
            parsers=[self.mock_parser],
            postValidators=[self.failing_validator],
            analyzers=[self.mock_analyzer],
            errorHandlers={"FailingValidator": [self.mock_handler]},
            childSpawners=[self.mock_spawner]
        )

        # Act
        result = manager.run(self.job_data)

        # Assert
        self.assertFalse(result)
        self.mock_handler.handle.assert_called_once_with(manager, self.job_data)
        self.mock_analyzer.analyze.assert_not_called()
        self.mock_spawner.spawn.assert_not_called()

    def test_run_validation_fails_no_handler(self):
        """Test that run() fails if validation fails and there is no corresponding error handler."""
        # Arrange
        self.mock_parser.parse.return_value = True
        self.failing_validator.postValidate.return_value = False

        manager = PostCalcManager(
            parsers=[self.mock_parser],
            postValidators=[self.failing_validator],
            analyzers=[self.mock_analyzer],
            errorHandlers={},  # No handler for "FailingValidator"
            childSpawners=[self.mock_spawner]
        )

        # Act
        result = manager.run(self.job_data)

        # Assert
        self.assertFalse(result)
        self.failing_validator.postValidate.assert_called_once()
        self.mock_handler.handle.assert_not_called()
        self.mock_analyzer.analyze.assert_not_called()

    def test_run_analyzer_fails(self):
        """Test that run() fails if an analyzer fails."""
        # Arrange
        self.mock_parser.parse.return_value = True
        self.mock_validator.postValidate.return_value = True
        self.mock_analyzer.analyze.return_value = False

        manager = PostCalcManager(
            parsers=[self.mock_parser],
            postValidators=[self.mock_validator],
            analyzers=[self.mock_analyzer],
            errorHandlers={},
            childSpawners=[self.mock_spawner]
        )

        # Act
        result = manager.run(self.job_data)

        # Assert
        self.assertFalse(result)
        self.mock_analyzer.analyze.assert_called_once()
        self.mock_spawner.spawn.assert_not_called()

    def test_run_spawner_fails(self):
        """Test that run() fails if a child spawner fails."""
        # Arrange
        self.mock_parser.parse.return_value = True
        self.mock_validator.postValidate.return_value = True
        self.mock_analyzer.analyze.return_value = True
        self.mock_spawner.spawn.return_value = False

        manager = PostCalcManager(
            parsers=[self.mock_parser],
            postValidators=[self.mock_validator],
            analyzers=[self.mock_analyzer],
            errorHandlers={},
            childSpawners=[self.mock_spawner]
        )

        # Act
        result = manager.run(self.job_data)

        # Assert
        self.assertFalse(result)
        self.mock_spawner.spawn.assert_called_once()


if __name__ == '__main__':
    unittest.main()
