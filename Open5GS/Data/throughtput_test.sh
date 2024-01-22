echo "Run throughtput tests"
for e in $(seq 1 16); do
    for c in 1 1; do
        echo "Run core $c tests (exec $e)"
        for i in 1 2 4 6 8 10; do
            echo "Running experiment $i"
            # Number of UEs and gnBs
            kubectl scale --replicas=$i statefulsets open5gs-my5grantester --namespace cemenin

            echo "Waiting connections for experiment $i"
            sleep $((1*60))

            echo "Starting experiment $i"
            for j in $(seq 0 $(($i - 1))); do
                IP=$(kubectl exec -i -n cemenin open5gs-my5grantester-$j -c my5grantester -- sh -c "ip -4 addr show uetun1 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'")
                kubectl exec -i -n cemenin open5gs-my5grantester-$j -c my5grantester -- sh -c "iperf -c open5gs-iperf --bind $IP -t 60 -i 1 -y C" > my5grantester-iperf-$e-$c-$i-$j.csv &
            done

            echo "Waiting for experiment $i to finish"
            sleep $((80))

            echo "Clear experiment $i environment"
            kubectl scale --replicas=0 statefulsets open5gs-my5grantester --namespace cemenin

            # Delete tester pods
            for j in $(seq 0 $(($i - 1))); do
                kubectl delete pod open5gs-my5grantester-$j --namespace cemenin &
            done
            sleep 40
        done
    done
done

