import lorun
import os

RESULT_STR = [
    '测试通过',
    'Presentation Error',
    '运行超时',
    '内存占用过多',
    '答案错误',
    '运行错误',
    '输出过多',
    '编译错误',
    '系统错误'
]


def runone(p_path, in_path, out_path, time, memory):
    fin = open(in_path)
    ftemp = open('temp.out', 'w')
    runcfg = {
        'args': ['python3', p_path],
        'fd_in': fin.fileno(),
        'fd_out': ftemp.fileno(),
        'timelimit': time,  # in MS
        'memorylimit': memory,  # in KB
    }
    rst = lorun.run(runcfg)
    fin.close()
    ftemp.close()
    
    if rst['result'] == 0:
        ftemp = open('temp.out')
        fout = open(out_path)
        crst = lorun.check(fout.fileno(), ftemp.fileno())
        fout.close()
        ftemp.close()
        os.remove('temp.out')
        if crst != 0:
            return {'result': crst}
    return rst


def judge(src_path, td_path, td_total, time, memory):
    a = []
    for i in range(td_total):
        in_path = os.path.join(td_path, '%d.in' % i)
        out_path = os.path.join(td_path, '%d.out' % i)
        if os.path.isfile(in_path) and os.path.isfile(out_path):
            rst = runone(src_path, in_path, out_path, time, memory)
            rst['result'] = RESULT_STR[rst['result']]
            a.append(rst)
        else:
            a.append('testdata:%d incompleted' % i)
            print(a)
            exit(-1)
    return(a)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 4:
        print('Usage:%s srcfile testdata_pth testdata_total')
        exit(-1)
    judge(sys.argv[1], sys.argv[2], int(sys.argv[3]))
