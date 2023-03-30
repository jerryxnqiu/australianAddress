# To create MySQL persistent volmne in Kubernetes
## Thanks to **"https://www.youtube.com/watch?v=PeQo8fOZ_J4&t=18s"**
### 1. Need to create secret as per the task
- kubectl create secret generic mysql-root-pass \
                        --from-literal='password=mysql'

- kubectl create secret generic mysql-user-pass \
                        --from-literal='username=mysql'\
                        --from-literal='password=mysql'
- kubectl create secret generic mysql-db-url \
                        --from-literal='database=mysql_db01'

- kubectl get secret

### 2. Create a PersistentVolume **mysql-pv**, its capacity should be **xxxMi** or **xxxGi**, set other parameters as per preference, **hostPath.path** to select the location kubectl create the file location

```yaml
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysql-pv
spec:
  storageClassName: manual
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteOnce
  hostPath:
    path: "/var/lib/mysql"
```

### 3. Createa a **PersistentVolumeClaim** to request to use this **PersistentVolume** storage. Name it as **mysql-pv-claim** and request a **xxxMi** of storage. Set other parameters as per your preference.

```yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pv-claim
spec:
  storageClassName: manual
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### 4. Create a **NodePort** type service named mysql and set nodePort to 30007, for public access

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  type: NodePort
  selector:
    app: mysql
  ports:
    - port: 3306
      targetPort: 3306
      nodePort: 30007
```


### 5. Create a deployment name **mysql-deployment**, for app **mysql**, set up env **MYSQL_ROOT_PASSWORD**, **mMYSQL_DATABASE**, **MYSQL_USER**, mount the volume to **/var/lib/mysql** and define the port as **containerPort: 3306** with name **name: mysql**

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-deployment
  labels:
    app: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      volumes:
      - name: mysql-pv
        persistentVolumeClaim:
          claimName: mysql-pv-claim
      containers:
      - name: mysql
        image: mysql:latest
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-root-pass
              key: password
        - name: MYSQL_DATABASE
          valueFrom:
            secretKeyRef:
              name: mysql-db-url
              key: database
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: mysql-user-pass
              key: username
        volumeMounts:
        - name: mysql-pv
          mountPath: /var/lib/mysql
        ports:
        - containerPort: 3306
          name: mysql

```

### 6. After the pod for mysql is running, can use below to access mysql shell and check if mysql is up and running
- kubectl exec -it <mysql-pod-name> -- /bin/bash
- printenv

### 7. Login MySQL and change from JS mode to SQL mode (\sql) if required **https://dev.mysql.com/doc/mysql-operator/en/mysql-operator-connecting-mysql-shell.html**
- mysql -u root -p 