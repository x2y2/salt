import commands
def scriptgrains():
    grains = {}
    try:
        gethostname = commands.getstatusoutput('hostname')
    except Exception,e:
        pass
    if gethostname[0] == 0:
        roles = gethostname[1].split('.')[1][:-2]
    grains['roles'] = roles
    return grains
