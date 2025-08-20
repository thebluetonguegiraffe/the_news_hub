import subprocess
from config import db_configuration

def run_chroma():
    path = db_configuration['db_path']
    subprocess.run(["chroma", "run", "--path", f"db/{path}"])

if __name__ == "__main__":
    run_chroma()


