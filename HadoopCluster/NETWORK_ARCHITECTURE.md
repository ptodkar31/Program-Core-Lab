# Hadoop Network Architecture Design

## Network Topology Overview

```
                        Internet/WAN
                            |
                    [Main Gateway Router]
                            |
        ┌─────────────────────────────────────────┐
        |              Core Network               |
        |         (192.168.1.0/24)               |
        └─────────────────────────────────────────┘
                            |
        ┌───────────────────┬───────────────────┬───────────────────┐
        |                   |                   |                   |
   [ADSL Router 1]     [ADSL Router 2]    [ADSL Router 3]    [ADSL Router 4]
   192.168.1.1/24      192.168.2.1/24     192.168.3.1/24     192.168.4.1/24
        |                   |                   |                   |
   [Master Nodes]      [DataNode 1]        [DataNode 2]        [DataNode 3]
        |                   |                   |                   |
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │  NameNode   │    │  DataNode   │    │  DataNode   │    │  DataNode   │
   │192.168.1.10 │    │192.168.2.10 │    │192.168.3.10 │    │192.168.4.10 │
   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
   ┌─────────────┐
   │ResourceMgr  │
   │192.168.1.11 │
   └─────────────┘
   ┌─────────────┐
   │Secondary NN │
   │192.168.1.12 │
   └─────────────┘
```

## IP Address Allocation

### Rack 1 - Master Nodes (192.168.1.0/24)
- **Gateway**: 192.168.1.1 (ADSL Router 1)
- **NameNode**: 192.168.1.10
- **ResourceManager**: 192.168.1.11  
- **Secondary NameNode**: 192.168.1.12
- **Network**: High-bandwidth, low-latency backbone

### Rack 2 - DataNode 1 (192.168.2.0/24)
- **Gateway**: 192.168.2.1 (ADSL Router 2)
- **DataNode 1**: 192.168.2.10
- **NodeManager 1**: 192.168.2.10 (co-located)
- **Network**: ADSL connection with 10-50 Mbps capacity

### Rack 3 - DataNode 2 (192.168.3.0/24)
- **Gateway**: 192.168.3.1 (ADSL Router 3)  
- **DataNode 2**: 192.168.3.10
- **NodeManager 2**: 192.168.3.10 (co-located)
- **Network**: ADSL connection with 10-50 Mbps capacity

### Rack 4 - DataNode 3 (192.168.4.0/24)
- **Gateway**: 192.168.4.1 (ADSL Router 4)
- **DataNode 3**: 192.168.4.10  
- **NodeManager 3**: 192.168.4.10 (co-located)
- **Network**: ADSL connection with 10-50 Mbps capacity

## ADSL Router Configuration

### Router 1 (Master Segment)
```bash
# Interface Configuration
interface eth0
  ip address 192.168.1.1 255.255.255.0
  
# DHCP Configuration  
dhcp pool master-pool
  network 192.168.1.0 255.255.255.0
  default-router 192.168.1.1
  dns-server 8.8.8.8 8.8.4.4
  
# Port Forwarding for Hadoop Services
ip nat inside source static tcp 192.168.1.10 9870 interface dialer0 9870
ip nat inside source static tcp 192.168.1.11 8088 interface dialer0 8088
```

### Router 2-4 (DataNode Segments)
```bash
# Example for Router 2 (similar for 3 and 4)
interface eth0
  ip address 192.168.2.1 255.255.255.0
  
# DHCP Configuration
dhcp pool datanode-pool
  network 192.168.2.0 255.255.255.0
  default-router 192.168.2.1
  dns-server 8.8.8.8 8.8.4.4
  
# Port Forwarding for DataNode
ip nat inside source static tcp 192.168.2.10 9864 interface dialer0 9864
```

## Network Security Configuration

### Firewall Rules
```bash
# Allow Hadoop ports between subnets
iptables -A INPUT -p tcp --dport 9000 -j ACCEPT  # HDFS NameNode
iptables -A INPUT -p tcp --dport 9870 -j ACCEPT  # NameNode Web UI
iptables -A INPUT -p tcp --dport 8088 -j ACCEPT  # ResourceManager Web UI
iptables -A INPUT -p tcp --dport 8032 -j ACCEPT  # ResourceManager
iptables -A INPUT -p tcp --dport 9864 -j ACCEPT  # DataNode Web UI
iptables -A INPUT -p tcp --dport 9866 -j ACCEPT  # DataNode Data Transfer
iptables -A INPUT -p tcp --dport 8042 -j ACCEPT  # NodeManager Web UI
iptables -A INPUT -p tcp --dport 22 -j ACCEPT    # SSH

# Block all other traffic
iptables -A INPUT -j DROP
```

