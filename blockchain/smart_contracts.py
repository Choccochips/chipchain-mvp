"""

This file will hold the logic for smart contracts on chipchain. As the file name suggests, smart contracts will be implemented in 
python for now. Will almost certainly move to an actual existing framework

"""

class SmartContract():
    def __init__(self, address = None, code = None, state = None, owner = ''):
        self.address = address
        # used to dict maps to callable functions 
        self.code = code or {}
        # dict for persistant storage
        self.state = state or {}
        self.owner = owner

    def execute(self, func_name, args, caller, chain = None):
        # check if the function exists in the code
        if func_name in self.code:
            # if so we call and pass args
            to_call = self.code[func_name]

            # check func signature
            import inspect
            sig = inspect.signature(to_call)

            if 'chain' in sig.parameters:
                return to_call(self.state, args, caller, chain)
            else:
                return to_call(self.state, args, caller)
        else:
            raise Exception('Function does not exist')

