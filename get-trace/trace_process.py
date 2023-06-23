import json
import argparse


def parse_argument():
    parser = argparse.ArgumentParser(description='Argument for trace_process.py')
    parser.add_argument('--trace_file', help='trace file (also input file) should be json', required=True)
    parser.add_argument('--output', help='output file', required=True)
    args = parser.parse_args()
    return args

def trace_process(args):
    res = json.load(open(args.trace_file))
    exe_trace = res["result"]["structLogs"]
    # write file
    wf = open(args.output, "w")

    for idx, item in enumerate(exe_trace):
        opcode = str(item["op"])
        if "push" in opcode.lower():
            # extract the top of stack in the next step
            stack = exe_trace[idx+1]["stack"]
            oprand = stack[-1]
            # print(f"{opcode} {oprand}")
            wf.write(f"{opcode} {oprand}\n")
        else:
            # print(f"{opcode}")
            wf.write(f"{opcode}\n")
    

if __name__ == '__main__':
    args = parse_argument()
    trace_process(args)
