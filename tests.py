from datetime import datetime, timedelta

import unittest

from unittest.mock import Mock, MagicMock, patch, call

import os

import tempfile

import logging

from typing import ClassVar

from config import Config


class TestConfig(Config):
    """Test configuration for unit tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    ELASTICSEARCH_URL = None
    MAIL_SERVER = None
    LOG_TO_STDOUT = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    ADMINS: ClassVar = ['admin@test.com']


class CreateAppTestCase(unittest.TestCase):
    """Test cases for the create_app factory function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config = TestConfig

    def tearDown(self):
        """Clean up after tests"""
        pass

    def test_create_app_with_default_config(self):
        """Test that create_app creates an app with default config"""
        from app import create_app
        app = create_app(self.test_config)
        self.assertIsNotNone(app)
        self.assertEqual(app.config['TESTING'], True)

    def test_create_app_initializes_extensions(self):
        """Test that all Flask extensions are initialized"""
        from app import create_app, db, migrate, login, bootstrap, moment
        app = create_app(self.test_config)

        # Check that extensions are bound to the app
        with app.app_context():
            self.assertIsNotNone(db.engine)
            self.assertIn('sqlalchemy', app.extensions)
            self.assertIn('migrate', app.extensions)

    def test_create_app_sets_login_view(self):
        """Test that login view is set correctly"""
        from app import create_app, login
        create_app(self.test_config)
        self.assertEqual(login.login_view, 'main.login')

    def test_create_app_registers_blueprints(self):
        """Test that blueprints are registered"""
        from app import create_app
        app = create_app(self.test_config)

        # Check that blueprints are registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        self.assertIn('errors', blueprint_names)
        self.assertIn('main', blueprint_names)

    def test_create_app_sets_upload_folder(self):
        """Test that UPLOAD_FOLDER is configured"""
        from app import create_app
        app = create_app(self.test_config)
        self.assertEqual(app.config['UPLOAD_FOLDER'], '/app/static/images')

    def test_create_app_sets_allowed_extensions(self):
        """Test that ALLOWED_EXTENSIONS is configured as a set"""
        from app import create_app
        app = create_app(self.test_config)
        self.assertEqual(app.config['ALLOWED_EXTENSIONS'], {'png', 'jpg', 'jpeg', 'gif'})
        self.assertIsInstance(app.config['ALLOWED_EXTENSIONS'], set)

    def test_create_app_with_elasticsearch_url(self):
        """Test that Elasticsearch is configured when URL is provided"""
        from app import create_app

        class ESConfig(TestConfig):
            ELASTICSEARCH_URL = 'http://localhost:9200'

        with patch('app.Elasticsearch') as mock_es:
            mock_es_instance = MagicMock()
            mock_es.return_value = mock_es_instance

            app = create_app(ESConfig)

            mock_es.assert_called_once_with(['http://localhost:9200'])
            self.assertEqual(app.elasticsearch, mock_es_instance)

    def test_create_app_without_elasticsearch_url(self):
        """Test that Elasticsearch is None when no URL is provided"""
        from app import create_app
        app = create_app(self.test_config)
        self.assertIsNone(app.elasticsearch)

    @patch('app.configure_logging')
    def test_create_app_calls_configure_logging(self, mock_configure_logging):
        """Test that configure_logging is called"""
        from app import create_app
        app = create_app(self.test_config)
        mock_configure_logging.assert_called_once_with(app)


