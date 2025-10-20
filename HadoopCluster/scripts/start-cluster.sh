#!/bin/bash

# Hadoop Cluster Management Script
# Start, stop, and manage the entire Hadoop cluster

set -e

# Configuration
HADOOP_USER="hadoop"
HADOOP_HOME="/opt/hadoop"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo -e "${BLUE}[SECTION]${NC} $1"
}

# Check if HDFS is formatted
check_hdfs_format() {
    log_info "Checking HDFS format status..."
    
    if [[ ! -d "$HADOOP_HOME/hdfs/namenode/current" ]]; then
        log_warn "HDFS is not formatted. Formatting now..."
        sudo -u $HADOOP_USER $HADOOP_HOME/bin/hdfs namenode -format -force
        log_info "HDFS formatted successfully"
    else
        log_info "HDFS is already formatted"
    fi
}

# Start HDFS services
start_hdfs() {
    log_section "Starting HDFS Services"
    
    log_info "Starting NameNode..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/hadoop-daemon.sh start namenode
    
    log_info "Starting Secondary NameNode..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/hadoop-daemon.sh start secondarynamenode
    
    log_info "Starting DataNodes..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/hadoop-daemons.sh start datanode
    
    # Wait for services to start
    sleep 5
    
    log_info "HDFS services started successfully"
}

# Start YARN services
start_yarn() {
    log_section "Starting YARN Services"
    
    log_info "Starting ResourceManager..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/yarn-daemon.sh start resourcemanager
    
    log_info "Starting NodeManagers..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/yarn-daemons.sh start nodemanager
    
    log_info "Starting Job History Server..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver
    
    # Wait for services to start
    sleep 5
    
    log_info "YARN services started successfully"
}

# Stop HDFS services
stop_hdfs() {
    log_section "Stopping HDFS Services"
    
    log_info "Stopping DataNodes..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/hadoop-daemons.sh stop datanode
    
    log_info "Stopping Secondary NameNode..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/hadoop-daemon.sh stop secondarynamenode
    
    log_info "Stopping NameNode..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/hadoop-daemon.sh stop namenode
    
    log_info "HDFS services stopped successfully"
}

# Stop YARN services
stop_yarn() {
    log_section "Stopping YARN Services"
    
    log_info "Stopping Job History Server..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/mr-jobhistory-daemon.sh stop historyserver
    
    log_info "Stopping NodeManagers..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/yarn-daemons.sh stop nodemanager
    
    log_info "Stopping ResourceManager..."
    sudo -u $HADOOP_USER $HADOOP_HOME/sbin/yarn-daemon.sh stop resourcemanager
    
    log_info "YARN services stopped successfully"
}

# Check cluster status
check_status() {
    log_section "Checking Cluster Status"
    
    log_info "Java processes running as $HADOOP_USER:"
    sudo -u $HADOOP_USER jps
    
    echo ""
    log_info "HDFS report:"
    sudo -u $HADOOP_USER $HADOOP_HOME/bin/hdfs dfsadmin -report
    
    echo ""
    log_info "YARN node status:"
    sudo -u $HADOOP_USER $HADOOP_HOME/bin/yarn node -list
}

# Create HDFS directories
create_hdfs_directories() {
    log_section "Creating HDFS Directories"
    
    log_info "Creating user directories in HDFS..."
    sudo -u $HADOOP_USER $HADOOP_HOME/bin/hdfs dfs -mkdir -p /user
    sudo -u $HADOOP_USER $HADOOP_HOME/bin/hdfs dfs -mkdir -p /user/$HADOOP_USER
    sudo -u $HADOOP_USER $HADOOP_HOME/bin/hdfs dfs -mkdir -p /tmp
    sudo -u $HADOOP_USER $HADOOP_HOME/bin/hdfs dfs -chmod 777 /tmp
    
    log_info "HDFS directories created successfully"
}

