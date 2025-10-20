#!/bin/bash

# Hadoop Cluster Installation Script
# Installs and configures Hadoop on all nodes

set -e  # Exit on any error

# Configuration variables
HADOOP_VERSION="3.3.6"
JAVA_VERSION="8"
HADOOP_USER="hadoop"
HADOOP_HOME="/opt/hadoop"
JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Install Java if not present
install_java() {
    log_info "Installing Java OpenJDK $JAVA_VERSION..."
    
    if command -v java &> /dev/null; then
        log_warn "Java is already installed"
        java -version
    else
        apt-get update
        apt-get install -y openjdk-$JAVA_VERSION-jdk
        
        # Set JAVA_HOME in environment
        echo "export JAVA_HOME=$JAVA_HOME" >> /etc/environment
        echo "export PATH=\$PATH:\$JAVA_HOME/bin" >> /etc/environment
    fi
}

# Create hadoop user
create_hadoop_user() {
    log_info "Creating Hadoop user..."
    
    if id "$HADOOP_USER" &>/dev/null; then
        log_warn "User $HADOOP_USER already exists"
    else
        useradd -m -s /bin/bash $HADOOP_USER
        usermod -aG sudo $HADOOP_USER
        log_info "Created user: $HADOOP_USER"
    fi
}

# Download and install Hadoop
install_hadoop() {
    log_info "Installing Hadoop $HADOOP_VERSION..."
    
    # Create Hadoop directory
    mkdir -p $HADOOP_HOME
    cd /tmp
    
    # Download Hadoop if not already present
    HADOOP_ARCHIVE="hadoop-$HADOOP_VERSION.tar.gz"
    if [[ ! -f $HADOOP_ARCHIVE ]]; then
        log_info "Downloading Hadoop $HADOOP_VERSION..."
        wget "https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/$HADOOP_ARCHIVE"
    fi
    
    # Extract Hadoop
    log_info "Extracting Hadoop..."
    tar -xzf $HADOOP_ARCHIVE -C /opt/
    mv /opt/hadoop-$HADOOP_VERSION/* $HADOOP_HOME/
    rmdir /opt/hadoop-$HADOOP_VERSION
    
    # Set ownership
    chown -R $HADOOP_USER:$HADOOP_USER $HADOOP_HOME
    
    log_info "Hadoop installed successfully at $HADOOP_HOME"
}

# Setup SSH keys for passwordless access
setup_ssh_keys() {
    log_info "Setting up SSH keys for passwordless access..."
    
    # Switch to hadoop user for SSH setup
    sudo -u $HADOOP_USER bash << 'EOF'
        # Generate SSH key if it doesn't exist
        if [[ ! -f ~/.ssh/id_rsa ]]; then
            ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
        fi
        
        # Add public key to authorized_keys
        cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
        chmod 0600 ~/.ssh/authorized_keys
        
        echo "SSH keys configured for passwordless access"
EOF
}

# Configure environment variables
configure_environment() {
    log_info "Configuring environment variables..."
    
    # Create hadoop environment file
    cat > /etc/environment << EOF
export JAVA_HOME=$JAVA_HOME
export HADOOP_HOME=$HADOOP_HOME
export HADOOP_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export HADOOP_MAPRED_HOME=\$HADOOP_HOME
export HADOOP_COMMON_HOME=\$HADOOP_HOME
export HADOOP_HDFS_HOME=\$HADOOP_HOME
export YARN_HOME=\$HADOOP_HOME
export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$JAVA_HOME/bin
EOF
    
    # Update hadoop user's bashrc
    sudo -u $HADOOP_USER bash << EOF
        cat >> ~/.bashrc << 'BASHRC_EOF'

# Hadoop Environment Variables
export JAVA_HOME=$JAVA_HOME
export HADOOP_HOME=$HADOOP_HOME
export HADOOP_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export HADOOP_MAPRED_HOME=\$HADOOP_HOME
export HADOOP_COMMON_HOME=\$HADOOP_HOME
export HADOOP_HDFS_HOME=\$HADOOP_HOME
export YARN_HOME=\$HADOOP_HOME
export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$JAVA_HOME/bin
BASHRC_EOF
EOF

    # Set JAVA_HOME in hadoop-env.sh
    echo "export JAVA_HOME=$JAVA_HOME" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh
}

# Create necessary directories
create_directories() {
    log_info "Creating Hadoop directories..."
    
    sudo -u $HADOOP_USER bash << EOF
        # Create HDFS directories
        mkdir -p $HADOOP_HOME/hdfs/namenode
        mkdir -p $HADOOP_HOME/hdfs/datanode
        mkdir -p $HADOOP_HOME/hdfs/secondary
        
        # Create YARN directories
        mkdir -p $HADOOP_HOME/yarn/local
        mkdir -p $HADOOP_HOME/yarn/logs
        
        # Create temp directory
        mkdir -p $HADOOP_HOME/tmp
        
        echo "Hadoop directories created successfully"
EOF
}

# Install additional dependencies
install_dependencies() {
    log_info "Installing additional dependencies..."
    apt-get update
    apt-get install -y wget curl ssh rsync net-tools
}

# Main installation function
main() {
    log_info "Starting Hadoop installation..."
    
    check_root
    install_dependencies
    install_java
    create_hadoop_user
    install_hadoop
    setup_ssh_keys
    configure_environment
    create_directories
    
    log_info "Hadoop installation completed successfully!"
    log_info "Please reboot the system and then copy configuration files to $HADOOP_HOME/etc/hadoop/"
    log_info "After configuration, initialize HDFS with: sudo -u $HADOOP_USER hdfs namenode -format"
}

# Run main function
main "$@"