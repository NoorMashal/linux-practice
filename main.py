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
    total_lines = 0
    error_500 = 0
    error_404 = 0
    error_401 = 0
    success_200 = 0

    with open(file_path, "r") as file:
        for line in file:
            total_lines += 1
            if "500" in line:
                error_500 += 1
            if "404" in line:
                error_404 += 1
            if "401" in line:
                error_401 += 1
            if "200" in line:
                success_200 += 1

    print(f"  Total Requests:     {total_lines}")
    print(f"  200 OK:             {success_200}")
    print(f"  401 Unauthorized:   {error_401}")
    print(f"  404 Not Found:      {error_404}")
    print(f"  500 Server Errors:  {error_500}")
    if error_500 > 0:
        print(f"WARNING: {error_500} server errors detected!")

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
    print("Authenticating with Azure...")
    subprocess.run(["az", "login"], check=False)

    location = "canadaeast"

    # Let the user choose resource group (folder)
    print("=== List of existing Resource Groups ===")
    result = subprocess.run(["az", "group", "list", "--query", "[].name", "-o", "tsv"], capture_output=True, text=True)
    print(result.stdout)

    rg_choice = input("Enter the name of the Resource Group to use (or type 'new' to create a new one): ")

    # Make sure the user enters a valid choice
    while True:
        if rg_choice in result.stdout.splitlines() or rg_choice.lower() == "new":
            break
        else:
            print("Invalid choice. Please enter a valid Resource Group name or 'new'.")
            rg_choice = input("Enter the name of the Resource Group to use (or type 'new' to create a new one): ")
    
    if rg_choice.lower() == "new":
        rg_name = input("Enter the name for the new Resource Group: ").strip()
        print("=== Creating Resource Group ===")
        run_az_command(["az", "group", "create", "--name", rg_name, "--location", location])
    else:
        rg_name = rg_choice

    if rg_choice.lower() == "new": # If the user chose to create a new resource group, prompt for VM name without checking for duplicates
        vm_name = input("Enter the name for the new VM: ").strip()

    else: # Check if the VM name already exists in the resource group
        result = subprocess.run(["az", "vm", "list", "--resource-group", rg_name, "--query", "[].name", "-o", "tsv"], capture_output=True, text=True)
        existing_vms = result.stdout.splitlines()
        print("=== List of existing VMs in Resource Group ===")
        print(result.stdout)
        
        # Check if the VM name already exists in the resource group
        while True:
            vm_name = input("Enter the name for the new VM: ").strip()
            if vm_name in existing_vms:
                print(f"VM name '{vm_name}' already exists in Resource Group '{rg_name}'. Please choose a different name.")
            else:
                break

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
    teardown = input("\nRun teardown when done? (y/n): ")
    if teardown.lower() == "y":
        print("=== Tearing Down Resources ===")
        run_az_command(["az", "group", "delete", "--name", rg_name, "--yes", "--no-wait"])
        print("Teardown initiated!")

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