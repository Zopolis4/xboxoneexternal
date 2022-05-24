import argparse

SECTOR_SIZE = 0x200
XBOX_ONE_NT_DISK_SIGNATURE = bytes.fromhex('12345678')
XBOX_ONE_BOOT_SIGNATURE = bytes.fromhex('99cc')
PC_BOOT_SIGNATURE = bytes.fromhex('55aa')

def update_boot_signature(sector, signature):
    print('NEW Boot Signature: \t0x' + signature.hex())
    return sector[:-2] + signature

def update_nt_disk_signature(sector, signature):
    print('NEW NT Disk Signature: \t0x{0}'+ signature.hex())
    return sector[:0x1b8] + signature + sector[0x1bc:]

def main():
    parser = argparse.ArgumentParser(description='Xbox One External HDD Tool')
    parser.add_argument('-d', '--drive', required=True, help='The target physical drive')
    parser.add_argument('-i', '--ignore', action='store_true',
                        help="Ignore the 'Xbox One NT Disk Signature' sanity check")
    parser.add_argument('-bs', '--bootsignature', action='store_true', help="Update 'Boot Signature'")
    parser.add_argument('-ds', '--disksignature', action='store_true', help="Update 'NT Disk Signature'")
    args = parser.parse_args()

    changes = False

    with open(args.drive, 'r+b') as disk:
        disk.seek(0)
        master_boot_record = disk.read(SECTOR_SIZE)

        nt_disk_signature = master_boot_record[0x1b8:0x1bc]
        boot_signature = master_boot_record[0x1fe:0x200]

        print('NT Disk Signature: \t0x' + nt_disk_signature.hex())
        print('Boot Signature: \t0x' + boot_signature.hex())

        if nt_disk_signature == XBOX_ONE_NT_DISK_SIGNATURE or args.ignore == True:
            if boot_signature == XBOX_ONE_BOOT_SIGNATURE:
                if args.bootsignature:
                    print('Operation: \t\tXbox One->PC')
                    master_boot_record = update_boot_signature(master_boot_record, PC_BOOT_SIGNATURE)
                    changes = True
            elif boot_signature == PC_BOOT_SIGNATURE:
                if args.bootsignature:
                    print('Operation: \t\tPC->Xbox One')
                    master_boot_record = update_boot_signature(master_boot_record, XBOX_ONE_BOOT_SIGNATURE)
                    changes = True
            else:
                print('Error: Unexpected Boot Signature.')

            if args.disksignature:
                master_boot_record = update_nt_disk_signature(master_boot_record, XBOX_ONE_NT_DISK_SIGNATURE)
                changes = True

            if changes:
                print('Writing new MBR ...', end=' ')
                disk.seek(0)
                disk.write(master_boot_record)
                print('done.')
        else:
            print('Error: Unexpected NT Disk Signature.')

if __name__ == "__main__":
    main()