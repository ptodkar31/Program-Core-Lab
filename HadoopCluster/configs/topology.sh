#!/bin/bash

# Network Topology Script for Hadoop Rack Awareness
# Maps IP addresses to rack locations for fault tolerance

# Function to determine rack based on IP address
get_rack_for_ip() {
    local ip=$1
    
    case $ip in
        # Master nodes - Rack 1 (192.168.1.x subnet)
        192.168.1.*)
            echo "/rack1"
            ;;
        # DataNode 1 - Rack 2 (192.168.2.x subnet - ADSL Router 2)
        192.168.2.*)
            echo "/rack2"
            ;;
        # DataNode 2 - Rack 3 (192.168.3.x subnet - ADSL Router 3)
        192.168.3.*)
            echo "/rack3"
            ;;
        # DataNode 3 - Rack 4 (192.168.4.x subnet - ADSL Router 4)
        192.168.4.*)
            echo "/rack4"
            ;;
        # Hostname resolution fallback
        *)
            # Try to resolve hostname to IP
            resolved_ip=$(nslookup $ip 2>/dev/null | grep "Address:" | tail -1 | awk '{print $2}')
            if [[ -n "$resolved_ip" ]]; then
                get_rack_for_ip $resolved_ip
            else
                echo "/default-rack"
            fi
            ;;
    esac
}

# Main script logic
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <hostname1> [hostname2] [hostname3] ..."
    exit 1
fi

# Process each hostname/IP provided as argument
for node in "$@"; do
    # Try to resolve hostname to IP if it's not already an IP
    if [[ $node =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        # It's already an IP address
        rack=$(get_rack_for_ip $node)
    else
        # It's a hostname, resolve to IP
        ip=$(getent hosts $node | awk '{print $1}' | head -1)
        if [[ -n "$ip" ]]; then
            rack=$(get_rack_for_ip $ip)
        else
            rack="/default-rack"
        fi
    fi
    
    echo "$rack"
done