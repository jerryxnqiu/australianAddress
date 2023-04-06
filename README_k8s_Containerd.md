## Setup Kubernetes Cluster with 2 nodes on GCP Compute Engine, using Containerd runtime
#### Thanks to https://www.youtube.com/watch?v=z_w3me8tmJA&t=281s
---
### 1. Install containerd runtime (All nodes)
https://github.com/containerd/containerd/blob/main/docs/getting-started.md

- Containerd - Option 1: From the official binaries
    - https://github.com/containerd/containerd/releases
    ```sh
    # Check and change the static hostname
    hostnamectl status
    sudo hostnamectl set-hostname k8s-master


    # Disable SWAP
    sudo swapoff -a
    sudo sed -i '/ swap /s/^\(.*\)$/#\1/g' /etc/fstab # No impact on debian OS

    # Install Containerd
    sudo apt-get install wget
    wget https://github.com/containerd/containerd/releases/download/v1.7.0/containerd-1.7.0-linux-amd64.tar.gz
    
    sudo tar Cxzvf /usr/local containerd-1.7.0-linux-amd64.tar.gz

    # Download service file
    wget https://raw.githubusercontent.com/containerd/containerd/main/containerd.service

    sudo mkdir -p /usr/local/lib/systemd/system

    sudo mv containerd.service /usr/local/lib/systemd/system/containerd.service

    sudo systemctl daemon-reload
    sudo systemctl enable --now containerd
    ```

- Install runc
    ```sh
    wget https://github.com/opencontainers/runc/releases/download/v1.1.5/runc.amd64

    sudo install -m 755 runc.amd64 /usr/local/sbin/runc

    sudo runc # To see details of runc
    ```

- Install CNI plugins
    ```sh
    wget https://github.com/containernetworking/plugins/releases/download/v1.2.0/cni-plugins-linux-amd64-v1.2.0.tgz

    sudo mkdir -p /opt/cni/bin

    sudo tar Cxzvf /opt/cni/bin cni-plugins-linux-amd64-v1.2.0.tgz
    ```

- Install crictl
    ```sh
    VERSION="v1.26.0" # Check latest version in /releases page
    
    wget https://github.com/kubernetes-sigs/cri-tools/releases/download/$VERSION/crictl-$VERSION-linux-amd64.tar.gz
    
    sudo tar zxvf crictl-$VERSION-linux-amd64.tar.gz -C /usr/local/bin
    
    rm -f crictl-$VERSION-linux-amd64.tar.gz

    sudo crictl # To check details of crictl

    cat <<EOF | sudo tee /etc/crictl.yaml 
    runtime-endpoint: unix:///run/containerd/containerd.sock
    image-endpoint: unix:///run/containerd/containerd.sock
    timeout: 2
    debug: true
    pull-image-on-create: false
    EOF

    sudo crictl ps
    sudo crictl image
    sudo crictl pull nginx 
    ```

### 2. Configure the forwarding IPv4 and letting iptables see bridged traffic
- https://kubernetes.io/docs/setup/production-environment/container-runtimes/#forwarding-ipv4-and-letting-iptables-see-bridged-traffic
    ```sh
    cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
    overlay
    br_netfilter
    EOF

    # To load
    sudo modprobe overlay
    sudo modprobe br_netfilter

    # sysctl params required by setup, params persist across reboots
    cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
    net.bridge.bridge-nf-call-iptables  = 1
    net.bridge.bridge-nf-call-ip6tables = 1
    net.ipv4.ip_forward                 = 1
    EOF

    # Apply sysctl params without reboot
    sudo sysctl --system

    # Verify that the br_netfilter, overlay modules are loaded by running below instructions
    lsmod | grep br_netfilter
    lsmod | grep overlay

    # Verify that the net.bridge.bridge-nf-call-iptables, net.bridge.bridge-nf-call-ip6tables, net.ipv4.ip_forward system variables are set to 1 in your sysctl config by running below instruction
    sudo sysctl net.bridge.bridge-nf-call-iptables net.bridge.bridge-nf-call-ip6tables net.ipv4.ip_forward

    sudo modprobe br_netfilter

    sudo sysctl -p /etc/sysctl.conf
    ```

### 3. Installing kubeadm, kubelet and kubectl
- https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#installing-kubeadm-kubelet-and-kubectl
    ```sh
    # Update the apt package index and install packages needed to use the Kubernetes apt repository:
    sudo apt-get update

    sudo apt-get install -y apt-transport-https ca-certificates curl

    # Download the Google Cloud public signing key
    sudo mkdir -p /etc/apt/keyrings
    sudo curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg

    # Add the Kubernetes apt repository:
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

    # Update apt package index, install kubelet, kubeadm and kubectl, and pin their version
    sudo apt-get update
    sudo apt-get install -y kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl
    ```

### 4. Creating a cluster with kubeadm (Only on master node)
    ```sh
    sudo kubeadm config images pull

    sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --cri-socket=unix:///var/run/containerd/containerd.sock --apiserver-advertise-address=<master node IP>10.128.0.33
    ```

    - When the above is successful, below will show up and need to be executed:
    ```sh
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    ```

### 7. Troubleshooting commands


### 8. Join the non-master node to master node

