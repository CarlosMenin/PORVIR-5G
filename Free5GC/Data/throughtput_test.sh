

kubectl port-forward deployment/free5gc-mongodb :27017 --namespace free5gc

echo "Run throughtput tests"
echo "Run core 1 tests (exec)"
for i in 1 2 4 6 8 10; do
    echo "Running experiment $i"
    # Number of UEs and gnBs
    kubectl scale --replicas=$i statefulsets free5gc-my5grantester --namespace free5gc

    echo "Waiting connections for experiment $i"
    sleep $((1*90))

    echo "Starting experiment $i"
    for j in $(seq 0 $(($i - 1))); do
        IP=$(kubectl exec -i -n free5gc free5gc-my5grantester-$j -c my5grantester -- sh -c "ip -4 addr show uetun1 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'")
        kubectl exec -i -n free5gc free5gc-my5grantester-$j -c my5grantester -- sh -c "iperf -c iperf --bind $IP -p 5001 -t 60 -i 1 -y C" > my5grantester-iperf-1-$i-$j.csv &
    done

    echo "Waiting for experiment $i to finish"
    sleep $((80))

    echo "Clear experiment $i environment"
    kubectl scale --replicas=0 statefulsets free5gc-my5grantester --namespace free5gc

    # Delete tester pods
    for j in $(seq 0 $(($i - 1))); do
        kubectl delete pod free5gc-my5grantester-$j --namespace free5gc &
    done
    sleep 60
done

python3 throughtput_graph.py
