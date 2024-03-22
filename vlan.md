# Document for Configuring Cisco Switch in GNS3

This guide is structured to ensure clear communication of each necessary step for configuring a Cisco switch within GNS3, with a strong emphasis on the critical step of entering configuration mode.

## Essential Steps Overview
1. **Entering Configuration Mode**: The foundational step for any configuration task on the Cisco switch.
2. **Performing Configuration Tasks**: Includes creating VLANs, assigning ports, etc.
3. **Exiting Configuration Mode**: Necessary to apply the configurations made.
4. **Saving the Configurations**: To ensure configurations persist after a system restart.

## Step-by-Step Commands

### Critical Step: Entering Configuration Mode

Before any configuration task, it is mandatory to enter the global configuration mode. Omitting this step will result in an inability to configure the switch.

```
SW1#configure terminal
SW1(config)#
```

### Exit Configuration Mode and Save Changes

After making your configuration changes, exit the configuration mode and save your changes to prevent loss:

```
SW1(config)#end
SW1#write
```

### Example: Creating VLAN 99 and Assigning Port Gi1/8

1. Enter Configuration Mode:

    ```
    SW1#configure terminal
    ```

1. Create VLAN 99 and Name It:

    ```
    SW1(config)#vlan 99
    SW1(config-vlan)#name Management
    ```

1. Assign Port Gi1/8 to VLAN 99:

    ```
    SW1(config)#interface gi1/8
    SW1(config-if)#switchport mode access
    SW1(config-if)#switchport access vlan 99
    SW1(config-if)#no shutdown
    ```

1. Exit Configuration Mode:

    ```
    SW1(config-if)#end
    ```

1. Save Configuration:

    ```
    SW1#write
    ```

### Additional Commands

* **Display VLAN Information**: Useful for verifying your VLAN configurations.

```
SW1#show vlan
```
