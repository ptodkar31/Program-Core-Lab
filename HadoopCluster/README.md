# Hadoop Distributed Architecture Design

## Overview
This project implements a distributed Hadoop architecture with NameNode, ResourceManager (modern equivalent of JobTracker), and multiple DataNodes separated by network routers.

## Architecture Components

### 1. Master Nodes
- **NameNode**: HDFS metadata management and file system namespace
- **ResourceManager**: Job scheduling and resource allocation (YARN)
- **Secondary NameNode**: Checkpoint and backup for NameNode

### 2. Worker Nodes
- **DataNodes**: Distributed data storage and block management
- **NodeManagers**: Resource management and task execution on worker nodes

### 3. Network Topology
```
Internet/WAN
     |
[ADSL Router 1] --- NameNode (Master) --- [Switch]
     |                                        |
[ADSL Router 2] --- DataNode 1              |
     |                                        |
[ADSL Router 3] --- DataNode 2              |
     |                                        |
[ADSL Router 4] --- DataNode 3 --- [Local Network]
```

## Network Configuration

### IP Address Schema
- **NameNode**: 192.168.1.10
- **ResourceManager**: 192.168.1.11  
- **Secondary NameNode**: 192.168.1.12
- **DataNode 1**: 192.168.2.10
- **DataNode 2**: 192.168.3.10
- **DataNode 3**: 192.168.4.10

### Port Configuration
- **HDFS NameNode**: 9000, 9870 (Web UI)
- **YARN ResourceManager**: 8032, 8088 (Web UI)
- **DataNode**: 9864, 9866, 9867
- **NodeManager**: 8042 (Web UI)

## Hardware Requirements

### NameNode (Master)
- **CPU**: 8+ cores
- **RAM**: 16GB+ (metadata storage)
- **Storage**: 500GB SSD (logs, metadata)
- **Network**: Gigabit Ethernet

### DataNodes (Workers)
- **CPU**: 4+ cores per node
- **RAM**: 8GB+ per node
- **Storage**: 2TB+ HDD per node (distributed storage)
- **Network**: Fast Ethernet minimum

## Replication Strategy
- **Default Replication Factor**: 3
- **Block Size**: 128MB (default)
- **Rack Awareness**: Enabled for fault tolerance

## Deployment Instructions

1. **Network Setup**
   ```bash
   # Configure static IPs on each node
   # Setup routing between ADSL segments
   # Configure firewall rules for Hadoop ports
   ```

2. **Install Hadoop**
   ```bash
   cd configs/
   ./install-hadoop.sh
   ```

3. **Configure Cluster**
   ```bash
   ./setup-namenode.sh
   ./setup-datanodes.sh
   ```

4. **Start Services**
   ```bash
   ./start-cluster.sh
   ```

## Monitoring and Management
- **HDFS Web UI**: http://namenode:9870
- **YARN Web UI**: http://resourcemanager:8088
- **Job History Server**: http://historyserver:19888

## Security Considerations
- Kerberos authentication (optional)
- SSL/TLS encryption for data transfer
- Network segmentation via ADSL routers
- Firewall rules for port access control

## Fault Tolerance
- Multiple DataNode replicas across different network segments
- Secondary NameNode for metadata backup
- Automatic failover capabilities
- Network partition tolerance through rack awareness

## Files Structure
```
HadoopCluster/
├── configs/           # Configuration files
├── scripts/           # Deployment and management scripts
├── monitoring/        # Cluster monitoring tools
├── security/          # Security configurations
└── docs/             # Additional documentation
```