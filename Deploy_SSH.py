from netmiko import ConnectHandler
from datetime import datetime

# --------- EDIT THESE IF NEEDED ---------
ROUTER_IP = "192.168.1.1"   # IP you used on G0/0/1 in bootstrap
USERNAME = "cisco"
PASSWORD = "class"
ENABLE_SECRET = "class"
# ----------------------------------------

router = {
    "device_type": "cisco_xe",     # cisco_ios would also work on this platform
    "host": ROUTER_IP,
    "username": USERNAME,
    "password": PASSWORD,
    "secret": ENABLE_SECRET,
    "session_log": "ssh_prestage_session.log",
}

print(f"\nConnecting to router {ROUTER_IP} over SSH...\n")
conn = ConnectHandler(**router)
conn.enable()
print("Connected and in enable mode.\n")

# 1) BACKUP BEFORE CHANGE
print("--- Backing up running configuration BEFORE changes ---\n")
running_config = conn.send_command("show running-config")

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_filename = f"prestage_{ROUTER_IP}_{timestamp}.txt"

with open(backup_filename, "w") as backup_file:
    backup_file.write(running_config)

print(f"Backup saved as: {backup_filename}\n")

# 2) PRE-DEPLOYMENT CONFIGURATION
print("--- Applying pre-deployment configuration (interfaces, route, banner) ---\n")

config_commands = [
    # Update banner to indicate staged / pre-deployed state
    "banner motd ^This router was pre-staged by automation on 12_02_2025 and is ready for deployment at the remote site.^",

    # Example WAN interface (made-up addresses using documentation ranges)
    "interface GigabitEthernet0/0/0",
    " description Uplink to ISP / core (staged)",
    " ip address 198.51.100.2 255.255.255.252",   # /30, example only
    " no shut",
    " exit",

    # Example LAN interface for remote site
    "interface Serial0/1/0",
    " description Point-to-point link to remote network (staged)",
    " ip address 10.10.10.1 255.255.255.252",     # example only
    " no shut",
    " exit",

    # Static route to remote site or default route (example)
    "ip route 10.20.20.0 255.255.255.0 10.10.10.2",   # remote LAN via Serial0/1/0 next-hop

    # You could also add a default route instead / as well, e.g.:
    # "ip route 0.0.0.0 0.0.0.0 198.51.100.1",

    # Optional: tag interfaces as "ready for deployment"
    "interface GigabitEthernet0/0/1",
    " description Staging / management interface (used during bootstrap)",
    " exit",
]

output = conn.send_config_set(config_commands)
print(output)

# 3) SAVE CONFIG
print("\n--- Saving configuration (write memory) ---\n")
print(conn.send_command("write memory"))

# 4) VERIFICATION
print("\n--- Verifying interfaces ---\n")
print(conn.send_command("show ip interface brief | include GigabitEthernet0/0/0"))
print(conn.send_command("show ip interface brief | include Serial0/1/0"))
print()

print("\n--- Verifying static route ---\n")
print(conn.send_command("show ip route | include 10.20.20.0"))
print()

print("\n--- Verifying banner ---\n")
print(conn.send_command("show banner motd"))
print()

conn.disconnect()
print("\nSSH pre-deployment demo complete. Router is staged and ready to ship.\n")
