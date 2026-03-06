from netmiko import ConnectHandler
import time

# -------- CONFIGURE THESE VALUES --------
COM_PORT = "COM6"        # Change to your COM port (e.g., COM3, COM5)
ROUTER_IP = "192.168.1.1"
ROUTER_MASK = "255.255.255.0"
USERNAME = "cisco"
PASSWORD = "class"
HOSTNAME = "MSTC_NET3_Bootstrap"
INTERFACE = "GigabitEthernet0/0/1"
# ----------------------------------------

print("\nConnecting to router console...\n")

router = {
    "device_type": "cisco_ios_serial",
    "host": "console",
#    "username": USERNAME,
#   "password": PASSWORD,
#   "secret": PASSWORD,
    "session_log": "console_session.log",
    "serial_settings": {
        "port": COM_PORT,     # "COM4", "COM3", etc.
        "baudrate": 9600,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1,
        "timeout": 1
    }
}


# Connect using console (serial)
conn = ConnectHandler(**router)
conn.enable()

print("Connected via console.")
time.sleep(1)

print("\n--- Starting bootstrap configuration ---\n")
time.sleep(1)

bootstrap_commands = [
     # Basic identity and global behavior
    f"hostname {HOSTNAME}",
    "banner motd ^This device was configured using Bootstrap Version 12_2_2025 and ready to deploy if a newer version is not available^",
    "no ip domain-lookup",
    "service password-encryption",
    "enable secret class",
    f"username {USERNAME} privilege 15 secret {PASSWORD}",
    "ip domain-name MSTC_demo.local",

    # Interface configuration
    f"interface {INTERFACE}",
    f" ip address {ROUTER_IP} {ROUTER_MASK}",
    " no shut",
    "exit",

    # SSH crypto + version
    "crypto key generate rsa modulus 2048",
    "ip ssh version 2",

    # VTY lines
    "line vty 0 4",
    " login local",
    " transport input ssh",
    " exec-timeout 5 0",
    " exit",

    # Console line
    "line console 0",
    " login local",
    " logging synchronous",
    " exec-timeout 5 0",
    " exit",
    

]

output = conn.send_config_set(bootstrap_commands)
print(output)

print("\nSaving configuration (write memory)...\n")
print(conn.send_command("write memory"))
time.sleep(2)

print("\n--- Verification Output ---\n")
print(conn.send_command("show ip interface brief"))
print()
print(conn.send_command("show run | include username"))
print()
print(conn.send_command("show run | section line vty"))
print()
print(conn.send_command("show crypto key mypubkey rsa"))
print()

conn.disconnect()
print("\nBootstrap complete. Router is now SSH-ready.")

