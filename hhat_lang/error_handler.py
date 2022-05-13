"""Error handler class for custom exceptions """


class ExceptionTemplate(Exception):
    def __call__(self, *args):
        return self.__class__(*(self.args + args))


class TypeExcpt(ExceptionTemplate):
    """Gen message for wrong type cases """
    pass

class GeneralExcp(ExceptionTemplate):
    """Gen message for general errors """
    pass


# leaving legacy for now TODO: drop later
def error_handler_wrapper(func):
    def inner_ehw(*args):
        try:
            value = func(*args) if args else func()

        except TypeError as err:
            value = None
            success = False
            msg = f"Wrong type. ({err})"

        except Exception as err:
            value = None
            success = False
            msg = f"Wrong argument for operation. ({err})"

        else:
            success = True
            msg = ""

        return value, success, msg

    return inner_ehw

