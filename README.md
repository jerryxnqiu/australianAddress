# **General Python Script -> Docker Image -> Google Cloud Registry -> Kubernetes Pods/Containers**

## **1. Setup gcloud environement**
### **1.1 Initial Setup**
- sudo /Users/jerryqiu/Downloads/google-cloud-sdk/install.sh
- sudo /Users/jerryqiu/Downloads/google-cloud-sdk/bin/gcloud init
- export PATH=$PATH:/Users/jerryqiu/Downloads/google-cloud-sdk/bin

### **1.2 Below command might need to run whenever start the terminal**
- sudo gcloud auth configure-docker

## **2. Create Docker Image and push to GCR**
### **2.1 Build Image**
- docker image build --pull \
                     --file '/Users/jerryqiu/Desktop/australianAddress/Dockerfile' \
                     --tag 'australianaddress:latest' \
                     --label 'com.microsoft.created-by=visual-studio-code' '/Users/jerryqiu/Desktop/australianAddress' \
                     --platform linux/amd64

- **-platform linux/amd64** is to solve "The requested image's platform (linux/arm64/v8) does not match the detected host platform (linux/amd64/v4) and no specific platform was requested" or do **export DOCKER_DEFAULT_PLATFORM=linux/amd64**

### **2.2 Tag the Image with GCR location**
- docker tag australianaddress gcr.io/datacollection-379709/australianaddress

### **2.3 sudo is required to perform root level execution to push image to GCR**
- sudo docker push gcr.io/datacollection-379709/australianaddress

## **3. Create secret service key to docker-registry in GCP**

- kubectl create secret docker-registry gcr-json-key \
          --docker-server=gcr.io \
          --docker-username=_json_key \
          --docker-password="$(cat ~/datacollection-379709-7a25852c478f.json)"

- kubectl patch serviceaccount default \
          -p '{"imagePullSecrets": [{"name": "gcr-json-key"}]}'

## **4. After first deployment, if fail for below, need to change the folder owner and priviledge**
- sudo chown "jerryqiu":"jerryqiu" /Users/jerryqiu/.docker -R
- sudo chmod -R g+rwx /Users/jerryqiu/.docker

## **5. Command to apply the deploment yaml file**
- kubectl apply -f gnaf_deployment.yaml

## **6. Commands to check deployment performacne and issues**

### **6.1 Getting details about Init Containers**
- kubectl describe pod <pod-name>
- kubectl exec -it <pod-name> -- /bin/bash
- kubectl logs <pod-name> <container-name>
- kubectl logs -f deploy/ -n