class ConfigureLoggingTestCase(unittest.TestCase):
    """Test cases for the configure_logging function"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = Mock()
        self.app.debug = False
        self.app.testing = False
        self.app.config = {
            'MAIL_SERVER': None,
            'LOG_TO_STDOUT': False
        }

    def test_configure_logging_skips_in_debug_mode(self):
        """Test that logging configuration is skipped in debug mode"""
        from app import configure_logging
        self.app.debug = True

        with patch('app.configure_mail_logging') as mock_mail:
            with patch('app.configure_file_logging') as mock_file:
                configure_logging(self.app)
                mock_mail.assert_not_called()
                mock_file.assert_not_called()

    def test_configure_logging_skips_in_testing_mode(self):
        """Test that logging configuration is skipped in testing mode"""
        from app import configure_logging
        self.app.testing = True

        with patch('app.configure_mail_logging') as mock_mail:
            with patch('app.configure_file_logging') as mock_file:
                configure_logging(self.app)
                mock_mail.assert_not_called()
                mock_file.assert_not_called()

    def test_configure_logging_calls_mail_logging_when_mail_server_set(self):
        """Test that mail logging is configured when MAIL_SERVER is set"""
        from app import configure_logging
        self.app.config['MAIL_SERVER'] = 'smtp.example.com'

        with patch('app.configure_mail_logging') as mock_mail:
            with patch('app.configure_file_logging') as mock_file:
                configure_logging(self.app)
                mock_mail.assert_called_once_with(self.app)
                mock_file.assert_called_once_with(self.app)

    def test_configure_logging_skips_mail_when_no_mail_server(self):
        """Test that mail logging is skipped when MAIL_SERVER is not set"""
        from app import configure_logging

        with patch('app.configure_mail_logging') as mock_mail:
            with patch('app.configure_file_logging') as mock_file:
                configure_logging(self.app)
                mock_mail.assert_not_called()
                mock_file.assert_called_once_with(self.app)

    def test_configure_logging_always_calls_file_logging_in_production(self):
        """Test that file logging is always configured in production mode"""
        from app import configure_logging

        with patch('app.configure_file_logging') as mock_file:
            configure_logging(self.app)
            mock_file.assert_called_once_with(self.app)


class ConfigureMailLoggingTestCase(unittest.TestCase):
    """Test cases for the configure_mail_logging function"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = Mock()
        self.app.logger = Mock()
        self.app.config = {
            'MAIL_SERVER': 'smtp.example.com',
            'MAIL_PORT': 587,
            'MAIL_USERNAME': None,
            'MAIL_PASSWORD': None,
            'MAIL_USE_TLS': False,
            'ADMINS': ['admin@example.com']
        }

    @patch('app.SMTPHandler')
    def test_configure_mail_logging_creates_smtp_handler(self, mock_smtp_handler):
        """Test that SMTPHandler is created with correct parameters"""
        from app import configure_mail_logging

        configure_mail_logging(self.app)

        mock_smtp_handler.assert_called_once_with(
            mailhost=('smtp.example.com', 587),
            fromaddr='no-reply@smtp.example.com',
            toaddrs=['admin@example.com'],
            subject='Recipe Book Failure',
            credentials=None,
            secure=None
        )

    @patch('app.SMTPHandler')
    def test_configure_mail_logging_with_credentials(self, mock_smtp_handler):
        """Test that credentials are set when username and password are provided"""
        from app import configure_mail_logging
        self.app.config['MAIL_USERNAME'] = 'user@example.com'
        self.app.config['MAIL_PASSWORD'] = 'secret'

        configure_mail_logging(self.app)

        call_kwargs = mock_smtp_handler.call_args[1]
        self.assertEqual(call_kwargs['credentials'], ('user@example.com', 'secret'))

    @patch('app.SMTPHandler')
    def test_configure_mail_logging_with_username_only(self, mock_smtp_handler):
        """Test that credentials are set when only username is provided"""
        from app import configure_mail_logging
        self.app.config['MAIL_USERNAME'] = 'user@example.com'

        configure_mail_logging(self.app)

        call_kwargs = mock_smtp_handler.call_args[1]
        self.assertEqual(call_kwargs['credentials'], ('user@example.com', None))

    @patch('app.SMTPHandler')
    def test_configure_mail_logging_with_password_only(self, mock_smtp_handler):
        """Test that credentials are set when only password is provided"""
        from app import configure_mail_logging
        self.app.config['MAIL_PASSWORD'] = 'secret'

        configure_mail_logging(self.app)

        call_kwargs = mock_smtp_handler.call_args[1]
        self.assertEqual(call_kwargs['credentials'], (None, 'secret'))

    @patch('app.SMTPHandler')
    def test_configure_mail_logging_with_tls(self, mock_smtp_handler):
        """Test that TLS is configured when MAIL_USE_TLS is True"""
        from app import configure_mail_logging
        self.app.config['MAIL_USE_TLS'] = True

        configure_mail_logging(self.app)

        call_kwargs = mock_smtp_handler.call_args[1]
        self.assertEqual(call_kwargs['secure'], ())

    @patch('app.SMTPHandler')
    def test_configure_mail_logging_without_tls(self, mock_smtp_handler):
        """Test that secure is None when MAIL_USE_TLS is False"""
        from app import configure_mail_logging

        configure_mail_logging(self.app)

        call_kwargs = mock_smtp_handler.call_args[1]
        self.assertIsNone(call_kwargs['secure'])

    @patch('app.SMTPHandler')
    def test_configure_mail_logging_sets_error_level(self, mock_smtp_handler):
        """Test that mail handler log level is set to ERROR"""
        from app import configure_mail_logging

        mock_handler_instance = MagicMock()
        mock_smtp_handler.return_value = mock_handler_instance

        configure_mail_logging(self.app)

        mock_handler_instance.setLevel.assert_called_once_with(logging.ERROR)

    @patch('app.SMTPHandler')
    def test_configure_mail_logging_adds_handler_to_logger(self, mock_smtp_handler):
        """Test that handler is added to app logger"""
        from app import configure_mail_logging

        mock_handler_instance = MagicMock()
        mock_smtp_handler.return_value = mock_handler_instance

        configure_mail_logging(self.app)

        self.app.logger.addHandler.assert_called_once_with(mock_handler_instance)


