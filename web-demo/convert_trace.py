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
    output = open("trace-" + tx_hash + ".txt", "w") # change output file name
    # output = open("trace_UniswapAddLiquidity2.txt", "w")

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
    output.write(">>call 0x" + contract_hash + "::0x" + function_hash + " (" + contract_name + "::" + function_name + ")\n")
    enter = False
    # Write rest of trace
    for i in range(len(trace)):
        line = ""
        pc = str(trace[i]["pc"])
        opcode = trace[i]["op"]

        # if len(pc) < 4:
        #     pc = "0" * (4-len(pc)) + pc
        line += pc + " "
        line += opcode + " "

        # Get line after PUSH
        if opcode.startswith("PUSH"):
            value = trace[i+1]["stack"][-1]
            line += value + " "
        # Call
        elif opcode == "CALL" or opcode == "STATICCALL":
            stack_idx = -4 if opcode=="CALL" else -3
            # hex
            contract_address = trace[i]["stack"][-2].lstrip("000000000000000000000000")
            offset = int(trace[i]["stack"][stack_idx], 16)
            # print(hex(offset))
            row = offset // 32
            col = (offset % 32)*2
            if col+8 > len(trace[i]["memory"][row]):
                func_selector = trace[i]["memory"][row][col:] + trace[i]["memory"][row+1][:col+8-len(trace[i]["memory"][row])]
            else:
                func_selector = trace[i]["memory"][row][col:col+8]
            print(contract_address, func_selector)
            if not enter and func_selector == function_hash:
                output.close()
                output = open("trace-" + tx_hash + ".txt", "w")
                output.write("======================================Begin==========================================\n")
                line = ">>call 0x" + contract_hash + "::0x" + function_hash + " (" + deploy_info[contract_hash] + "::" + deploy_info[function_hash] + ") "
                enter = True
            else:
                line += "-\n>>" + opcode.lower() + ' 0x' + contract_address
                line += "::0x" + func_selector
                # deployment info
                line += " (" + deploy_info[contract_address] + "::" + deploy_info[func_selector] + ") "
        elif opcode == "RETURN":
            line += "-\n<<return "
        elif opcode == "STOP":
            line += "-\n<<stop "
        output.write(line + "-\n")
    output.write("======================================End==========================================")
    trace_file.close()
    output.close()

def main():
    # Get file names
    # ARGS = sys.argv
    # TRACE_FNAME = ARGS[1]

    # Call method
    # output_trace("trace_addLiquidity.json", "addLiquidity", "deployment_info.json", "theorem_addLiquidity.json")
    # output_trace("trace_removeLiquidity.json", "removeLiquidity", "deployment_info.json", "theorem_removeLiquidity.json")
    # output_trace("trace_swap.json", "addLiquidity", "deployment_info.json", "theorem_swap.json")
    # output_trace("trace_integerOverflow.json", "integerOverflow", "deployment_info.json", "theorem_integerOverflow.json")
    # output_trace("trace_noReentrancy.json", "noReentrancy", "deployment_info.json", "theorem_noReentrancy.json")
    output_trace("trace_reentrancy.json", "reentrancy", "deployment_info.json", "theorem_reentrancy.json")
    

if __name__ == "__main__":
    main()