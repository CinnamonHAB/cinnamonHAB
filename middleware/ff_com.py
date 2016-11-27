import subprocess

# returns the output of the Metric-FF planner
# arguments
#    pddl_path - the path where the pddl files can be found
#    domain - the name of the domain file
#    problem - the name of the problem file
#    search_config - the search configuration used. default is 4
# return value: string containing the output of the planner
def get_plan(pddl_path, domain, problem, search_config=4):
    command = "/home/oskar/Metric-FF-v2.0/ff -p " + pddl_path + " -o " + domain + " -f " + problem + " -s " + str(search_config)
    try:
        out = subprocess.check_output(command, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError, e:
        out = e.output

    return out
