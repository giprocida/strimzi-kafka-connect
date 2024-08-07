from kubernetes import client, config
import os




def get_secret_pod_mapping(pod_list):
    """Create a mapping between secret names and the pods that use them 
    in a given list of pod.
    This function iterates through a list of Kubernets pods and extracts information 
    about the secrets each pod uses.
    
    Args:
        pod_list (Kubernetes obj): A list of Kubernetes pod objects.
         
    Returns:
        dict: A dictionary where keys are secret names and values are lists of pod 
             names that use the corresponding secret. """
    secretName_to_pod_mapping = {}
    for pod in pod_list.items:
        for container in pod.spec.containers:
            if container.env:
             for env_var in container.env:
                 if env_var.value_from and env_var.value_from.secret_key_ref:
                     secret_name = env_var.value_from.secret_key_ref.name
                     if secret_name in secretName_to_pod_mapping:
                        # Each pod uses the same secret for different configuration. To remove duplicates pod 
                        # check if the pod already exist in the secret_to_pod_mapping[secret_name] list
                        if pod.metadata.name not in secretName_to_pod_mapping[secret_name]:
                         secretName_to_pod_mapping[secret_name].append(pod.metadata.name)
                     else:
                         secretName_to_pod_mapping[secret_name] = [pod.metadata.name]
    return secretName_to_pod_mapping
        


def print_pods_and_containers(pod_list):
    """
    Print every container for each pod in the given list of pods.
    This function iterates through a list of Kubernetes pods and prints the name
    of each pod and its containers.
    
    Args:
        pod_list (Kubernetes obj): A list of Kubernetes pod objects.
    """
    for pod in pod_list.items:
        print(f"Pod: {pod.metadata.name}")
        for container in pod.spec.containers:
            print(f"  Container: {container.name}")



def get_secret_to_secretValue(secrets,secretName_to_pod_mapping):
    """
    Extracts secret values from Kubernetes secrets and categorizes them based on ownership.

    This function takes a list of Kubernetes secrets and a mapping of secret names to pods
    that use them. It categorizes the secrets into two dictionaries: one for secrets with
    no owner references and one for secrets with owner references.
    
    Args:
        secrets (Kubernetes obj): A list of Kubernetes secret obj
        secretName_to_pod_mapping (dict): A mapping of secret names to pods

    Returns:
        dict: A dictionary (secret_with_no
             owner_refences) where keys are secret names with no owner references, and values
              are lists of secret data.
    """

    secret_with_no_owner = {}

    secret_with_owner= {}

    for secret in secrets.items:
    
      secret_name = secret.metadata.name
      if secret.metadata.owner_references is None and secret_name in secretName_to_pod_mapping:
          if secret_name not in secret_with_no_owner:
              secret_with_no_owner[secret_name] = [secret.data]
          else:
              secret_with_no_owner[secret_name].append[secret.data]
      elif secret.metadata.owner_references is not None:# and secret_name in secret_to_pod_mapping:
            for ref in secret.metadata.owner_references:
              owner_name = ref.name
              if owner_name in secret_with_owner:
                  secret_with_owner[secret_name].append(secret.data)
              secret_with_owner[secret_name] = [secret.data]
    return secret_with_no_owner


def groupSecretsbyComponents(secret_with_no_owner):
    """
    Group and save secret data into component-specific directories.

    This function takes a dictionary where keys are component names and values are lists
    of secret data. It creates a directory structure under 'mycertificates' for each
    component and saves the secret data into files within their respective directories.

    Args:
        secret_with_no_owner (dict): A dictionary where keys are component names, and
            values are lists of secret data.
    """
    base_dir = "mycertificates"

    for component_name,cert_list in secret_with_no_owner.items():
        component_dir = os.path.join(base_dir,component_name)
        if not os.path.exists(component_dir):
            os.makedirs(component_dir)
            for key,val in cert_list[0].items():
                filepath = os.path.join(component_dir,key)

                with open(filepath,'w') as f:
                  f.write(val)

def print_all_secrets(secret_list):
    """
    Print all secrets in the given list of secrets.
    This function iterates through a list of Kubernetes secrets and prints the name
    of each secret.
    
    Args:
        secret_list (Kubernetes obj): A list of Kubernetes secret objects.
    """
    for secret in secret_list.items:
        print(f"Secret: {secret.metadata.name}")
            

if __name__=='__main__':
    
    # Load the in-cluster configuration
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    namespace = "debezium-example"

    pod_list = v1.list_namespaced_pod(namespace)

    print_pods_and_containers(pod_list)

    print_all_secrets(pod_list)