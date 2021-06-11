
# Python ecosystem ...
PY3="python3"
PY_PATH=PYTHONPATH=\"../:../bundles/icmp_0/:../bundles/tlshs/\"

TCPD="tcpdump"


function launch_gen_test()
{
    now="$(date +%s)"
    outdir="./test_gen_captures"
    pkt_cnt="240"
    cpt_if="ovs-p1"

    sudo ${TCPD} -c ${pkt_cnt} -i ${cpt_if} \
                 -w ${outdir}/${now}_test_gen.pcap \
                 "icmp" &
    eval sudo ${PY_PATH} ${PY3} test_gen.py &

    for job in `jobs -p`
    do
        echo ${job}
        wait ${job}
    done
}


function launch_test_cases()
{
    eval sudo ${PY_PATH} ${PY3} run_test_cases.py
}


function main()
{
    printf "Test launch script says: Hello, World!\n"
    # launch_gen_test
    launch_test_cases
}


main

