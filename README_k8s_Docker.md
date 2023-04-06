## Setup Kubernetes Cluster with 2 nodes on GCP Compute Engine, using Docker runtime
#### Thanks to https://www.youtube.com/watch?v=o6bxo0Oeg6o&t=429s and https://www.youtube.com/watch?v=Ro2qeYeisZQ
---
### 1. Install Docker Engine
- https://kubernetes.io/docs/setup/production-environment/container-runtimes/#docker
- Install using the repository (all nodes)
    - https://docs.docker.com/engine/install/debian/#install-using-the-repository
    ```sh
    sudo apt-get update
    sudo apt-get install ca-certificates curl gnupg
    sudo mkdir -m 0755 -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```

- Install Docker Engine
    ```sh
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```
- If want to install older version
    ```sh
    apt-cache madison docker-ce | awk '{ print $3 }'
    VERSION_STRING=5:20.10.23~3-0~debian-bullseye
    sudo apt-get install docker-ce=$VERSION_STRING docker-ce-cli=$VERSION_STRING containerd.io docker-buildx-plugin docker-compose-plugin

    # to check if docker runtime is runing
    sudo docker run hello-world
    ```
- Set the cgroupdriver to systemd if not yet done
    ```sh
    cat <<EOF | sudo tee /etc/docker/daemon.json
    {
        "exec-opts": ["native.cgroupdriver=systemd"],
        "log-driver": "json-file",
        "log-opts": {
            "max-size": "100m"
        },
        "storage-driver": "overlay2"
    }
    EOF
    ```
---
### 2. To disable the swap
-
    ```sh
    sudo swapoff -a
    ```
---
### 3. Configure the forwarding IPv4 and letting iptables see bridged traffic
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
    ```
---
### 4. Install cri-dockerd for Docker
- https://github.com/Mirantis/cri-dockerd#to-use-with-kubernetes
    ```sh
    git clone https://github.com/Mirantis/cri-dockerd.git
    sudo apt-get install wget

    # Run these commands as root
    ###Install GO###
    wget https://storage.googleapis.com/golang/getgo/installer_linux
    chmod +x ./installer_linux
    ./installer_linux
    source ~/.bash_profile

    cd cri-dockerd
    mkdir bin
    go build -o bin/cri-dockerd
    mkdir -p /usr/local/bin
    sudo install -o root -g root -m 0755 bin/cri-dockerd /usr/local/bin/cri-dockerd
    sudo cp -a packaging/systemd/* /etc/systemd/system
    sudo sed -i -e 's,/usr/bin/cri-dockerd,/usr/local/bin/cri-dockerd,' /etc/systemd/system/cri-docker.service

    sudo systemctl daemon-reload
    sudo systemctl enable cri-docker.service
    sudo systemctl enable --now cri-docker.socket
    ```
- Regarding Cgroup drivers for Docker Engine (Ignore if runtime is Docker)

    - Note: These instructions assume that you are using the cri-dockerd adapter to integrate Docker Engine with Kubernetes.
    - On each of your nodes, install Docker for your Linux distribution as per Install Docker Engine.
    - Install cri-dockerd, following the instructions in that source code repository.
    - For cri-dockerd, the CRI socket is /run/cri-dockerd.sock by default.
---
### 5. Installing kubeadm, kubelet and kubectl
- https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#installing-kubeadm-kubelet-and-kubectl
    ```sh
    #Update the apt package index and install packages needed to use the Kubernetes apt repository:
    sudo apt-get update

    sudo apt-get install -y apt-transport-https ca-certificates curl

    #Download the Google Cloud public signing key
    sudo curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg

    # Add the Kubernetes apt repository
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

    #Update apt package index, install kubelet, kubeadm and kubectl, and pin their version
    sudo apt-get update
    sudo apt-get install -y kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl
    ```
---
### 6. Creating a cluster with kubeadm (Only on master node)
- https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/
    ```sh
    sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --cri-socket=unix:///var/run/cri-dockerd.sock --apiserver-advertise-address=<master node IP>10.128.0.14

    sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock

    ip addr # To find out the master node IP
    ```
- When the above is successful, below will show up and need to be executed:
    ```sh
    - mkdir -p $HOME/.kube
    - sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    - sudo chown $(id -u):$(id -g) $HOME/.kube/config
    ```
---
### 7. Install Network Plugin (Only on master node)
- https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises
- Download the Calico networking manifest for the Kubernetes API datastore.
    ```sh
    curl https://raw.githubusercontent.com/projectcalico/calico/v3.25.1/manifests/calico.yaml -O
    ```
- Apply the manifest using the following command.
    ```sh
    kubectl apply -f calico.yaml
    ```
---
### 8. Join the non-master node to master node
- After the below, kubectl get nodes, should see the addition nodes
    ```sh
    sudo kubeadm join <control-plane-host>:<control-plane-port> --token <token> --discovery-token-ca-cert-hash sha256:<hash>
    ```


