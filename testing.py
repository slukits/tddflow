class T(object):
    """
    A T instance t provides means to communicate with the testing
    framework (e.g. t.breakIfNot) and to assert expected behavior (e.g.
    t.truthy).
    """

    def __init__(self, failed: callable):
        self.__failed = failed

    def truthy(self, value) -> bool:
        if value:
            return True
        self.__failed(True)
