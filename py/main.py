import subprocess

def run_script(script_name, args=None):
    """Esegue uno script con argomenti opzionali e stampa l'output."""
    command = ['python', script_name]
    if args:
        command.extend(args)
    
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Errore nell'esecuzione di {script_name}:")
        print(result.stderr)
        exit(1)
    else:
        print(f"{script_name} eseguito con successo.")
        print(result.stdout)

def main():
    # Step 1: Esegui dataCatalog.py
    print("Esecuzione di dataCatalog.py...")
    run_script('dataCatalog.py')

    # Step 2: Esegui aiRequest.py
    print("Esecuzione di aiRequest.py...")
    run_script('aiRequest.py')

    # Step 3: Esegui resultAnalyzer.py
    print("Esecuzione di resultAnalyzer.py...")
    run_script('resultAnalyzer.py')

if __name__ == "__main__":
    main()
