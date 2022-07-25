import argparse

SECTOR_SIZE = 0x200
XBOX_ONE_NT_DISK_SIGNATURE = bytes.fromhex('12345678')
XBOX_ONE_BOOT_SIGNATURE = bytes.fromhex('99cc')
PC_BOOT_SIGNATURE = bytes.fromhex('55aa')

def main():
    parser = argparse.ArgumentParser(description='Xbox One/Series External Drive Converter')
    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('drive', help='The target physical drive')
    group.add_argument('--toxbox', action='store_true',
                        help="Convert the drive from Xbox to PC")
    group.add_argument('--topc', action='store_true',
                        help="Convert the drive from PC to Xbox")
    args = parser.parse_args()

    with open(args.drive, 'r+b') as disk:
        disk.seek(0)
        master_boot_record = disk.read(SECTOR_SIZE)
        mbr_backup = disk.read(SECTOR_SIZE)

        nt_disk_signature = master_boot_record[0x1b8:0x1bc]
        boot_signature = master_boot_record[0x1fe:0x200]

        print('NT Disk Signature: \t0x' + nt_disk_signature.hex())
        print('Boot Signature: \t0x' + boot_signature.hex())

        if args.toxbox == True:
            XboxToPC(args.drive)
        elif args.topc == True:
            PCToXbox(args.drive)

        print('Writing new MBR ...')
        disk.write(master_boot_record)

        if master_boot_record == disk.read(SECTOR_SIZE):
            print('Success')
        else:
            print('Writing new MBR failed, attempting to revert')
            disk.seek(0)
            disk.write(mbr_backup)

def XboxToPC(drive):
   with open(drive, 'r+b') as disk:
       disk.seek(0)
       master_boot_record = disk.read(SECTOR_SIZE)
       nt_disk_signature = master_boot_record[0x1b8:0x1bc]
       boot_signature = master_boot_record[0x1fe:0x200]
       if boot_signature == XBOX_ONE_BOOT_SIGNATURE:
           print('Operation: Xbox One -> PC')
           master_boot_record = (master_boot_record[:0x1b8] + PC_BOOT_SIGNATURE + master_boot_record[0x1bc:])

def PCToXbox(drive):
   with open(args.drive, 'r+b') as disk:
       disk.seek(0)
       master_boot_record = disk.read(SECTOR_SIZE)
       nt_disk_signature = master_boot_record[0x1b8:0x1bc]
       boot_signature = master_boot_record[0x1fe:0x200]
       if boot_signature == PC_BOOT_SIGNATURE:
           print('Operation: PC -> Xbox One')
           master_boot_record = (master_boot_record[:0x1b8] + XBOX_ONE_BOOT_SIGNATURE + master_boot_record[0x1bc:])


if __name__ == "__main__":
    main()
