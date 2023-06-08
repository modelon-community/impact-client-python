class Log(str):
    """Log class inheriting from string object."""

    def show(self) -> None:
        """Prints the formatted log."""
        print(self)
