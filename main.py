import subprocess

def get_memory():
  print("=== Memory Usage ===")
  memory = subprocess.run(["free", "-h"], capture_output=True, text=True)
  print(memory.stdout)

def get_disk():
   print("=== Disk Usage ===")
   disk = subprocess.run(["df", "-h"], capture_output=True, text=True)
   print(disk.stdout)

def get_cpu():
   print("=== CPU Usage ===")
   cpu = subprocess.run("ps aux --sort=-%cpu | head -10", capture_output=True, text=True, shell=True)
   print(cpu.stdout)

def get_network():
   print("=== Network Usage ===")
   network = subprocess.run(["ss", "-tuln"], capture_output=True, text=True)
   print(network.stdout)

def analyze_logs(file_path):
    print("=== Log Analysis ===")
    total = 0
    with open(file_path, "r") as file:
        for line in file:
            if "500" in line:
                total += 1
    print(f"Total 500 errors found: {total}")
    return total

def main():
    print("=========================================")
    print("     SRE SYSTEM DIAGNOSTICS REPORT")
    print("=========================================")
    get_memory()
    get_disk()
    get_cpu()
    get_network()
    analyze_logs("logs.txt")
    print("=========================================")
    print("          END OF REPORT")
    print("=========================================")


if __name__ == "__main__":
    main()