### VPN Configuration (Optional)
```bash
# OpenVPN server on master node for secure inter-rack communication
# Client configuration on each DataNode
```

## Routing Configuration

### Static Routes
```bash
# On Master Node (192.168.1.10)
route add -net 192.168.2.0/24 gw 192.168.1.1
route add -net 192.168.3.0/24 gw 192.168.1.1  
route add -net 192.168.4.0/24 gw 192.168.1.1

# On DataNode 1 (192.168.2.10)
route add -net 192.168.1.0/24 gw 192.168.2.1
route add -net 192.168.3.0/24 gw 192.168.2.1
route add -net 192.168.4.0/24 gw 192.168.2.1
```

### DNS Resolution
```bash
# /etc/hosts on all nodes
192.168.1.10    namenode namenode.cluster.local
192.168.1.11    resourcemanager rm.cluster.local
192.168.1.12    secondarynamenode snn.cluster.local
192.168.2.10    datanode1 dn1.cluster.local
192.168.3.10    datanode2 dn2.cluster.local  
192.168.4.10    datanode3 dn3.cluster.local
```

## Bandwidth and QoS

### Traffic Prioritization
```bash
# High priority for Hadoop control traffic
tc qdisc add dev eth0 root handle 1: htb default 30
tc class add dev eth0 parent 1: classid 1:1 htb rate 50mbit
tc class add dev eth0 parent 1:1 classid 1:10 htb rate 30mbit ceil 50mbit
tc class add dev eth0 parent 1:1 classid 1:20 htb rate 15mbit ceil 40mbit
tc class add dev eth0 parent 1:1 classid 1:30 htb rate 5mbit ceil 20mbit

# Hadoop control traffic (high priority)
tc filter add dev eth0 parent 1: protocol ip prio 1 u32 match ip dport 9000 0xffff flowid 1:10
tc filter add dev eth0 parent 1: protocol ip prio 1 u32 match ip dport 8032 0xffff flowid 1:10

# Data transfer (medium priority)  
tc filter add dev eth0 parent 1: protocol ip prio 2 u32 match ip dport 9866 0xffff flowid 1:20
```

### Network Monitoring
```bash
# Bandwidth monitoring per interface
nload eth0

# Network latency testing between racks
ping -c 10 datanode1
ping -c 10 datanode2  
ping -c 10 datanode3

# Throughput testing
iperf3 -s  # On target node
iperf3 -c <target_ip> -t 60  # On source node
```

## Fault Tolerance Features

### Network Redundancy
- **Primary Path**: Direct routing through main gateway
- **Backup Path**: Mesh connectivity between ADSL routers
- **Heartbeat Monitoring**: 3-second intervals for failure detection

### Rack Awareness Implementation
- **Replication Policy**: 2 replicas on different racks + 1 local
- **Network Distance**: Configured via topology script
- **Load Balancing**: Considers network locality for job placement

### Connection Pooling
```xml
<!-- In core-site.xml -->
<property>
  <name>ipc.client.connection.maxidletime</name>
  <value>10000</value>
</property>

<property>
  <name>ipc.client.connect.max.retries</name>
  <value>10</value>
</property>
```

## Performance Optimization

### Network Tuning
```bash
# TCP buffer sizes
echo 'net.core.rmem_default = 262144' >> /etc/sysctl.conf
echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf
echo 'net.core.wmem_default = 262144' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf

# TCP congestion control
echo 'net.ipv4.tcp_congestion_control = bbr' >> /etc/sysctl.conf

# Apply changes
sysctl -p
```

### ADSL Optimization
```bash
# MTU size optimization for ADSL
ip link set dev eth0 mtu 1492

# Buffer bloat mitigation
tc qdisc add dev eth0 root fq_codel
```

## Deployment Checklist

1. **Network Infrastructure**
   - [ ] ADSL routers configured with static IPs
   - [ ] Inter-router routing tables configured
   - [ ] Firewall rules implemented
   - [ ] DNS resolution working

2. **Hadoop Configuration**  
   - [ ] Network topology script deployed
   - [ ] Rack awareness enabled
   - [ ] Worker nodes configured
   - [ ] SSH passwordless access setup

3. **Testing**
   - [ ] Network connectivity test
   - [ ] HDFS replication across racks
   - [ ] MapReduce job execution
   - [ ] Failover scenarios tested

4. **Monitoring**
   - [ ] Network monitoring tools deployed
   - [ ] Hadoop metrics collection
   - [ ] Alerting configured
   - [ ] Performance baselines established