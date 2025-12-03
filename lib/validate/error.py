import re


class ValidationError(Exception):
    "Data Validation Error Format <https://gbv.github.io/validation-error-format/>"

    def __init__(self, message, position=None):
        super().__init__(message)
        self.position = position

    def to_dict(self):
        e = {"message": str(self)}
        if self.position:
            e["position"] = self.position
        return e

    def wrapInFile(self, file):
        message = f"{str(self)} in {file}"
        position = [{
            "dimension": "file",
            "address": file,
            "errors": [self.to_dict()]
        }]
        return ValidationError(message, position)

    def fromException(error):
        msg = str(error)
        pos = None
        if type(error) is SyntaxError and error.lineno:
            pos = {"line": error.lineno}
            if error.offset:
                pos["linecol"] = f"{error.lineno}:{error.offset}"
            # remove location from message
            msg = re.sub(f"^[^:]+line {error.lineno}[^:]*: ", "", msg)
            msg = re.sub(f"\\s*\\([^)]*line {error.lineno}[^)]*\\)$", "", msg)
        return ValidationError(msg, pos)
