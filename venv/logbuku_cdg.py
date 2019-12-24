import os


def write_log(filename, str):
    print "Starting Log"
    log_file = open(filename, "w")
    log_file.write(str)
    log_file.close()
    print "End"


def main():
    # filename = "session_log/buku_ta/BAB5/F04.txt"
    # filename = "session_log/buku_ta/IND/subscribers/30k_3d_15000subs.txt"
    # filename = "session_log/buku_ta/ANT/subscribers/30k_3d_15000subs.txt"
    # filename = "session_log/buku_ta/FC/dimensi/30k_5d_5000subs.txt"

    # ANT
    cmd = "python virtual_records_final.py 8768,6578,6779 5000 0.3,0.3,0.3 100"
    # IND
    # cmd = "python virtual_records_final.py 9898,7578,9896 15000 0.3,0.3,0.3 10"
    # FC
    # cmd = "python virtual_records_final.py 40,2999,297,108,40 5000 0.2,0.2,0.2,0.2,0.2 10"
    # cmd = "python virtual_records_final.py 40,2999,297,108,40,1500,200 5000 0.14,0.14,0.14,0.14,0.14,0.14,0.14 10"
    # cmd = "python virtual_records_final.py 40,2999,297,108,40,1500,200,220,190,2800 5000 0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1 10"

    print "Calculate"

    result = os.popen(cmd).read()

    write_log(filename, result)


if __name__ == '__main__':
    main()