# Test cluster functionality
test_cluster() {
    log_section "Testing Cluster Functionality"
    
    log_info "Running HDFS test..."
    # Create test file
    echo "Hello Hadoop Cluster!" > /tmp/test.txt
    
    # Put file into HDFS
    sudo -u $HADOOP_USER $HADOOP_HOME/bin/hdfs dfs -put /tmp/test.txt /user/$HADOOP_USER/
    
    # List files
    sudo -u $HADOOP_USER $HADOOP_HOME/bin/hdfs dfs -ls /user/$HADOOP_USER/
    
    # Get file back
    sudo -u $HADOOP_USER $HADOOP_HOME/bin/hdfs dfs -get /user/$HADOOP_USER/test.txt /tmp/test_from_hdfs.txt
    
    # Compare files
    if diff /tmp/test.txt /tmp/test_from_hdfs.txt; then
        log_info "HDFS test passed successfully"
    else
        log_error "HDFS test failed"
        return 1
    fi
    
    # Clean up
    sudo -u $HADOOP_USER $HADOOP_HOME/bin/hdfs dfs -rm /user/$HADOOP_USER/test.txt
    rm -f /tmp/test.txt /tmp/test_from_hdfs.txt
    
    log_info "Running MapReduce test..."
    # Run a simple MapReduce example
    sudo -u $HADOOP_USER $HADOOP_HOME/bin/hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar pi 2 10
    
    log_info "Cluster test completed successfully"
}

# Display web interfaces
show_web_interfaces() {
    log_section "Web Interfaces"
    
    echo "Access the following web interfaces:"
    echo "• NameNode Web UI: http://$(hostname -I | awk '{print $1}'):9870"
    echo "• ResourceManager Web UI: http://$(hostname -I | awk '{print $1}'):8088"
    echo "• Job History Server: http://$(hostname -I | awk '{print $1}'):19888"
    echo "• DataNode Web UI: http://$(hostname -I | awk '{print $1}'):9864"
}

# Main function
usage() {
    echo "Usage: $0 {start|stop|restart|status|test|format}"
    echo ""
    echo "Commands:"
    echo "  start    - Start the Hadoop cluster"
    echo "  stop     - Stop the Hadoop cluster"
    echo "  restart  - Restart the Hadoop cluster"
    echo "  status   - Check cluster status"
    echo "  test     - Test cluster functionality"
    echo "  format   - Format HDFS (WARNING: This will delete all data)"
    exit 1
}

case "$1" in
    start)
        log_info "Starting Hadoop cluster..."
        check_hdfs_format
        start_hdfs
        create_hdfs_directories
        start_yarn
        show_web_interfaces
        log_info "Hadoop cluster started successfully!"
        ;;
    stop)
        log_info "Stopping Hadoop cluster..."
        stop_yarn
        stop_hdfs
        log_info "Hadoop cluster stopped successfully!"
        ;;
    restart)
        log_info "Restarting Hadoop cluster..."
        stop_yarn
        stop_hdfs
        sleep 5
        start_hdfs
        start_yarn
        show_web_interfaces
        log_info "Hadoop cluster restarted successfully!"
        ;;
    status)
        check_status
        show_web_interfaces
        ;;
    test)
        test_cluster
        ;;
    format)
        log_warn "WARNING: This will format HDFS and delete all data!"
        read -p "Are you sure? (yes/no): " confirm
        if [[ $confirm == "yes" ]]; then
            stop_yarn
            stop_hdfs
            sudo -u $HADOOP_USER rm -rf $HADOOP_HOME/hdfs/namenode/*
            sudo -u $HADOOP_USER rm -rf $HADOOP_HOME/hdfs/datanode/*
            sudo -u $HADOOP_USER $HADOOP_HOME/bin/hdfs namenode -format
            log_info "HDFS formatted successfully"
        else
            log_info "Format cancelled"
        fi
        ;;
    *)
        usage
        ;;
esac