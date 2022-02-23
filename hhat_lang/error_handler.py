

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

