"""

Actual 'engine' for testing console. No surprise, this file is to be used for testing

'"""

import importlib
import pkgutil
import tests

# allowed to run through and pick up on naming conventions
def discover_tests():
    test_modules = []
    for importer, name, _ in pkgutil.iter_modules(tests.__path__):
        if name.startswith('test_'):
            module = importlib.import_module(f'tests.{name}')
            if hasattr(module, 'NAME') and hasattr(module, 'run'):
                test_modules.append(module)
    # sort alphabetically by name for consistent ordering
    test_modules.sort(key=lambda m: m.NAME)
    return test_modules

def main():
    modules = discover_tests()

    # simple console 'UI' for easier testing on my end. will be losing my mind otherwise. Will provide more 
    # value as I add more features to the chain
    while True:
        print("\n  ***********************************************")
        print("  *         ChipChain Test Console               *")
        print("  ************************************************")
        # runs through options
        for i, mod in enumerate(modules, 1):
            label = f"{i}. {mod.NAME}"
            print(f"  *  {label:<42}  *")
        all_label = f"{len(modules)+1}. Run all tests"
        print(f"  *  {all_label:<42}  *")
        print(f"  *  {'0. Exit':<42}  *")
        print("  ************************************************")

        #takes in input that corresponds to a given test
        choice = input("\n  Enter choice: ").strip()

        if choice == '0':
            print("\n  Exiting...\n")
            break
        elif choice == str(len(modules) + 1):
            for mod in modules:
                mod.run()
            print(f"\n  {'*' * 46}")
            print("    All tests complete!") 
            print(f"  {'*' * 46}") 
        elif choice.isdigit() and 1 <= int(choice) <= len(modules):
            modules[int(choice) - 1].run()
        else:
            print("\n  Invalid choice, try again...")

if __name__ == "__main__":
    main()