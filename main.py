import subprocess
import datetime

def get_memory():
    result = subprocess.run(["free", "-h"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    mem_line = lines[1].split()
    total = mem_line[1]
    used = mem_line[2]
    available = mem_line[6]
    
    # Get percentage
    result2 = subprocess.run(["free"], capture_output=True, text=True)
    lines2 = result2.stdout.strip().split("\n")
    mem2 = lines2[1].split()
    total_kb = int(mem2[1])
    used_kb = int(mem2[2])
    percent = round((used_kb / total_kb) * 100, 2)
    
    status = "WARNING" if percent > 80 else "NORMAL"
    
    print("Memory")
    print("-" * 20)
    print(f"Average Usage   : {percent}%")
    print(f"Peak Usage      : {percent}%")
    print(f"Status          : {status}")
    print()

def get_disk():
    result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    disk_line = lines[1].split()
    available = disk_line[3]
    percent_used = disk_line[4].replace("%", "")
    
    status = "WARNING" if int(percent_used) > 80 else "NORMAL"
    
    print("Disk")
    print("-" * 20)
    print(f"Usage           : {percent_used}%")
    print(f"Available       : {available}")
    print(f"Status          : {status}")
    print()

def get_cpu():
    result = subprocess.run(["ps", "-A", "-o", "%cpu"], capture_output=True, text=True)
    values = [float(x) for x in result.stdout.strip().split("\n")[1:] if x.strip()]
    avg = round(sum(values) / len(values), 2) if values else 0
    peak = round(max(values), 2) if values else 0
    
    status = "WARNING" if avg > 80 else "NORMAL"
    
    print("CPU")
    print("-" * 20)
    print(f"Average Usage   : {avg}%")
    print(f"Peak Usage      : {peak}%")
    print(f"Status          : {status}")
    print()

def get_network():
    result = subprocess.run(["ss", "-tuln"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")[1:]
    
    print("Listening Ports")
    print("-" * 20)
    print()
    
    internal = []
    local = []
    
    for line in lines:
        parts = line.split()
        if len(parts) >= 5:
            proto = parts[0]
            addr_port = parts[4]
            if ":" in addr_port:
                addr, port = addr_port.rsplit(":", 1)
                if "127" in addr or "::1" in addr:
                    local.append((proto, addr, port))
                else:
                    internal.append((proto, addr, port))
    
    print("INTERNAL")
    print("-" * 20)
    print(f"{'Protocol':<10} {'Host':<25} {'Port':<10} {'Service'}")
    print("-" * 60)
    for proto, addr, port in internal:
        service = "DNS" if port == "53" else "Unknown"
        print(f"{proto:<10} {addr:<25} {port:<10} {service}")
    
    print()
    print("LOCALHOST")
    print("-" * 20)
    print(f"{'Protocol':<10} {'Host':<25} {'Port':<10} {'Service'}")
    print("-" * 60)
    for proto, addr, port in local:
        service = "DNS" if port == "53" else "Local"
        print(f"{proto:<10} {addr:<25} {port:<10} {service}")
    print()

def analyze_logs(file_path):
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

    print("Log Analysis")
    print("-" * 20)
    print(f"Total Requests  : {total_lines}")
    print(f"200 OK          : {success_200}")
    print(f"401 Unauthorized: {error_401}")
    print(f"404 Not Found   : {error_404}")
    print(f"500 Errors      : {error_500}")
    if error_500 > 0:
        print(f"Status          : WARNING - {error_500} server error(s) detected!")
    else:
        print(f"Status          : NORMAL")
    print()

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