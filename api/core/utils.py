class U:
    # Function is needed to make dictionary hashable/comparable
    # ie when using set() function
    @staticmethod
    def frozendict(d: dict):
        return frozenset(d.keys()), frozenset(d.values())
