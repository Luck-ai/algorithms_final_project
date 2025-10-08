def ask_choice(prompt, choices=('1', '2'), default='1'):
        while True:
            ans = input(prompt).strip()
            if ans == '' and default is not None:
                return default
            if ans in choices:
                return ans
            print(f"Please enter one of: {', '.join(choices)}")

def ask_yes_no(prompt, default=False):

        suffix = ' [y/N]: ' if not default else ' [Y/n]: '
        while True:
            ans = input(prompt + suffix).strip().lower()
            if ans == '' and default is not None:
                return default
            if 'y' in ans.lower():
                return True
            if 'n' in ans.lower():
                return False
            print("Please answer 'y' or 'n'.")

def ask_int(prompt, default, min_value=1, max_value=999):
        while True:
            ans = input(f"{prompt} [{default}]: ").strip()
            if ans == '':
                return default
            try:
                v = int(ans)
                if v < min_value or v > max_value:
                    print(f"Please enter a number between {min_value} and {max_value}.")
                    continue
                return v
            except ValueError:
                print("Please enter a valid integer.")