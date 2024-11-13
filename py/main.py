import subprocess

def run_script(script_name, args=None):
    command = ['python', script_name]
    if args:
        command.extend(args)
    
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"execution error on {script_name}:")
        print(result.stderr)
        exit(1)
    else:
        print(f"{script_name} successfull execution.")
        print(result.stdout)

def main():

    print("dataCatalog.py esecution...")
    run_script('dataCatalog.py')

    print("aiRequest.py esecution...")
    run_script('aiRequest.py')

    print("resultAnalyzer.py esecution...")
    run_script('resultAnalyzer.py')

if __name__ == "__main__":
    main()
