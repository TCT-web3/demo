import sys
import json

def output_trace(trace_fname, deployment_fname):
    trace_file = open(trace_fname, "r")
    trace = json.load(trace_file)["result"]["structLogs"]
    deploy_info = json.load(open(deployment_fname, "r"))
    output = open("output.txt", "w")
    output.write("======================================Begin==========================================\n")
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

def main():
    # Get file names
    ARGS = sys.argv
    TRACE_FNAME = ARGS[1]

    # Call method
    output_trace(TRACE_FNAME, "deployment_info.json")
    

if __name__ == "__main__":
    main()