class ConfigureFileLoggingTestCase(unittest.TestCase):
    """Test cases for the configure_file_logging function"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = Mock()
        self.app.logger = Mock()
        self.app.config = {
            'LOG_TO_STDOUT': False
        }

    @patch('app.logging.StreamHandler')
    def test_configure_file_logging_uses_stream_handler_for_stdout(self, mock_stream_handler):
        """Test that StreamHandler is used when LOG_TO_STDOUT is True"""
        from app import configure_file_logging
        self.app.config['LOG_TO_STDOUT'] = True

        mock_handler_instance = MagicMock()
        mock_stream_handler.return_value = mock_handler_instance

        with patch('os.path.exists', return_value=True):
            with patch('os.mkdir'):
                configure_file_logging(self.app)

        mock_stream_handler.assert_called_once()
        mock_handler_instance.setLevel.assert_called_once_with(logging.INFO)

    @patch('app.RotatingFileHandler')
    def test_configure_file_logging_uses_rotating_handler_for_file(self, mock_rotating_handler):
        """Test that RotatingFileHandler is used when LOG_TO_STDOUT is False"""
        from app import configure_file_logging

        mock_handler_instance = MagicMock()
        mock_rotating_handler.return_value = mock_handler_instance

        with patch('os.path.exists', return_value=True):
            configure_file_logging(self.app)

        mock_rotating_handler.assert_called_once_with(
            'logs/app.log',
            maxBytes=10240,
            backupCount=10
        )

    @patch('app.RotatingFileHandler')
    @patch('os.mkdir')
    @patch('os.path.exists', return_value=False)
    def test_configure_file_logging_creates_logs_directory(self, _mock_exists, mock_mkdir, mock_rotating_handler):
        """Test that logs directory is created if it doesn't exist"""
        from app import configure_file_logging

        mock_handler_instance = MagicMock()
        mock_rotating_handler.return_value = mock_handler_instance

        configure_file_logging(self.app)

        mock_mkdir.assert_called_once_with('logs')

    @patch('app.RotatingFileHandler')
    @patch('os.path.exists', return_value=True)
    def test_configure_file_logging_skips_directory_creation_if_exists(self, _mock_exists, mock_rotating_handler):
        """Test that logs directory is not created if it already exists"""
        from app import configure_file_logging

        mock_handler_instance = MagicMock()
        mock_rotating_handler.return_value = mock_handler_instance

        with patch('os.mkdir') as mock_mkdir:
            configure_file_logging(self.app)
            mock_mkdir.assert_not_called()

    @patch('app.RotatingFileHandler')
    @patch('os.path.exists', return_value=True)
    def test_configure_file_logging_sets_formatter(self, _mock_exists, mock_rotating_handler):
        """Test that formatter is set on file handler"""
        from app import configure_file_logging

        mock_handler_instance = MagicMock()
        mock_rotating_handler.return_value = mock_handler_instance

        configure_file_logging(self.app)

        # Verify setFormatter was called with a Formatter instance
        self.assertEqual(mock_handler_instance.setFormatter.call_count, 1)
        formatter_arg = mock_handler_instance.setFormatter.call_args[0][0]
        self.assertIsInstance(formatter_arg, logging.Formatter)

    @patch('app.RotatingFileHandler')
    @patch('os.path.exists', return_value=True)
    def test_configure_file_logging_sets_info_level(self, _mock_exists, mock_rotating_handler):
        """Test that handler log level is set to INFO"""
        from app import configure_file_logging

        mock_handler_instance = MagicMock()
        mock_rotating_handler.return_value = mock_handler_instance

        configure_file_logging(self.app)

        mock_handler_instance.setLevel.assert_called_once_with(logging.INFO)

    @patch('app.RotatingFileHandler')
    @patch('os.path.exists', return_value=True)
    def test_configure_file_logging_adds_handler_to_logger(self, _mock_exists, mock_rotating_handler):
        """Test that handler is added to app logger"""
        from app import configure_file_logging

        mock_handler_instance = MagicMock()
        mock_rotating_handler.return_value = mock_handler_instance

        configure_file_logging(self.app)

        self.app.logger.addHandler.assert_called_once_with(mock_handler_instance)

    @patch('app.logging.StreamHandler')
    def test_configure_file_logging_sets_logger_level_to_info(self, mock_stream_handler):
        """Test that app logger level is set to INFO"""
        from app import configure_file_logging
        self.app.config['LOG_TO_STDOUT'] = True

        mock_handler_instance = MagicMock()
        mock_stream_handler.return_value = mock_handler_instance

        configure_file_logging(self.app)

        self.app.logger.setLevel.assert_called_once_with(logging.INFO)

    @patch('app.logging.StreamHandler')
    def test_configure_file_logging_logs_startup_message(self, mock_stream_handler):
        """Test that startup message is logged"""
        from app import configure_file_logging
        self.app.config['LOG_TO_STDOUT'] = True

        mock_handler_instance = MagicMock()
        mock_stream_handler.return_value = mock_handler_instance

        configure_file_logging(self.app)

        self.app.logger.info.assert_called_once_with('Recipe book startup')


