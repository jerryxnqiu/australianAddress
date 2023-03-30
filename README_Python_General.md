# **General Python Script -> Docker Image -> Google Cloud Registry -> Kubernetes Pods/Containers**

## **1. Setup gcloud environement**
### **1.1 
- kubectl create namespace localdev
- kubectl create secret docker-registry gcr-json-key \
                        --docker-server=eu.gcr.io \
                        --docker-username=_json_key \
                        --docker-password="$(cat ~/json-key-file.json)" \
                        --docker-email=any@valid.email
- Thanks to **"https://blog.container-solutions.com/using-google-container-registry-with-kubernetes"**

### **1.2 Initial Setup**
- sudo /Users/$USER/Downloads/google-cloud-sdk/install.sh
- sudo /Users/$USER/Downloads/google-cloud-sdk/bin/gcloud init
- export PATH=$PATH:/Users/$USER/Downloads/google-cloud-sdk/bin


### **1.3 Below command might need to run whenever start the terminal**
- sudo gcloud auth configure-docker

## **2. Create Docker Image and push to GCR**
### **2.1 Build Image**
- docker image build --pull \
                     --file '/Users/$USER/Desktop/<Docker Image Name>/Dockerfile' \
                     --tag '<Docker Image Name>:latest' \
                     --label 'com.microsoft.created-by=visual-studio-code' '/Users/$USER/Desktop/<Docker Image Name>' \
                     --platform linux/amd64

- If image create platform does not match the deployment platform, error like "The requested image's platform (linux/arm64/v8) does not match the detected host platform (linux/amd64/v4) and no specific platform was requested" might occur. Need to add **"-platform linux/amd64"** to the docker image build command or do **"export DOCKER_DEFAULT_PLATFORM=linux/amd64"**

### **2.2 Tag the Image with GCR location**
- docker tag <Docker Image Name> gcr.io/<gcp-project-ID>/<Docker Image Name>

### **2.3 sudo is required to perform root level execution to push image to GCR**
- sudo docker push gcr.io/<gcp-project-ID>/<Docker Image Name>

## **3. Create secret service key to docker-registry in GCP**

- kubectl create secret docker-registry gcr-json-key \
          --docker-server=gcr.io \
          --docker-username=_json_key \
          --docker-password="$(cat ~/<Project ID and Key>.json)"

- kubectl patch serviceaccount default \
          -p '{"imagePullSecrets": [{"name": "gcr-json-key"}]}'

## **4. After first deployment, if fail for below, need to change the folder owner and priviledge**
- sudo chown "$USER":"$USER" /Users/$USER/.docker -R
- sudo chmod -R g+rwx /Users/$USER/.docker

## **5. Command to apply the deploment yaml file**
- kubectl apply -f deployment.yaml

## **6. Commands to check deployment performacne and issues**

### **6.1 To run from a bash session
- kubectl exec -i -t mycontainer /bin/bash

### **6.2 Getting details about Init Containers**
- kubectl describe pod <pod-name>
- kubectl exec -it <pod-name> -- /bin/bash
- kubectl logs <pod-name> <container-name>
- kubectl logs -f deploy/ -n
