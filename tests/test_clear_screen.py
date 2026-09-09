import sys
from digital_bomb.utils.clear_screen import clear_screen


def test_clear_screen_windows(mocker):
    mock_run = mocker.patch("digital_bomb.utils.clear_screen.run")
    mock_flush = mocker.patch("sys.stdout.flush")
    mocker.patch.object(sys, "platform", "win32")
    mock_logger = mocker.patch("digital_bomb.utils.clear_screen.logger")

    clear_screen()

    mock_run.assert_called_once_with(["cmd", "/c", "cls"])
    mock_flush.assert_called_once()
    mock_logger.exception.assert_not_called()


def test_clear_screen_non_windows(mocker):
    mock_run = mocker.patch("digital_bomb.utils.clear_screen.run")
    mock_flush = mocker.patch("sys.stdout.flush")
    mocker.patch.object(sys, "platform", "linux")
    mock_logger = mocker.patch("digital_bomb.utils.clear_screen.logger")

    clear_screen()

    mock_run.assert_called_once_with(["/usr/bin/clear"])
    mock_flush.assert_called_once()
    mock_logger.exception.assert_not_called()