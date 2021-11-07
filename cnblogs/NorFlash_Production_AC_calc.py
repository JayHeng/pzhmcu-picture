import sys, os
import argparse

FLASH_3B_ADDR_MAX_SIZE = (8* 1024 * 1024)

##################################################
# IS25WP064A
# s_flashType = 'QSPIFlash'
# s_flashSpeedSlowInHz = (50 * 1000 * 1000)
# s_flashSpeedFastInHz = (133 * 1000 * 1000)
# s_flashDevicePadNum  = 4

# s_flashPageSizeInByte   = 256
# s_flashSectorSizeInByte = (4 * 1024)
# s_flashBlockSizeInByte  = (32 * 1024)
# s_flashTotalSizeInByte  = (8 * 1024 * 1024)

# s_flashPageProgramWaitTimeInUs    = 200
# s_flashSectorEraseWaitTimeInUs    = (70 * 1000)
# s_flash32KBBlockEraseWaitTimeInUs = (100 * 1000)
# s_flash64KBBlockEraseWaitTimeInUs = (150 * 1000)
# s_flashBlockEraseWaitTimeInUs     = s_flash32KBBlockEraseWaitTimeInUs
# s_flashChipEraseWaitTimeInUs      = (16 * 1000 * 1000)

##################################################
# MX25UM51345G
# s_flashType = 'OctalFlash'
# s_flashSpeedSlowInHz = (50 * 1000 * 1000)
# s_flashSpeedFastInHz = (200 * 1000 * 1000)
# s_flashDevicePadNum  = 8

# s_flashPageSizeInByte   = 256
# s_flashSectorSizeInByte = (4 * 1024)
# s_flashBlockSizeInByte  = (64 * 1024)
# s_flashTotalSizeInByte  = (64 * 1024 * 1024)

# s_flashPageProgramWaitTimeInUs    = 150
# s_flashSectorEraseWaitTimeInUs    = (25 * 1000)
# s_flash64KBBlockEraseWaitTimeInUs = (220 * 1000)
# s_flashBlockEraseWaitTimeInUs     = s_flash64KBBlockEraseWaitTimeInUs
# s_flashChipEraseWaitTimeInUs      = (150 * 1000 * 1000)

##################################################
# S25KS512S
s_flashType = 'HyperFlash'
s_flashSpeedSlowInHz = (50 * 1000 * 1000)
s_flashSpeedFastInHz = (166 * 1000 * 1000)
s_flashDevicePadNum  = 8

s_flashPageSizeInByte   = 512
s_flashSectorSizeInByte = (256 * 1024)
s_flashBlockSizeInByte  = s_flashSectorSizeInByte
s_flashTotalSizeInByte  = (64 * 1024 * 1024)

s_flashPageProgramWaitTimeInUs    = 475
s_flashSectorEraseWaitTimeInUs    = (930 * 1000)
s_flashBlockEraseWaitTimeInUs     = s_flashSectorEraseWaitTimeInUs
s_flashChipEraseWaitTimeInUs      = (220 * 1000 * 1000)

class CalcFlashProductionTime(object):
    def __init__(self):
        pass

    def _read_options(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--version", help="CalcFlashProductionTime 0.1")
        return parser.parse_args()

    def _process(self, imageSize):
        blockNum = imageSize / s_flashBlockSizeInByte
        sectorNum = imageSize / s_flashSectorSizeInByte
        pageNum = imageSize / s_flashPageSizeInByte

        programWaitTimeInUs = pageNum * s_flashPageProgramWaitTimeInUs
        eraseWaitTimeInUs = 0
        if (imageSize == s_flashTotalSizeInByte):
            eraseWaitTimeInUs = s_flashChipEraseWaitTimeInUs
        elif (blockNum >= 1):
            eraseWaitTimeInUs = s_flashBlockEraseWaitTimeInUs * blockNum
        elif (sectorNum >= 1):
            eraseWaitTimeInUs = s_flashSectorEraseWaitTimeInUs * sectorNum
        else:
            print ("Error: Unsupported case")
            return -1
        if s_flashType == 'QSPIFlash' or s_flashType == 'OctalFlash':
            addrBytes = 0
            if s_flashTotalSizeInByte > FLASH_3B_ADDR_MAX_SIZE:
                addrBytes = 4
            else:
                addrBytes = 3
            dataTransferTimeSlowInUs = ((8 + addrBytes * 8 + s_flashPageSizeInByte * 8) * pageNum * 1000000 * 1.0) / s_flashSpeedSlowInHz
            if s_flashType == 'QSPIFlash':
                dataTransferTimeFastInUs = (((8 + addrBytes * 8 + s_flashPageSizeInByte * 8) * pageNum * 1000000 * 1.0) / s_flashDevicePadNum) / s_flashSpeedFastInHz
            elif s_flashType == 'OctalFlash':
                dataTransferTimeFastInUs = (((8 + 8 + addrBytes * 8 + s_flashPageSizeInByte * 8) * pageNum * 1000000 * 1.0) / s_flashDevicePadNum) / s_flashSpeedFastInHz
        elif s_flashType == 'HyperFlash':
            dataTransferTimeSlowInUs = ((64 * (256 + 5) * pageNum * 1000000 * 1.0) / (s_flashDevicePadNum * 2)) / s_flashSpeedSlowInHz
            dataTransferTimeFastInUs = ((64 * (256 + 5) * pageNum * 1000000 * 1.0) / (s_flashDevicePadNum * 2)) / s_flashSpeedFastInHz

        print "---------------------------------------------"
        print "Slow Speed SPI mode data transfer time: ", (dataTransferTimeSlowInUs * 1.0 / 1000000), "s"
        print "High Speed QPI/OPI mode data transfer time: ", (dataTransferTimeFastInUs * 1.0 / 1000000), "s"
        print "Total Program wait time: ", (programWaitTimeInUs * 1.0 / 1000000), "s"
        print "Total Erase wait time: ", (eraseWaitTimeInUs * 1.0 / 1000000), "s"
        print "Slow Speed SPI mode total time: ", ((dataTransferTimeSlowInUs + programWaitTimeInUs + eraseWaitTimeInUs) * 1.0 / 1000000), "s"
        print "High Speed QPI/OPI mode total time: ", ((dataTransferTimeFastInUs + programWaitTimeInUs + eraseWaitTimeInUs) * 1.0 / 1000000), "s"
        print "---------------------------------------------"

    def _finalize(self):
        pass

    def run(self):
        # Read command line arguments.
        args = self._read_options()
        self._process(s_flashSectorSizeInByte)
        self._process(s_flashTotalSizeInByte / 2)
        self._process(s_flashTotalSizeInByte)
        self._finalize()

# Create the main class and run it.
if __name__ == "__main__":
    exit(CalcFlashProductionTime().run())
