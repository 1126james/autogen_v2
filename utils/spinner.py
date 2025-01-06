import sys
import threading
import time
import itertools
from typing import Any, Awaitable

class Spinner:
    @staticmethod
    async def async_with_spinner(
        message: str,
        style: str = "braille",
        console_class: Any = None,
        coroutine: Awaitable = None
    ):
        """
        Static method to use the spinner with async operations
        
        Args:
            message: Text to display next to the spinner
            style: Style of spinner (currently only supports "braille")
            console_class: The Console class for displaying output
            coroutine: The async operation to run while showing the spinner
        """
        spinner = Spinner(message)
        try:
            spinner.start()
            await console_class(coroutine)
            return None
        finally:
            spinner.stop()
            print()  # Add a newline before Console output starts
    
    def __init__(self, message=""):
        """
        Initialize the spinner
        
        Args:
            message: Text to display next to the spinner
        """
        self.message = message
        self.done = False
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        
    def start(self):
        """Start the spinner animation in a separate thread"""
        self.done = False
        threading.Thread(target=self._spin).start()
        
    def stop(self):
        """Stop the spinner animation"""
        self.done = True
        
    def _spin(self):
        """Internal method to handle the spinner animation"""
        while not self.done:
            char = next(self.spinner)
            sys.stdout.write(f'\r{char} {self.message}')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.flush()