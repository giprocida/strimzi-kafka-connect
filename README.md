## Project Overview ##



This project demonstrates how to deploy `Debezium` and `Kafka` on Kubernetes using Minikube.
Before we start, let's first highlight some key differences between Kubernetes running on Docker Desktop and Kubernetes running on Minikube.

## Prerequisites ##


* Docker Desktop installed and Kubernetes enabled.
* Minikube installed.
* kubectl installed and configured to interact with both environments.

###  Minikube vs. Docker Desktop ###


#### Minikube ####
Minikube is designed to run a local Kubernetes cluster on your machine for development and testing. It creates a VM (or uses a container) to run the Kubernetes cluster, and this VM/container runs its own Docker daemon, isolated from your host machine’s Docker daemon. You start Minikube using a command, choosing a VM driver (like VirtualBox) or a container driver (like Docker). For example, you might use minikube start.

In terms of networking, the Minikube VM/container has its own network configuration. Services are not accessible from localhost by default; you need to use commands like minikube service to access them or find the Minikube IP and NodePort. For example, you can access a service using `minikube service service-name`. Take a look at the [Minikube documentation](https://minikube.sigs.k8s.io/docs/handbook/accessing/) for more insights.  To use Docker images with Minikube, you need to build them inside Minikube’s Docker environment by pointing your shell to Minikube’s Docker daemon, using a command like eval $(minikube docker-env). Take a look at the [Minikube documentation](https://minikube.sigs.k8s.io/docs/tutorials/docker_desktop_replacement/#steps) for more insights.

Minikube offers flexibility and is closer to production setups but requires manual configuration for network access and image management.


#### Kubernetes on Docker Desktop ####

Docker Desktop integrates Kubernetes to provide an easy-to-use local Kubernetes environment for development. It runs a lightweight VM to host the Docker daemon and Kubernetes components, and both Docker and Kubernetes share the same Docker daemon, simplifying image management. Kubernetes can be enabled through Docker Desktop settings with a simple toggle, and the Kubernetes components are managed within the same VM used by Docker.

In terms of networking, Docker Desktop provides seamless network integration, making services accessible via localhost and the host’s IP address. For example, you can access a service using `curl http://localhost:NodePort.` Docker images built on your host machine are immediately available to the Kubernetes cluster without additional configuration, and you can build an image using a command like `docker build -t my-image:latest .`.

Docker Desktop simplifies development with a unified Docker and Kubernetes environment, providing seamless network access and a shared Docker daemon.



## Deploying Debezium on Minikube ##
This guide complements the official Debezium documentation by highlighting key steps and providing additional resources to help you avoid common issues. Follow the [Debezium documentation](https://debezium.io/documentation/reference/stable/operations/kubernetes.html) as the primary source for deploying Debezium on Minikube.


Kubernetes files to deploy:

1. A Secret called `debezium-secret` containing base64-encoded credentials for connecting to the MySQL database.

2. A Role called `connector-configuration-role` which grants read access to a specific Kubernetes Secret named `debezium-secret` within the `debezium-example` namespace.

3. A RoleBinding called `connector-configuration-role-binding` which binds the Role to the Kafka Connect cluster service account.

4. A Deployment called `mysql` for deploying a MySQL database specified in the `mysql-deployment.yaml` file

5. A service called `mysql` specified in the `mysql-deployment.file`


Custom Resources using Strimzi Kafka CRD:

1. Kafka which deploys the Kafka cluster (`debezium-cluster.yaml`)

2. KafkaConnect which deploys the Kafka Connect cluster with the necessary plugins (`debezium-connect-cluster-custombuild.yaml`)

3. KafkaConnector which configures the connector for capturing changes from MySQL and streaming them to Kafka (`debezium-connector.yaml`)


#### Important Notes ####
**Issue with KafkaConnect configuration**: When applying the configuration file from the [Debezium documentation](https://debezium.io/documentation/reference/stable/operations/kubernetes.html), you may encounter issues with the version field specified in the YAML file. To resolve this, update the version from 3.1.0 to 3.7.1, or alternatively, use the `debezium-connect-cluster.yaml` file directly.

**Issue with Shell Commands**: When creating the KafkaConnector using shell commands as suggested in the tutorial, you may encounter issues with reading database credentials. It is recommended to store the YAML configuration in a file and apply it using kubectl apply -f ..... For more information, refer to this Stack Overflow post for troubleshooting [KafkaConnector not reading database credentials](https://stackoverflow.com/questions/75831703/strimzi-kafkaconnector-not-reading-database-credentials-from-secrets).


**Why two debezium-connect-cluster files?**: 

* `debezium-connect-cluster-custombuild.yaml`: Indicates that the configuration involves a custom build process and includes plugins.
* `debezium-connect-cluster-prebuiltimage.yaml`: Indicates that the configuration uses a pre-built image without additional build steps or plugins.









### Understanding the Interplay of ServiceAccounts, Roles, and RoleBindings ###
This section provides a practical understanding of Kubernetes resources, specifically `ServiceAccount`, `Role`, and `RoleBinding`. We will create three Kubernetes resources to demonstrate their usage:

* RoleBinding: Grants the necessary permissions to the ServiceAccount.
* Role: Defines the permissions for accessing resources.
* Pod: Utilizes the ServiceAccount to operate within the defined permissions.

Follow the steps below to learn more:

#### Configuring Minikube's Docker Daemon and Managing Docker Images ####


1. Configure your shell to use Minikube's Docker daemon. 
Minikube has its own Docker daemon. To build Docker images directly within Minikube, you need to point your shell to 
Minikube's Docker daemon.
Check the Docker environment for Minikube:
```
minikube docker-env
```
Point your shell to minikube's docker-daemon, run:
```
eval $(minikube docker-env)
```
To make sure that your Docker CLI is now configured to use the Docker daemon inside your Minikube environment, run:
```
docker info | grep -i "name:"
```
If the command returns `Name: minikube`, it confirms that the Docker daemon is running inside the Minikube VM.


2. Build your Docker image. Navigate go to the directory containing your Dockerfile named `app-printer` and build your image:

```
docker build -t gprocida6g/printer:1.0 .
```

3. Verify the Docker Image. After building the image, verify that it was built inside your Minikube environment by listing the images:

```
docker images
```
You should see `gprocida6g/objects-printer:1.0` in the list of images.


If you wish to delete a Docker image, you can use the following command:

```
docker rmi <image-name> or <image-id>
```

For example, to delete the image `gprocida6g/objects-printer:1.0`, you can run:

```
docker rmi gprocida6g/objects-printer:1.0
```


**Create a Role Resource**

Use an imperative command:

```
kubectl create role pod-listing-role \
  --verb=get,list \
  --resource=pods,secrets \
  --namespace=kafka \
  --dry-run=client -o yaml > my-role.yaml
```

Or just use the provided `my-role.yaml` file. <br />
The Role defined in the `my-role.yaml` file grants permissions to perform get and list operations on the pods and secrets resources within the `debezium-example` namespace. This means any ServiceAccount, User, or Group that this Role is bound to can view and list the pods and secrets in that namespace.

Apply the Role:
```
kubectl apply -f my-role.yaml
```


**Create a Rolebinding resource**

Use an imperative command:

```
kubectl create rolebinding pod-listing-binding \
  --role=pod-listing-role \
  --serviceaccount=kafka:default \
  --dry-run=client \
  --namespace=kafka \
  -o yaml > my-role-binding.yaml
```

or just use the provided `my-role-binding.yaml` file. <br />
The RoleBinding defined in the file `my-role-binding.yaml` grants the permissions defined in the `pod-listing-role` Role to the default ServiceAccount in the debezium-example namespace. This means that the default ServiceAccount in the debezium-example namespace will have the permissions to get and list pods and secrets within that namespace. 

Apply the RoleBinding:
```
kubectl apply -f my-role-binding.yaml
```


**Create the pod**

Create a pod named `debug-pod` that uses the gprocida6g/printer:1.0 image and is set to be created in the `debezium-example` namespace:

```
kubectl run debug-pod \
  --image=gprocida6g/printer:1.0 \
  --namespace=debezium-example \
  --dry-run=client -o yaml > printer.yaml
```


Now, modify the deployment configuration by adding `imagePullPolicy: Never` that will instruct the kubelet to never pull the container image from the registry. This means that Kubernetes will only use the image if it is already present on the node where the pod is scheduled. 

Apply the pod:

```
kubectl apply -f printer.yaml
```

Now, log into the pod and check the output. You will see all the secrets belonging to the debezium-example namespace printed out, along with all the containers for each pod.




