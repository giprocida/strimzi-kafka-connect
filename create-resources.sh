
kubectl apply -f debezium-secret.yaml;
sleep 2;
kubectl apply -f connector-configuration-role.yaml;
sleep 2;
kubectl apply -f connector-configuration-role-binding.yaml;
sleep 2;
kubectl apply -f mysql-deployment.yaml;

