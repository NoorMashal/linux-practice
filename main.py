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

def run_az_command(command_list):
    print(f"Executing: {' '.join(command_list)}")
    try:
        result = subprocess.run(command_list, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command!")
        print(f"Error Code: {e.returncode}")
        print(e.stderr)

def create_vm():
    rg_name = "rg-compute-prod-01"
    vm_name = "vm-appserver-prod-01"
    location = "canadaeast"

    print("=== Creating Resource Group ===")
    run_az_command(["az", "group", "create", "--name", rg_name, "--location", location])

    print("=== Creating VM ===")
    run_az_command(["az", "vm", "create",
        "--resource-group", rg_name,
        "--name", vm_name,
        "--image", "Ubuntu2204",
        "--size", "Standard_B2ats_v2",
        "--storage-sku", "Standard_LRS",
        "--admin-username", "azureuser",
        "--generate-ssh-keys",
        "--location", location,
        "--nsg", ""])

    print("=== Setting Auto-Shutdown ===")
    run_az_command(["az", "vm", "auto-shutdown",
        "--resource-group", rg_name,
        "--name", vm_name,
        "--time", "1800",
        "--location", location])

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

    choice = input("\nDeploy to Azure? (y/n): ")
    if choice.lower() == "y":
        create_vm()
    else:
        print("Skipping Azure deployment.")


if __name__ == "__main__":
    main()