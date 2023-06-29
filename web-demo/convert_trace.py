import sys
import json
import re

def output_trace(trace_fname, tx_hash, deployment_fname, theorem_fname):
    # Open files
    trace_file = open(trace_fname, "r")
    trace = json.load(trace_file)["result"]["structLogs"]
    theorem_file = open("uploads/" + theorem_fname, "r")
    theorem = json.load(theorem_file)
    with open(deployment_fname, "r") as deploy_info_file:
        deploy_info = json.load(deploy_info_file)
    output = open("trace-" + tx_hash + ".txt", "w")

    # Map entry point to deployment file
    hashes = re.search(r"([^:]+)::([^:]+)", theorem["entry-for-real"])
    contract_hash = hashes.group(1)
    function_hash = hashes.group(2)
    print(contract_hash, function_hash)
    names = re.search(r"([^:]+)::([^:]+)", theorem["entry-for-test"])
    contract_name = names.group(1)
    function_name = names.group(2)
    print(contract_name, function_name)

    deploy_info[contract_hash] = contract_name
    deploy_info[function_hash] = function_name

    with open(deployment_fname, "w") as deploy_info_file:
        deploy_info_file.write(json.dumps(deploy_info))

    # Write header
    output.write("======================================Begin==========================================\n")
    output.write(">>enter " + contract_hash + "::" + function_hash + " (" + contract_name + "::" + function_name + ")\n")
    # Write rest of trace
    for i in range(len(trace)):
        line = ""
        pc = str(trace[i]["pc"])
        opcode = trace[i]["op"]

        if len(pc) < 4:
            pc = "0" * (4-len(pc)) + pc
        line += pc + " "
        line += opcode + " "

        # Get line after PUSH
        if opcode.startswith("PUSH"):
            value = trace[i+1]["stack"][-1]
            line += value + " "
        # Call
        elif opcode == "CALL":
            # hex
            contract_address = trace[i]["stack"][-2]
            line += "-\n>>enter " + '0x' + contract_address
            offset = int(trace[i]["stack"][-4], 16)
            row = offset // 32
            col = (offset % 32)*2
            func_selector = trace[i]["memory"][row][col:col+8]
            line += "::0x" + func_selector
            # deployment info
            line += "(" + deploy_info[contract_address] + "::" + deploy_info[func_selector] + ") "
        elif opcode == "RETURN":
            line += "-\n<<leave "
        elif opcode == "STOP":
            line += "-\n<<leave "
        output.write(line + "-\n")
    output.write("======================================End==========================================")
    trace_file.close()
    output.close()