class IntegrationTestCase(unittest.TestCase):
    """Integration tests for the complete app initialization"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config = TestConfig

    def test_create_app_full_initialization(self):
        """Test complete app creation and initialization"""
        from app import create_app
        app = create_app(self.test_config)

        # Test that app is configured correctly
        self.assertTrue(app.testing)
        self.assertIsNotNone(app.config['SECRET_KEY'])

        # Test that all config keys are set
        self.assertIn('UPLOAD_FOLDER', app.config)
        self.assertIn('ALLOWED_EXTENSIONS', app.config)

        # Test that blueprints work
        with app.test_client() as client:
            # This should hit a route from one of the blueprints or 404
            response = client.get('/')
            # We expect either a valid response or 404, not a 500
            self.assertIn(response.status_code, [200, 302, 404, 405])

    def test_app_context_includes_models(self):
        """Test that models can be imported after app creation"""
        from app import create_app
        app = create_app(self.test_config)

        with app.app_context():
            # Models should be importable
            from app.models import Recipe2, User, Ingredients
            self.assertIsNotNone(Recipe2)
            self.assertIsNotNone(User)
            self.assertIsNotNone(Ingredients)

    @patch('app.Elasticsearch')
    def test_app_with_all_features_enabled(self, mock_es):
        """Test app creation with all features enabled"""
        from app import create_app

        class FullConfig(TestConfig):
            ELASTICSEARCH_URL = 'http://localhost:9200'
            MAIL_SERVER = 'smtp.example.com'
            MAIL_PORT = 587
            MAIL_USERNAME = 'user@example.com'
            MAIL_PASSWORD = 'secret'
            MAIL_USE_TLS = True
            LOG_TO_STDOUT = True
            DEBUG = False
            TESTING = False

        mock_es_instance = MagicMock()
        mock_es.return_value = mock_es_instance

        # This should not raise any exceptions
        app = create_app(FullConfig)

        self.assertIsNotNone(app)
        self.assertEqual(app.elasticsearch, mock_es_instance)


class EdgeCasesTestCase(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_configure_mail_logging_with_empty_admins_list(self):
        """Test mail logging with empty admins list"""
        from app import configure_mail_logging
        app = Mock()
        app.logger = Mock()
        app.config = {
            'MAIL_SERVER': 'smtp.example.com',
            'MAIL_PORT': 587,
            'MAIL_USERNAME': None,
            'MAIL_PASSWORD': None,
            'MAIL_USE_TLS': False,
            'ADMINS': []
        }

        with patch('app.SMTPHandler') as mock_handler:
            configure_mail_logging(app)
            # Should still be called even with empty list
            mock_handler.assert_called_once()

    def test_configure_mail_logging_with_multiple_admins(self):
        """Test mail logging with multiple admins"""
        from app import configure_mail_logging
        app = Mock()
        app.logger = Mock()
        app.config = {
            'MAIL_SERVER': 'smtp.example.com',
            'MAIL_PORT': 587,
            'MAIL_USERNAME': None,
            'MAIL_PASSWORD': None,
            'MAIL_USE_TLS': False,
            'ADMINS': ['admin1@example.com', 'admin2@example.com', 'admin3@example.com']
        }

        with patch('app.SMTPHandler') as mock_handler:
            configure_mail_logging(app)
            call_kwargs = mock_handler.call_args[1]
            self.assertEqual(len(call_kwargs['toaddrs']), 3)

    def test_configure_file_logging_with_none_log_to_stdout(self):
        """Test file logging when LOG_TO_STDOUT is None (falsy)"""
        from app import configure_file_logging
        app = Mock()
        app.logger = Mock()
        app.config = {'LOG_TO_STDOUT': None}

        with patch('app.RotatingFileHandler') as mock_handler:
            with patch('os.path.exists', return_value=True):
                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance
                configure_file_logging(app)
                # Should use file handler, not stream handler
                mock_handler.assert_called_once()

    def test_create_app_with_custom_config_class(self):
        """Test creating app with a custom configuration class"""
        from app import create_app

        class CustomConfig(TestConfig):
            CUSTOM_SETTING = 'custom_value'
            UPLOAD_FOLDER = '/custom/path'

        app = create_app(CustomConfig)

        self.assertEqual(app.config['CUSTOM_SETTING'], 'custom_value')
        # UPLOAD_FOLDER should be overridden by create_app
        self.assertEqual(app.config['UPLOAD_FOLDER'], '/app/static/images')

    def test_allowed_extensions_is_mutable_set(self):
        """Test that ALLOWED_EXTENSIONS can be modified"""
        from app import create_app
        app = create_app(TestConfig)

        original_extensions = app.config['ALLOWED_EXTENSIONS'].copy()
        app.config['ALLOWED_EXTENSIONS'].add('webp')

        self.assertIn('webp', app.config['ALLOWED_EXTENSIONS'])
        self.assertEqual(len(app.config['ALLOWED_EXTENSIONS']), len(original_extensions) + 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)