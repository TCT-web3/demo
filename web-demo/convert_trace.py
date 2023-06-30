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
    hashes = re.search(r"0x([^:]+)::0x([^:]+)", theorem["entry-for-real"])
    contract_hash = hashes.group(1)
    function_hash = hashes.group(2)
    names = re.search(r"([^:]+)::([^:]+)", theorem["entry-for-test"])
    contract_name = names.group(1)
    function_name = names.group(2)

    deploy_info[contract_hash] = contract_name
    deploy_info[function_hash] = function_name

    with open(deployment_fname, "w") as deploy_info_file:
        deploy_info_file.write(json.dumps(deploy_info))

    # Write header
    output.write("======================================Begin==========================================\n")
    output.write(">>enter 0x" + contract_hash + "::0x" + function_hash + " (" + contract_name + "::" + function_name + ")\n")
    enter = False
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
            contract_address = trace[i]["stack"][-2].lstrip("000000000000000000000000")
            offset = int(trace[i]["stack"][-4], 16)
            row = offset // 32
            col = (offset % 32)*2
            func_selector = trace[i]["memory"][row][col:col+8]

            if not enter and func_selector == function_hash:
                output.close()
                output = open("trace-" + tx_hash + ".txt", "w")
                output.write("======================================Begin==========================================\n")
                line = ">>enter 0x" + contract_hash + "::0x" + function_hash + " (" + deploy_info[contract_hash] + "::" + deploy_info[function_hash] + ") "
                enter = True

            else:
                line += "-\n>>enter " + '0x' + contract_address
                line += "::0x" + func_selector
                # deployment info
                line += " (" + deploy_info[contract_address] + "::" + deploy_info[func_selector] + ") "
        elif opcode == "RETURN":
            line += "-\n<<leave "
        elif opcode == "STOP":
            line += "-\n<<leave "
        output.write(line + "-\n")
    output.write("======================================End==========================================")
    trace_file.close()
    output.close()

def main():
    # Get file names
    ARGS = sys.argv
    TRACE_FNAME = ARGS[1]

    # Call method
    output_trace(TRACE_FNAME, "0xdc796b5fd6d87794379e0014ad3dfe406696a6deda3c6fe45844225589a75722", "deployment_info.json", "theorem-0xdc796b5fd6d87794379e0014ad3dfe406696a6deda3c6fe45844225589a75722.json")
    

if __name__ == "__main__":
    main()