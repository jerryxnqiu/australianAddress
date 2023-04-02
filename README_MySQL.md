## To create MySQL persistent volmne in Kubernetes
### Thanks to **"https://www.youtube.com/watch?v=PeQo8fOZ_J4&t=18s"**
#### 1. To create secret as per the task
```sh
- kubectl create secret generic mysql-root-pass \
                        --from-literal='password=mysql'

- kubectl create secret generic mysql-user-pass \
                        --from-literal='username=mysql'\
                        --from-literal='password=mysql'
- kubectl create secret generic mysql-db-url \
                        --from-literal='database=mysql_db01'

- kubectl get secret
```
---
#### 2. Create a PersistentVolume **mysql-pv**, its capacity should be **xxxMi** or **xxxGi**, set other parameters as per preference, **hostPath.path** to select the location kubectl create the file location
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
---
#### 3. Createa a **PersistentVolumeClaim** to request to use this **PersistentVolume** storage. Name it as **mysql-pv-claim** and request a **xxxMi** of storage. Set other parameters as per your preference.
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
---
#### 4. Create a **NodePort** type service named mysql and set nodePort to 30007, for public access
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
---
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
---
### 6. After the pod for mysql is running, can use below to access mysql bash command line, to check if mysql is up and running and do command line actions
```sh
kubectl exec -it <mysql-pod-name> -- /bin/bash
printenv
```
---
### 7. Login MySQL and change from JS mode to SQL mode (\sql) if required **https://dev.mysql.com/doc/mysql-operator/en/mysql-operator-connecting-mysql-shell.html**
```sql
mysql -u root -p 

CREATE TABLE IF NOT EXISTS ADDRESS_DETAIL_psv (
    ADDRESS_DETAIL_PID VARCHAR(256) NOT NULL PRIMARY KEY,
    DATE_CREATED DATE,
    DATE_LAST_MODIFIED DATE,
    DATE_RETIRED DATE,
    BUILDING_NAME VARCHAR(256),
    LOT_NUMBER_PREFIX CHAR(4),
    LOT_NUMBER CHAR(4),
    LOT_NUMBER_SUFFIX CHAR(4),
    FLAT_TYPE_CODE CHAR(4),
    FLAT_NUMBER_PREFIX CHAR(4),
    FLAT_NUMBER CHAR(4),
    FLAT_NUMBER_SUFFIX CHAR(4),
    LEVEL_TYPE_CODE CHAR(4),
    LEVEL_NUMBER_PREFIX CHAR(4),
    LEVEL_NUMBER CHAR(4),
    LEVEL_NUMBER_SUFFIX CHAR(4),
    NUMBER_FIRST_PREFIX CHAR(4),
    NUMBER_FIRST CHAR(4),
    NUMBER_FIRST_SUFFIX CHAR(4),
    NUMBER_LAST_PREFIX CHAR(4),
    NUMBER_LAST CHAR(4),
    NUMBER_LAST_SUFFIX CHAR(4),
    STREET_LOCALITY_PID CHAR(4),
    LOCATION_DESCRIPTION CHAR(4),
    LOCALITY_PID CHAR(4),
    ALIAS_PRINCIPAL CHAR(4),
    POSTCODE CHAR(4),
    PRIVATE_STREET CHAR(4),
    LEGAL_PARCEL_ID CHAR(4),
    CONFIDENCE CHAR(4),
    ADDRESS_SITE_PID CHAR(4),
    LEVEL_GEOCODED_CODE CHAR(4),
    PROPERTY_PID CHAR(4),
    GNAF_PROPERTY_PID CHAR(4),
    PRIMARY_SECONDARY CHAR(6)
);

LOAD DATA INFILE '/var/lib/mysql-files/ACT_ADDRESS_DETAIL_psv.psv' INTO TABLE ADDRESS_DETAIL_psv IGNORE 1 LINES;
SHOW COLUMNS FROM ADDRESS_DETAIL_psv;
DROP TABLE ADDRESS_DETAIL_psv;
```